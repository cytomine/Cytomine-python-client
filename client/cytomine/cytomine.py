# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2015. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from time import strftime, gmtime

import os
import requests
import shutil
from cachecontrol import CacheControlAdapter
from requests_toolbelt import MultipartEncoder

from .utils import CytomineAuth, deprecated

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"


class Cytomine(object):
    __instance = None

    def __init__(self, host, public_key, private_key, verbose=0, use_cache=True, protocol="http",
                 working_path="/tmp", **kwargs):
        """
        Initialize the Cytomine Python client which is a singleton.

        Parameters
        ----------
        host : str
            The Cytomine host (without protocol).
        public_key : str
            The Cytomine public key.
        private_key : str
            The Cytomine private key.
        verbose : int
            The verbosity level of the client.
        use_cache : bool
            True to use HTTP cache, False otherwise.
        protocol : str ("http", "https")
            The protocol.
        working_path : str
            Deprecated.
        kwargs : dict
            Deprecated arguments.
        """
        self._host = host.replace("http://", "").replace("https://", "")
        self._public_key = public_key
        self._private_key = private_key
        self._verbose = verbose
        self._use_cache = use_cache
        self._protocol = protocol.replace("://", "")
        self._base_path = "/api/"
        self._logger = None  # TODO

        # Deprecated
        self._working_path = working_path

        self._session = requests.session()
        if self._use_cache:
            self._session.mount('{}://'.format(self._protocol), CacheControlAdapter())

        Cytomine.__instance = self

    @classmethod
    def connect(cls, host, public_key, private_key, verbose=0, use_cache=True):
        """
        Connect the client with the given host and the provided credentials.

        Parameters
        ----------
        host : str
            The Cytomine host (without protocol).
        public_key : str
            The Cytomine public key.
        private_key : str
            The Cytomine private key.
        verbose : int
            The verbosity level of the client.
        use_cache : bool
            True to use HTTP cache, False otherwise.

        Returns
        -------
        client : Cytomine
            A connected Cytomine client.
        """
        return cls(host, public_key, private_key, verbose, use_cache)

    @staticmethod
    def get_instance():
        return Cytomine.__instance

    @property
    def host(self):
        return self._host

    def set_credentials(self, public_key, private_key):
        self._public_key = public_key
        self._private_key = private_key

    def _base_url(self):
        return "{}://{}{}".format(self._protocol, self._host, self._base_path)

    @staticmethod
    def _headers(accept="application/json, */*", content_type=None):
        headers = dict()

        if accept is not None:
            headers['accept'] = accept

        if content_type is not None:
            headers['content-type'] = content_type

        headers['date'] = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime())
        headers['X-Requested-With'] = 'XMLHTTPRequest'

        return headers

    def get(self, model, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()
        response = self._session.get("{}{}".format(self._base_url(), uri),
                                     auth=CytomineAuth(
                                         self._public_key, self._private_key,
                                         self._base_url(), self._base_path),
                                     headers=self._headers(),
                                     params=query_parameters)

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return model.populate(response.json())

    def put(self, model, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()
        response = self._session.put("{}{}".format(self._base_url(), uri),
                                     auth=CytomineAuth(
                                         self._public_key, self._private_key,
                                         self._base_url(), self._base_path),
                                     headers=self._headers(content_type='application/json'),
                                     params=query_parameters,
                                     data=model.to_json())

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return model.populate(response.json()[model.callback_identifier])

    def delete(self, model, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()
        response = self._session.delete("{}{}".format(self._base_url(), uri),
                                        auth=CytomineAuth(
                                            self._public_key, self._private_key,
                                            self._base_url(), self._base_path),
                                        headers=self._headers(content_type='application/json'),
                                        params=query_parameters)

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return True

    def post(self, model, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()
        response = self._session.post("{}{}".format(self._base_url(), uri),
                                      auth=CytomineAuth(
                                          self._public_key, self._private_key,
                                          self._base_url(), self._base_path),
                                      headers=self._headers(content_type='application/json'),
                                      params=query_parameters,
                                      data=model.to_json())

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return model.populate(response.json()[model.callback_identifier])

    def upload_file(self, model, filename, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()
        m = MultipartEncoder(fields={"files[]": (filename, open(filename, 'rb'))})
        response = self._session.post("{}{}".format(self._base_url(), uri),
                                      auth=CytomineAuth(
                                          self._public_key, self._private_key,
                                          self._base_url(), self._base_path),
                                      headers=self._headers(content_type=m.content_type),
                                      params=query_parameters,
                                      data=m)

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return model.populate(response.json()[model.callback_identifier])

    def download_file(self, url, destination, override=False, payload=None):
        if override:
            response = self._session.get(url,
                                         auth=CytomineAuth(
                                             self._public_key, self._private_key,
                                             self._base_url(), self._base_path),
                                         headers=self._headers(content_type='application/json'),
                                         params=payload,
                                         stream=True)

            if not response.status_code == requests.codes.ok:
                self._logger.warning(response.reason)
                return False

            with open(destination, "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            return True
        else:
            return True

    def upload_image(self, upload_host, filename, id_storage, id_project=None, properties=None, sync=False):
        from .models.storage import UploadedFile

        query_parameters = {
            "idStorage": id_storage,
            "cytomine": "{}://{}".format(self._protocol, self._host),
            "sync": sync
        }

        if id_project:
            query_parameters["idProject"] = id_project

        if properties:
            query_parameters["keys"] = ','.join(list(properties.keys()))
            query_parameters["values"] = ','.join(list(properties.values()))

        upload_host = upload_host.replace("http://", "").replace("https://", "").replace("/", "")

        m = MultipartEncoder(fields={"files[]": (filename, open(filename, 'rb'))})
        response = self._session.post("http://{}/upload".format(upload_host),
                                      auth=CytomineAuth(
                                          self._public_key, self._private_key,
                                          "http://{}".format(upload_host), ""),
                                      headers=self._headers(content_type=m.content_type),
                                      params=query_parameters,
                                      data=m)

        if not response.status_code == requests.codes.ok:
            self._logger.warning(response.reason)
            return False

        return UploadedFile().populate(json.loads(response.json()[0]["uploadFile"]))

    # Project
    @deprecated
    def add_project(self, project_name, id_ontology):
        from .models.project import Project
        return Project(project_name, id_ontology).save()

    @deprecated
    def edit_project(self, id_project, project_name, id_ontology):
        from .models.project import Project
        project = Project().fetch(id_project)
        project.name = project_name
        project.ontology = id_ontology
        return project.update()

    @deprecated
    def delete_project(self, id_project):
        from .models.project import Project
        return Project().delete(id_project)

    @deprecated
    def get_project(self, id_project):
        from .models.project import Project
        return Project().fetch(id_project)

    @deprecated
    def get_projects(self):
        from .models.project import ProjectCollection
        return ProjectCollection().fetch()

    # Ontology
    @deprecated
    def add_ontology(self, name):
        from .models.ontology import Ontology
        return Ontology(name).save()

    @deprecated
    def delete_ontology(self, id_ontology):
        from .models.ontology import Ontology
        return Ontology().delete(id_ontology)

    @deprecated
    def get_ontology(self, id_ontology):
        from .models.ontology import Ontology
        return Ontology().fetch(id_ontology)

    # Term
    @deprecated
    def add_term(self, name, id_ontology, color="#ff0000"):
        from .models.ontology import Term
        return Term(name, id_ontology, color).save()

    @deprecated
    def delete_term(self, id_term):
        from .models.ontology import Term
        return Term().delete(id_term)

    @deprecated
    def get_term(self, id_term):
        from .models.ontology import Term
        return Term().fetch(id_term)

    @deprecated
    def get_terms(self, id_ontology=None):
        from .models.ontology import TermCollection
        terms = TermCollection()
        if id_ontology:
            terms.filters["ontology"] = id_ontology
        return terms.fetch()

    @deprecated
    def add_relation_term(self, id_parent, id_child):
        from .models.ontology import RelationTerm
        return RelationTerm(id_parent, id_child).save()

    # uploadedfile
    @deprecated
    def get_uploaded_file(self, id_uploaded_file):
        from .models.storage import UploadedFile
        return UploadedFile().fetch(id_uploaded_file)

    # storage
    @deprecated
    def get_storage(self, id_storage):
        from .models.storage import Storage
        return Storage().fetch(id_storage)

    # annotations
    @deprecated
    def get_annotation(self, id_annotation=None):
        from .models.annotation import Annotation, AnnotationCollection
        if id_annotation:
            return Annotation().fetch(id_annotation)
        else:
            return AnnotationCollection().fetch()

    @deprecated
    def get_annotations(self, id_project=None, id_user=None, id_image=None, id_term=None, showGIS=None,
                        showWKT=None, showMeta=None, bbox=None, id_bbox=None, reviewed_only=False):
        from .models.annotation import AnnotationCollection
        return AnnotationCollection(project=id_project, user=id_user, image=id_image, term=id_term,
                                    showMeta=showMeta, bbox=bbox, bboxAnnotation=id_bbox, reviewed=reviewed_only,
                                    showTerm=(showMeta or showGIS or showWKT)).fetch()

    @deprecated
    def add_annotation(self, location, id_image, minPoint=None, maxPoint=None):
        from .models.annotation import Annotation
        annotation = Annotation(location, id_image)
        annotation.query_parameters["minPoint"] = minPoint
        annotation.query_parameters["maxPoint"] = maxPoint
        annotation.save()

    @deprecated
    def add_annotations(self, locations, id_image):
        return self.add_annotations_with_term(locations, id_image, None)

    @deprecated
    def add_annotations_with_term(self, locations, id_image, id_term):
        from .models.image import ImageInstance
        from .models.annotation import Annotation
        image = ImageInstance.fetch(id_image)
        id_term = [id_term] if id_term else None
        return [Annotation(location, id_image, id_term, image.project).save() for location in locations]

    @deprecated
    def delete_annotation(self, id_annotation):
        from .models.annotation import Annotation
        return Annotation().delete(id_annotation)

    @deprecated
    def dump_annotations(self, annotations, get_image_url_func=None, dest_path="/tmp", override=False,
                         excluded_terms=None, desired_zoom=None, desired_max_size=None, tile_size=None,
                         translate=None):
        from .models.annotation import Annotation

        if not excluded_terms:
            excluded_terms = []

        mask = False
        alpha = False
        if get_image_url_func == Annotation.get_annotation_alpha_crop_url:
            mask = True
            alpha = True
        elif get_image_url_func == Annotation.get_annotation_mask_url:
            mask = True
            alpha = False
        else:
            NotImplementedError("Crop tiled translated not implemented")
            # # extend the area to use a fixed-size tile (assuming the tile is larger than the annotation bounding box)
            # # print "Fixed tile cropURL"
            # p_annotation = self.get_annotation(annot.id)
            # p = loads(p_annotation.location)
            # minx, miny, maxx, maxy = int(p.bounds[0]), int(p.bounds[1]), int(p.bounds[2]), int(p.bounds[3])
            # image = self.get_image_instance(p_annotation.image)
            # for t in range(0, translate):
            #     original_cropURL = get_image_url_func(annot, desired_zoom, desired_max_size)
            #     # print "original cropURL = %s" % original_cropURL
            #     cropURL = self.__protocol + self.__host + self.__base_path
            # + Annotation.get_annotation_crop_tiled_translated(
            #         annot, minx, maxx, miny, maxy, p_annotation.image, image.height, tile_size, translate)
            #     # print "tiled cropURL: %s" % cropURL
            #     filename = "%s/%d_%d_%d_translated_%d.png" % (termPath, annot.image, annot.id, tile_size, t)
            #     # queue.put((cropURL, filename, annot))

        dest_pattern = os.path.join(dest_path, "{term}", "{image}_{id}.png")
        for annotation in annotations:
            for term in annotation.term:
                if term in excluded_terms:
                    continue
                annotation.dump(dest_pattern, override, mask, alpha, bits=8, zoom=desired_zoom,
                                max_size=desired_max_size)

        return annotations

    # annotation_term
    @deprecated
    def add_annotation_term(self, id_annotation, term, expected_term, rate, annotation_term_model=None):
        from .models.annotation import AnnotationTerm, AlgoAnnotationTerm
        if annotation_term_model == AlgoAnnotationTerm:
            return AlgoAnnotationTerm(id_annotation, term, expected_term, rate).save()
        else:
            return AnnotationTerm(id_annotation, term).save()

    @deprecated
    def add_user_annotation_term(self, id_annotation, term):
        return self.add_annotation_term(id_annotation, term, None, None)

    # abstract image
    @deprecated
    def get_image(self, id_image):
        from .models.image import AbstractImage
        return AbstractImage().fetch(id_image)

    @deprecated
    def edit_image(self, id_image, filename=None, path=None, mime=None, id_sample=None, id_scanner=None,
                   magnification=None, resolution=None):
        from .models.image import AbstractImage
        image = AbstractImage()
        image = image.fetch(id_image)
        image.filename = filename if filename else image.filename
        image.path = path if path else image.path
        image.mime = mime if mime else image.mime
        image.scanner = id_scanner if id_scanner else image.scanner
        image.sample = id_sample if id_sample else image.sample
        image.magnification = magnification if magnification else image.magnification
        image.resolution = resolution if resolution else image.resolution
        image.update()

    @deprecated
    def delete_image(self, id_image):
        from .models.image import AbstractImage
        return AbstractImage().delete(id_image)

    # image_instance
    @deprecated
    def add_image_instance(self, id_base_image, id_project):
        from .models.image import ImageInstance
        return ImageInstance(id_base_image, id_project).save()

    @deprecated
    def delete_image_instance(self, id_image_instance):
        from .models.image import ImageInstance
        return ImageInstance().delete(id_image_instance)

    @deprecated
    def get_image_instance(self, id_image_instance, include_server_urls=False):
        from .models.image import ImageInstance

        if include_server_urls:
            return ImageInstance().fetch_with_image_servers(id_image_instance)
        else:
            return ImageInstance().fetch(id_image_instance)

    @deprecated
    def get_project_image_instances(self, id_project):
        from .models.image import ImageInstanceCollection
        return ImageInstanceCollection(filters={"project": id_project}).fetch()

    @deprecated
    def dump_project_images(self, id_project=None, dest_path="imageinstances/", override=False,
                            image_instances=None, max_size=None):
        from .models.image import ImageInstanceCollection

        dest_pattern = os.path.join(self._working_path, dest_path, "{project}", "{id}.jpg")

        if not image_instances:
            image_instances = ImageInstanceCollection({"project": id_project}).fetch()
        for image_instance in image_instances:
            image_instance.dump(dest_pattern, override, max_size=max_size)

        return image_instances

    # software
    @deprecated
    def get_software(self, id_software):
        from .models.software import Software
        return Software().fetch(id_software)

    @deprecated
    def add_software(self, name, service_name, result_name, execute_command=None):
        from .models.software import Software
        return Software(name, service_name, result_name, execute_command).save()

    # software project
    @deprecated
    def add_software_project(self, project, software):
        from .models.software import SoftwareProject
        return SoftwareProject(software, project).save()

    # software_parameters
    @deprecated
    def add_software_parameter(self, name, id_software, type, default_value, required, index, set_by_server,
                               uri=None, uriPrintAttribut=None, uriSortAttribut=None):
        from .models.software import SoftwareParameter
        return SoftwareParameter(name, type, id_software, default_value, required, index, set_by_server, uri,
                                 uriSortAttribut, uriPrintAttribut).save()

    @deprecated
    def get_software_parameter(self, id_software_parameter):
        from .models.software import SoftwareParameter
        return SoftwareParameter().fetch(id_software_parameter)

    @deprecated
    def delete_software_parameter(self, id_software_parameter):
        from .models.software import SoftwareParameter
        return SoftwareParameter().delete(id_software_parameter)

    # Job
    @deprecated
    def get_job(self, id_job):
        from .models.software import Job
        return Job().fetch(id_job)

    @deprecated
    def update_job_status(self, job, status=None, status_comment=None, progress=None):
        job.status = status if status else job.status
        job.statusComment = status_comment if status_comment else job.statusComment
        job.progress = progress if progress else job.progress
        job.update()

    # Job Parameter
    @deprecated
    def add_job_parameter(self, id_job, id_software_parameter, value):
        from .models.software import JobParameter
        return JobParameter(id_job, id_software_parameter, value).save()

    # def add_job_parameters(self, job, software, values):
    #     job_parameters_values = {}
    #     cytomine_job = self.get_job(job)
    #     for software_parameter in software.parameters:
    #         software_parameter_name = software_parameter["name"]
    #         if values[software_parameter["name"]]:
    #             job_parameters_values[software_parameter["id"]] = software_parameter_name, values[
    #                 software_parameter_name]
    #         elif (cytomine_job.algoType == "jobtemplate" and software_parameter_name == "annotation"):
    #             print
    #             "Do not add annotation param if JobTemplate"
    #         else:
    #             job_parameters_values[software_parameter["id"]] = software_parameter_name, software_parameter[
    #                 "defaultParamValue"]
    #
    #     for software_parameter_id in job_parameters_values:
    #         name, value = job_parameters_values[software_parameter_id]
    #         self.add_job_parameter(job, software_parameter_id, value)
    #     return job_parameters_values


    # JobTemplate
    @deprecated
    def get_job_template(self, id_job_template):
        from .models.software import JobTemplate
        return JobTemplate.fetch(id_job_template)

    @deprecated
    def add_job_template(self, name, id_project, id_software):
        from .models.software import JobTemplate
        return JobTemplate(name, id_software, id_project).save()

    @deprecated
    def delete_job_template(self, id_job_template):
        from .models.software import JobTemplate
        return JobTemplate().delete(id_job_template)

    # JobData
    @deprecated
    def add_job_data(self, job, key, filename):
        from .models.software import JobData
        job_data = JobData(id_job=job, key=key, filename=filename).save()
        job_data.upload(filename)
        return job_data

    @deprecated
    def get_job_data_file(self, id_job_data, dest_path):
        from .models.software import JobData
        return JobData().fetch(id_job_data).download(dest_path)








    #
    # def get_reviewed_annotations(self, id_project=None):
    #     annotations = ReviewedAnnotationCollection()
    #     if id_project:
    #         annotations.project = id_project
    #     annotations = self.fetch(annotations)
    #     return annotations


"""
    # User
    def get_user(self, id_user=None):
        if id_user:
            user = User()
            user.id = id_user
            return self.fetch(user)
        else:
            user = UserCollection()
            return self.fetch(user)

    def get_current_user(self):
        user = User()
        user.current = True
        return self.fetch(user)

    def add_user(self, username, firstname, lastname, email, password):
        user = User()
        user.username = username
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.password = password
        return self.save(user)

    # tmp service, should be done by add job service
    def add_user_job(self, software, project):
        user = User()
        user.software = software
        user.project = project
        return self.save(user)

    def edit_user(self, id_user, username, firstname, lastname, email, password):
        user = self.get_user(id_user)
        user.username = username
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.password = password
        return self.update(user)

    def delete_user(self, id_user):
        user = self.get_user(id_user)
        return self.delete(user)

    # Role
    def get_role(self, id):
        role = Role()
        role.id = id
        return self.fetch(role)

    def get_roles(self, filter_by_authority=None):
        # filter_by_authority : ROLE_USER or ROLE_ADMIN
        roles = RoleCollection()
        roles = self.fetch(roles)
        if filter_by_authority:
            roles = [i for i in roles.data() if i.authority == filter_by_authority]
            roles = roles.pop()
        return roles

    # UserRole
    def add_user_role(self, id_user, id_role):
        role = UserRole()
        role.user = id_user
        role.role = id_role
        return self.save(role)

    def delete_user_role(self, id_user, id_role):
        role = self.get_user_role(id_user, id_role)
        if role:
            return self.delete(role)
        else:
            return False

    def get_user_role(self, id_user=None, id_role=None):
        user_role = UserRole()
        user_role.role = id_role
        user_role.user = id_user
        user_role.id = id_role * id_user  # fake_id
        return self.fetch(user_role)

    # group
    def add_group(self, name):
        group = Group()
        group.name = name
        return self.save(group)

    def get_group(self, id_group=None):
        group = Group()
        if id_group:
            group.id = id_group
        return self.fetch(group)

    def edit_group(self, id_group, name):
        group = self.get_group(id_group)
        group.name = name
        return self.update(group)

    def delete_group(self, id_group):
        group = self.get_group(id_group)
        return self.delete(group)

    

    # imagegroup
    def get_image_group(self, id_image_group=None):
        image_group = ImageGroup()
        if id_image_group:
            image_group.id = id_image_group
        return self.fetch(image_group)

    def delete_image_group(self, id_image_group):
        imagegrp = self.get_image_group(id_image_group)
        return self.delete(imagegrp)

    # userGroup
    def add_user_group(self, id_user, id_group):
        userGroup = UserGroup()
        userGroup.user = id_user
        userGroup.group = id_group
        return self.save(userGroup)

    # userGroup
    def get_user_group(self, id_user, id_group):
        if not id_group:
            userGroup = RoleCollection()
            if id_user:
                userGroup.user = id_user
            return self.fetch(userGroup)
        else:
            userGroup = UserGroup()
            userGroup.group = id_group
            if id_user:
                userGroup.user = id_user
                userGroup.id = id_user * id_group
            return self.fetch(userGroup)

    # userGroup
    def delete_user_group(self, id_user, id_group):
        userGroup = self.get_user_group(id_user, id_group)
        return self.delete(userGroup)

    # get positions (as a single request or with multiple requests (paging)
    def get_positions(self, id_image=None, id_user=None, showDetails=None, afterthan=None, beforethan=None,
                      maxperpage=None):
        positions = PositionCollection()
        positions.imageinstance = id_image
        query = ""
        if id_user:
            query += "user=" + str(id_user)
        if showDetails:
            query += "&showDetails=true"
        if afterthan:
            query += "&afterThan=" + str(afterthan)
        if beforethan:
            query += "&beforeThan=" + str(beforethan)
        # use paginator for large collections
        if maxperpage:
            positions_tmp = PositionCollection()
            positions_tmp.init_paginator(maxperpage, 0)
            while True:
                positions_tmp.imageinstance = id_image
                positions_tmp = self.fetch(positions_tmp, query=query)
                if not positions:
                    positions = positions_tmp
                else:
                    positions.data().extend(positions_tmp.data())
                if not (positions_tmp.next_page()):
                    break
        else:
            positions = self.fetch(positions, query=query)
        return positions





    # property
    def get_annotation_property(self, annotation_id, annotation_property_id):
        annotation_property = AnnotationProperty()
        annotation_property.domainIdent = annotation_id
        annotation_property.id = annotation_property_id
        return self.fetch(annotation_property)

    def add_annotation_property(self, annotation_id, key, value):
        annotation_property = AnnotationProperty()
        annotation_property.domainIdent = annotation_id
        annotation_property.key = key
        annotation_property.value = value
        return self.save(annotation_property)

    def edit_annotation_property(self, annotation_id, annotation_property_id, key, value):
        annotation_property = self.get_annotation_property(annotation_id, annotation_property_id)
        if annotation_property:
            annotation_property.key = key
            annotation_property.value = value
            return self.update(annotation_property)
        else:
            return None

    def delete_annotation_property(self, annotation_id, annotation_property_id):
        annotation_property = self.get_annotation_property(annotation_id, annotation_property_id)
        if annotation_property:
            return self.delete(annotation_property)
        else:
            return None

    def get_annotation_properties(self, annotation_id):
        annotation_properties = AnnotationPropertyCollection()
        annotation_properties.annotation_id = annotation_id
        return self.fetch(annotation_properties)

    def get_abstract_image_properties(self, abstract_image_id):
        abstract_image_properties = AbstractImagePropertyCollection()
        abstract_image_properties.abstract_image_id = abstract_image_id
        return self.fetch(abstract_image_properties)

    

    def get_project_users(self, id_project):
        users = UserCollection()
        users.project = id_project
        return self.fetch(users)

    def upload_mask(self, url, filename):
        # poster
        register_openers()
        content_type = ""
        file_header = {"mask": open(filename, "rb")}
        datagen, headers = multipart_encode(file_header.items())
        # get the content_type
        for header in headers.items():
            if header[0] == "Content-Type":
                content_type = header[1]

        # post boundary
        self.__authorize("POST", url=url, content_type=content_type)
        fullHeaders = dict(headers.items() + self.__headers.items())
        fullURL = self.__protocol + self.__host + self.__base_path + url
        print "fullURL : %s " % fullURL
        # poster incompatible with httplib2 so we use urllib2
        request = urllib2.Request(fullURL, datagen, fullHeaders)
        response = urllib2.urlopen(request, timeout=self.__timeout)
        json_response = json.loads(response.read())
        return json_response['polygons']

    def prog_callback(self, param, current, total):
        pct = 100 - ((total - current) * 100) / (total)
        self.pbar.update(pct)

    def union_polygons(self, id_user, id_image, id_term, min_intersection_length, area, buffer_length=None):
        annotation_union = AnnotationUnion()
        annotation_union.id_user = id_user
        annotation_union.id_image = id_image
        annotation_union.id_term = id_term
        annotation_union.min_intersection_length = min_intersection_length
        annotation_union.buffer_length = buffer_length
        annotation_union.area = area
        # return self.update(annotation_union)
        return self.fetch(annotation_union)

    def included_annotations(self, id_image, id_user, id_annotation_roi, id_terms=[], reviewed_only=False):
        annotations = AnnotationCollection()
        annotations.included = True
        annotations.imageinstance = id_image
        # annotations.id_user = id_user
        # annotations.id_annotation_roi = id_annotation_roi
        # terms...
        if id_terms:
            query = "annotation=%d&user=%d&terms=%s" % (
            id_annotation_roi, id_user, str(id_terms).strip('[]').replace(' ', ''))
        else:
            query = "annotation=%d&user=%d" % (id_annotation_roi, id_user)

        if reviewed_only:
            query = query + "&reviewed=true"
        annotations = self.fetch(annotations, query=query)
        return annotations

    def init_storage_for_user(self, id):  # tmp method pour storage creation
        url = "storage/create/%d" % id
        self.__authorize("POST", url=url, content_type='application/json')
        if self.__verbose: print "POST %s..." % (self.__base_path + url)
        self.__conn.request("POST", self.__base_path + url, body="",
                            headers=dict(self.__headers.items() + [('content-type', 'application/json')]))
        response = self.__conn.getresponse()
        response_text = response.read()
        if self.__verbose: print "response_text : %s" % response_text

    def build_token_key(self, username, validity):
        upload_query = "token.json?username=%s&validity=%d" % (username, validity)
        fullURL = self.__protocol + self.__host + self.__base_path + upload_query
        resp, content = self.fetch_url(fullURL)
        print "%s => %s" % (resp, content)
        json_response = json.loads(content)
        return json_response.get('token')

    def __getstate__(self):  # Make cytomine client serializable
        self.__conn = None
        return self.__dict__
"""