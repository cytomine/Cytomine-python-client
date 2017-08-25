# -*- coding: utf-8 -*-


#
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
# */

__author__          = "Stévens Benjamin <b.stevens@ulg.ac.be>" 
__contributors__    = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]                
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"



import os, sys
import sha, base64, hmac
import httplib, urllib2, httplib2
from progressbar import ProgressBar
import json
import warnings
import locale
from time import strftime, gmtime
import time
import shapely
from shapely.wkt import loads

try:
    import Image
except:
    from PIL import Image
import Queue

import socket

from .utils import ImageFetcher
from models import *

#API
class Cytomine(object):

    def __init__(self, host, public_key, private_key, working_path="/tmp", protocol="http://", base_path="/api/",
                 verbose=False, timeout=120):
        self.__protocol = protocol
        host = host.replace("http://" , "")
        host = host.replace("https://" , "")
        self.__host = host
        self.__timeout = timeout
        self.__base_path = base_path
        self.__public_key = public_key
        self.__private_key = private_key
        self.__working_path = working_path
        self.__cache = "%s/%s" %(working_path,".cache")
        self.__conn = None
        self.__headers = None
        self.__verbose = verbose

    # http://code.google.com/apis/storage/docs/reference/v1/developer-guidev1.html#authentication
    def __authorize(self, action, url="", content_type="", accept="application/json,*/*", sign_with_base_path = True):
        #sometimes url fetched are complete url, we have to remove  host and base_path in order to sign
        url = url.replace("http://%s%s" % (self.__host, self.__base_path), "")
        url = url.replace("https://%s%s" % (self.__host, self.__base_path), "")
        self.__conn = httplib.HTTPConnection(self.__host, timeout=self.__timeout)
        locale.setlocale(locale.LC_TIME)
        self.__headers = {'accept': accept, 'date': strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),
                          'X-Requested-With': 'XMLHttpRequest'}
        canonical__headers = "%s\n\n%s\n%s\n" % (action, content_type, self.__headers['date'])
        if sign_with_base_path:
            message_to_sign = "%s%s%s" % (canonical__headers, self.__base_path, url)
        else:
            message_to_sign = "%s%s" % (canonical__headers, url)
        #if self.__verbose : print "message_to_sign = %s " % message_to_sign
        signature = base64.b64encode(hmac.new(self.__private_key, message_to_sign, sha).digest())
        authorization = "CYTOMINE %s:%s" % (self.__public_key, signature)
        if self.__verbose: print "authorization = %s " % authorization
        self.__headers['authorization'] = authorization

    def set_credentials(self, public_key, private_key):
        self.__public_key = public_key
        self.__private_key = private_key

    def basic_auth(self, username, password):
        auth = base64.encodestring(username + ':' + password)
        self.__headers = {'content-type': 'application/json', 'accept': 'application/json',
                          'Authorization': 'Basic ' + auth, 'X-Requested-With': 'XMLHttpRequest'}

    def __handle_response(self, status):
        if self.__verbose: print "HTTP STATUS : %s" % status
        if status == 200: # or status == 304 or status == 201:
            return True
        elif status == 400:
            print "Bad Request"
            return False
        elif status == 404:
            print "Not Found"
            return False
        elif status == 401:
            print "Unauthorized"
            return False
        elif status == 500:
            print "Internal Server Error"
            return False
        else:
            print "Error Somewhere"
            return False

    def fetch(self, model, url="", query=""):
        if isinstance(model, Collection):
            if query == "":
                query = "?%s" % model.get_paginator_query()
            else:
                query = "?%s&%s" % (query, model.get_paginator_query())
        self.__authorize("GET", url = url + model.to_url() + query)
        if self.__verbose : print "GET %s..." % (self.__host + self.__base_path + url + model.to_url() + query)
        established = None
        while(not established):
            try:
                self.__conn.request("GET", self.__base_path + url + model.to_url() + query, headers=self.__headers)
                established = True
            #except socket.timeout, socket.error, Exception:
            except Exception:
                print "socket timeout/error while request GET"
                time.sleep(1)
                continue

        response = self.__conn.getresponse()
        response_text = response.read()
        if self.__verbose: print "response_text : %s" % response_text
        if not self.__handle_response(response.status):
            print response_text
            return None
        return model.__class__(json.dumps(json.loads(response_text)))

    def save_collection(self, collection, url="", query=""):
        if len(collection) < 1: return None

        model = collection[0]

        json_collections = []
        for model in collection:
            json_collections.append(model.to_json())
        data = "[%s]" % ','.join(json_collections)

        self.__authorize("POST", url=url + model.to_url() + query, content_type='application/json')
        if self.__verbose: print "POST %s..." % (self.__base_path + url + model.to_url() + query)
        if self.__verbose: print "DATA : %s" % data
        self.__conn.request("POST", self.__base_path + url + model.to_url() + query, body=data,
                            headers=dict(self.__headers.items() + [('content-type', 'application/json')]))
        response = self.__conn.getresponse()
        response_text = response.read()
        if self.__verbose: print "response_text : %s" % response_text
        if not self.__handle_response(response.status):
            return None
        response_data = json.loads(response_text)
        result = []
        for item in response_data:
            result_model = model.__class__(json.dumps(item['object']))
            result.append(result_model)
        return result

    def save(self, model, url = "", query = ""):
        self.__authorize("POST", url = url + model.to_url() + query, content_type = 'application/json')
        if self.__verbose : print "POST %s..." % (self.__base_path + url + model.to_url() + query)
        if self.__verbose : print "DATA : %s" % model.to_json()
        established = None
        while(not established):
            try:
                if self.__verbose:
                    print "base_path: %s" %self.__base_path
                    print "url: %s" %url
                    print "url: %s" %model.to_url()+query
                self.__conn.request("POST", self.__base_path + url + model.to_url() + query, body = model.to_json(), headers=dict(self.__headers.items()+[('content-type','application/json')]))
                established = True
            #except socket.timeout, socket.error, error, e, err:
            except Exception as inst:
                print "socket timeout/error while request POST"
                print type(inst)
                print inst
                time.sleep(1)
                continue

        response = self.__conn.getresponse()
        response_text = response.read()
        if self.__verbose: print "response_text : %s" % response_text
        if not self.__handle_response(response.status):
            return None
        return model.__class__(json.dumps(json.loads(response_text)[model._callback_identifier]))

    def update(self, model, url="", query=""):
        self.__authorize("PUT", url=url + model.to_url() + query, content_type='application/json')
        if self.__verbose: print "PUT %s..." % (self.__base_path + url + model.to_url() + query)
        if self.__verbose: print "DATA : %s" % model.to_json()
        self.__conn.request("PUT", self.__base_path + url + model.to_url() + query, body=model.to_json(),
                            headers=dict(self.__headers.items() + [('content-type', 'application/json')]))

        response = self.__conn.getresponse()
        response_text = response.read()
        if not self.__handle_response(response.status):
            print response_text
            return None
        return model.__class__(json.dumps(json.loads(response_text)[model._callback_identifier]))

    def delete(self, model, url = "", query = ""):
        self.__authorize("DELETE", url = url + model.to_url() + query, content_type = 'application/json')
        if self.__verbose : print "DELETE %s..." % (self.__base_path + url + model.to_url() + query)
        established = None
        while(not established):
            try:
                self.__conn.request("DELETE", self.__base_path + url + model.to_url() + query, headers=dict(self.__headers.items()+[('content-type','application/json')]))
                established = True
            #except socket.timeout, socket.error, error, e, err:
            except Exception:
                print "socket timeout/error while request PUT"
                time.sleep(1)
                continue
        response = self.__conn.getresponse()
        if not self.__handle_response(response.status):
            return False
        return True


    def fetch_url_into_file(self, url, filename, is_image=True, override=False):
        if override or not (os.path.exists(filename)):
            if self.__verbose: print "fetch %s \n into %s" % (url, filename)
            resp, content = self.fetch_url(url)
            try:
                f = open(filename, 'wb')
                f.write(content)
                f.close()
                #if (is_image):                    
                #    im = Image.open(filename)
                #    im.verify()
                return True
            except IOError:
                print "CROP ERROR : %s " % filename
                os.remove(filename)
                return False
        elif os.path.exists(filename):
            return True

    def fetch_url(self, url):
        if self.__verbose : print "fetch %s" % url
        self.__authorize("GET", url = url, accept = "")
#        httplib2.debuglevel=4                
        con = httplib2.Http(self.__cache, timeout=self.__timeout)                
        con.follow_all_redirects = False
        con.follow_redirects = False
        resp, content = con.request(url, headers=self.__headers)
        if (resp.status == 302 or resp.status == 301): #redirect or moved permanently
            return self.fetch_url(resp['location'])
        else:
            return resp, content

    #Project
    def add_project(self, project_name, id_ontology):
        project = Project()
        project.name = project_name
        project.ontology = id_ontology
        return self.save(project)

    def get_projects(self):
        projects = ProjectCollection()
        projects = self.fetch(projects)
        return projects

    def get_project(self, id_project):
        project = Project()
        project.id = id_project
        return self.fetch(project)

    def edit_project(self, id_project, project_name, id_ontology):
        project = self.get_project(id_project)
        project.name = project_name
        project.ontology = id_ontology
        return self.update(project)

    def delete_project(self, id_project):
        project = self.get_project(id_project)
        return self.delete(project)

    #Ontology
    def add_ontology(self, name):
        ontology = Ontology()
        ontology.name = name
        return self.save(ontology)

    def delete_ontology(self, id_ontology):
        ontology = Ontology()
        ontology.id = id_ontology
        return self.delete(ontology)

    def get_ontology(self, id_ontology):
        ontology = Ontology()
        ontology.id = id_ontology
        return self.fetch(ontology)

    #Term
    def add_term(self, name, id_ontology, color="#ff0000"):
        term = Term()
        term.name = name
        term.ontology = id_ontology
        term.color = color
        return self.save(term)

    def add_relation_term(self, id_parent, id_child):
        relation_term = RelationTerm()
        relation_term.is_new = True
        relation_term.term1 = id_parent
        relation_term.term2 = id_child
        return self.save(relation_term)

    def delete_relation_term(self, id_parent, id_child):
        relation_term = RelationTerm()
        relation_term.term1 = id_parent
        relation_term.term2 = id_child
        return self.delete(relation_term)

    def delete_term(self, id_term):
        term = Term()
        term.id = id_term
        return self.delete(term)

    def get_terms(self, id_ontology=None):
        terms = TermCollection()
        if id_ontology:
            terms.ontology = id_ontology
        return self.fetch(terms)

    #User    
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

    #tmp service, should be done by add job service
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

    #Role
    def get_role(self, id):
        role = Role()
        role.id = id
        return self.fetch(role)

    def get_roles(self, filter_by_authority=None):
        #filter_by_authority : ROLE_USER or ROLE_ADMIN
        roles = RoleCollection()
        roles = self.fetch(roles)
        if filter_by_authority:
            roles = [i for i in roles.data() if i.authority == filter_by_authority]
            roles = roles.pop()
        return roles

    #UserRole
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
        user_role.id = id_role * id_user #fake_id                
        return self.fetch(user_role)

    #group
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

    #image_instance
    def add_image_instance(self, id_base_image, id_project):
        image = ImageInstance()
        image.baseImage = id_base_image
        image.project = id_project
        return self.save(image)

    def get_image_instance(self, id_image_instance=None, include_server_urls=False):
        image = ImageInstance()
        if id_image_instance:
            image.id = id_image_instance

        image = self.fetch(image)
        if include_server_urls:
            server_urls = ImageInstanceServersURL()
            server_urls.id = image.baseImage
            server_urls = self.fetch(server_urls)
            image.server_urls = server_urls.imageServersURLs

        return image

    def delete_image_instance(self, id_image_instance):
        image = self.get_image_instance(id_image_instance)
        return self.delete(image)


    #imagegroup
    def get_image_group(self, id_image_group = None):
        image_group = ImageGroup()
        if id_image_group:
            image_group.id = id_image_group
        return self.fetch(image_group)


    def delete_image_group(self, id_image_group):
        imagegrp = self.get_image_group(id_image_group)
        return self.delete(imagegrp)


    #userGroup
    def add_user_group(self, id_user, id_group):
        userGroup = UserGroup()
        userGroup.user = id_user
        userGroup.group = id_group
        return self.save(userGroup)

    #userGroup
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

    #userGroup
    def delete_user_group(self, id_user, id_group):
        userGroup = self.get_user_group(id_user, id_group)
        return self.delete(userGroup)

    # annotations
    def get_annotations(self, id_project = None, id_user = None, id_image = None, id_term = None, showGIS = None, showWKT = None, showMeta = None, bbox = None, id_bbox= None, reviewed_only = False):
        annotations = AnnotationCollection()
        query=""
        if id_project:
            query += "&project=" + str(id_project)
        if id_term:
            query += "&terms=" + str(id_term)  # terms for multiple, term instead
        if id_user:
            # TODO use ReviewedAnnotationCollection instead of messing with user field
            query = "{}&{}={}".format(query, "reviewUsers" if reviewed_only else "users",
                                      str(id_user).strip('[]').replace(' ', ''))
        if id_image:
            query += "&images=%s" % str(id_image).strip('[]').replace(' ', '')
        if bbox:
            query += "&bbox=%s" % urllib.quote_plus(bbox)  # %str(bbox).strip('[]').replace(' ','%20')
        if id_bbox:
            query += "&bboxAnnotation=%s" % str(id_bbox)
        if showGIS:
            query += "&showGIS=true"
        if showWKT:
            query += "&showWKT=true"
        if showMeta:
            query += "&showMeta=true"
        if showMeta or showGIS or showWKT:
            query += "&showTerm=true"
        if reviewed_only:
            query += "&reviewed=true"
                
        # print query
        annotations = self.fetch(annotations,query=query)
        return annotations

    def get_reviewed_annotations(self, id_project=None):
        annotations = ReviewedAnnotationCollection()
        if id_project:
            annotations.project = id_project
        annotations = self.fetch(annotations)
        return annotations

    def get_annotation(self, id_annotation=None):
        annotation = AnnotationCollection()
        if id_annotation:
            annotation = Annotation()
            annotation.id = id_annotation
        return self.fetch(annotation)

    def add_annotation(self, location, id_image, minPoint = None, maxPoint = None):
        query=""
        annotation = Annotation()
        annotation.location = location
        annotation.image = id_image
        annotation.name = ""
        if minPoint:
            query = query + "&minPoint=" + str(minPoint)
        if maxPoint:
            query = query + "&maxPoint=" + str(maxPoint)
        return self.save(annotation,query=query)

    def add_annotations(self, locations, id_image):
        annotations = []
        image = self.get_image_instance(id_image)
        for location in locations:
            annotation = Annotation()
            annotation.location = location
            annotation.image = id_image
            annotation.name = ""
            annotation.project = image.project
            annotations.append(annotation)
        return self.save_collection(annotations)

    def add_annotations_with_term(self, locations, id_image, id_term):
        annotations = []
        image = self.get_image_instance(id_image)
        for location in locations:
            annotation = Annotation()
            annotation.location = location
            annotation.image = id_image
            annotation.name = ""
            annotation.project = image.project
            annotation.term = id_term
            annotations.append(annotation)
        return self.save_collection(annotations)

    def delete_annotation(self, id_annotation):
        annotation = self.get_annotation(id_annotation)
        return self.delete(annotation)

    def delete_annotations(self, idProject, idUser):
        success = True
        annotations = self.get_annotations(idProject)
        for annotation in annotations.data():
            if idUser == annotation.user:
                success = success and self.deleteAnnotation(annotation.id)
        return success

    # annotation_term
    def add_annotation_term(self, id_annotation, term, expected_term, rate, annotation_term_model=AnnotationTerm):
        annotation_term = annotation_term_model()
        annotation_term.annotationIdent = id_annotation
        annotation_term.annotation = id_annotation
        annotation_term.term = term
        annotation_term.expectedTerm = expected_term
        annotation_term.rate = rate
        self.save(annotation_term)

    def add_user_annotation_term(self, id_annotation, term, expected_term, rate, annotation_term_model = AnnotationTerm):
        annotation_term = annotation_term_model()
        annotation_term.userannotation = id_annotation
        annotation_term.annotation = id_annotation
        annotation_term.term = term
        annotation_term.expectedTerm =expected_term        
        annotation_term.rate = rate
        self.save(annotation_term)

    def add_user_annotation_term(self, id_annotation, term):
        annotation_term = AnnotationTerm()
        annotation_term.userannotation = id_annotation
        annotation_term.annotation = id_annotation
        annotation_term.term = term
        #annotation_term.expectedTerm =term        
        #annotation_term.rate = 1.0
        self.save(annotation_term)


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

    # uploadedfile
    def get_uploaded_file(self, id_uploaded_file):
        uploaded_file = UploadedFile()
        uploaded_file.id = id_uploaded_file
        return self.fetch(uploaded_file)

    # storage
    def get_storage(self, id_storage):
        storage = Storage()
        storage.id = id_storage
        return self.fetch(storage)
        
    # software
    def get_software(self, id_software):
        software = Software()
        software.id = id_software
        return self.fetch(software)

    def add_software(self, name, service_name, result_name):
        software = Software()
        software.name = name
        software.serviceName = service_name
        software.resultName = result_name
        return self.save(software)


    def add_software(self, name, service_name, result_name, execute_command=None):
        software = Software()
        software.name = name
        software.serviceName = service_name
        software.resultName = result_name
        software.executeCommand = execute_command
        return self.save(software)


    # software project
    def add_software_project(self, project, software):
        software_project = SoftwareProject()
        software_project.project = project
        software_project.software = software
        return self.save(software_project)

        #software_parameters

    def add_software_parameter(self, name, id_software, type, default_value, required, index, set_by_server, uri=None,
                               uriPrintAttribut=None, uriSortAttribut=None):
        software_parameter = SoftwareParameter()
        software_parameter.name = name
        software_parameter.software = id_software
        software_parameter.type = type #String #Integer
        software_parameter.defaultValue = default_value
        software_parameter.required = required
        software_parameter.index = index
        software_parameter.setByServer = set_by_server
        software_parameter.uri = uri
        software_parameter.uriPrintAttribut = uriPrintAttribut
        software_parameter.uriSortAttribut = uriSortAttribut
        return self.save(software_parameter)


    def get_software_parameter(self, id_software_parameter):
        software_parameter = SoftwareParameter()
        software_parameter.id = id_software_parameter
        return self.fetch(software_parameter)

    def delete_software_parameter(self, id_software_parameter):
        software_parameter = self.get_software_parameter(id_software_parameter)
        if software_parameter:
            return self.delete(software_parameter)
        else:
            return None



    # Job
    def get_job(self, id_job):
        job = Job()
        job.id = id_job
        return self.fetch(job)

    # Job Parameter
    def add_job_parameter(self, id_job, id_software_parameter, value):
        job_parameter = JobParameter()
        job_parameter.job = id_job
        job_parameter.softwareParameter = id_software_parameter
        job_parameter.value = value
        return self.save(job_parameter)

    def add_job_parameters(self, job, software, values):
        #software = conn.getSoftware(id_software)
        #software_parameters_map = {}
        job_parameters_values = {}
        for software_parameter in software.parameters:
            software_parameter_name = software_parameter["name"]
            if values[software_parameter["name"]]:
                job_parameters_values[software_parameter["id"]] = software_parameter_name, values[
                    software_parameter_name]
            else:
                job_parameters_values[software_parameter["id"]] = software_parameter_name, software_parameter[
                    "defaultParamValue"]

        for software_parameter_id in job_parameters_values:
            name, value = job_parameters_values[software_parameter_id]
            self.add_job_parameter(job, software_parameter_id, value)
        return job_parameters_values

    def add_job_data(self, job, key, filename):
        job_data = JobData()
        job_data.job = job.id
        job_data.key = key
        job_data.filename = filename
        job_data = self.save(job_data)
        self.upload_job_data_file(job_data, filename)
        return job_data
        #Read filename and upload

    def get_job_data_file(self, id_job_data, dest_path):
        job_data = JobData()
        job_data.id = id_job_data
        job_data = self.fetch(job_data)
        url = "jobdata/%d/download" % job_data.id
        fullURL = self.__protocol + self.__host + self.__base_path + url
        return self.fetch_url_into_file(fullURL, dest_path, is_image, False)

    def update_job_status(self, job, status=None, status_comment=None, progress=None):
        if self.__verbose: print status_comment
        if status: job.status = status
        if status_comment: job.statusComment = str(status_comment)
        if progress: job.progress = int(progress)
        if (status or status_comment) or progress:
            return self.update(job)
        else:
            return job

    #JobTemplate
    def add_job_template(self, name, id_project, id_software):
        job_template = JobTemplate()
        job_template.name = name
        job_template.project = id_project
        job_template.software = id_software
        return self.save(job_template)


    # Check / for destPath

    #old
    def _dump_annotations(self, annotations, get_image_url_func=Annotation.get_annotation_crop_url, dest_path="/tmp",
                         override=False, excluded_terms=[], desired_zoom=None, desired_max_size=None):
        if not (os.path.exists(dest_path)):
            os.mkdir(dest_path)
        nbAnnotations = len(annotations.data())

        images = []
        pbar = None
        if self.__verbose:
            pbar = ProgressBar(maxval=nbAnnotations).start()

        queue = Queue.Queue()
        threads = []
        for i in xrange(3):
            t = ImageFetcher(queue, self, override, pbar)
            threads.append(t)
            t.setDaemon(True)
            t.start()

        for annotation in annotations.data():

            if self.__verbose and not (len(annotation.term)):
                print "Skip %s/%s : annotation (%s) without term " % (i, nbAnnotations, annotation.id)
                continue

            for term in annotation.term:
                if term in excluded_terms:
                    continue
                    #Create term path
                termPath = os.path.join(dest_path, str(term))
                if not (os.path.exists(termPath)):
                    os.mkdir(termPath)
                filename = "%s/%d.png" % (termPath, annotation.id)
                #print "SETTING filename attribute"
                #time.sleep(1)
                setattr(annotation, "filename", filename)
                if False and annotation.area == 0:
                    print "Skip %s/%s : annotation (%s) area is equal to 0" % (i, nbAnnotations, annotation.id)
                    if os.path.exists(filename):
                        os.remove(filename)
                else:
                    print "Get crop at zoom %d" % desired_zoom
                    cropURL = get_image_url_func(annotation, desired_zoom, desired_max_size)
                    print cropURL
                    #print "annotation filename: %s" %annotation.filename
                    #put into queue
                    queue.put((cropURL, filename, annotation))

        queue.join()
        if self.__verbose:
            pbar.finish()

        return annotations
        
    #dump_annotations takes a collection of annotations and generates in dest_path cropped images according to zoom/translation/tile parameters
    def dump_annotations(self, annotations, get_image_url_func = Annotation.get_annotation_crop_url, dest_path = "/tmp", override = False, excluded_terms = [], desired_zoom = None, desired_max_size = None, tile_size = None, translate = None):
        if not(os.path.exists(dest_path)):
            os.makedirs(dest_path)                    
        
        nbAnnotations = len(annotations.data())

        images = []
        pbar = None
        if self.__verbose:
            pbar = ProgressBar(maxval=nbAnnotations).start()

        queue = Queue.Queue()
        threads = []
        for i in xrange(3):
            t = ImageFetcher(queue, self,  override, pbar)
            threads.append(t)
            t.setDaemon(True)
            t.start()

        for annot in annotations.data():                            
            
            if self.__verbose and not(len(annot.term)):
                print "Skip %s/%s : annotation (%s) without term " % (i, nbAnnotations, annot.id)
                continue

            for term in annot.term:
                if term in excluded_terms: 
                    continue
                #Create term path
                termPath = os.path.join(dest_path, str(term))
                if not(os.path.exists(termPath)):
                    os.mkdir(termPath)
                filename = "%s/%d_%d.png" % (termPath, annot.image,annot.id)
                #print "SETTING filename attribute"
                #time.sleep(1)
                setattr(annot, "filename", filename)
                if False and annot.area == 0:
                    print "Skip %s/%s : annotation (%s) area is equal to 0" % (i, nbAnnotations, annot.id)
                    if os.path.exists(filename): 
                        os.remove(filename)
                else:
                    if tile_size:
                        #extend the area to use a fixed-size tile (assuming the tile is larger than the annotation bounding box)
                        print "Fixed tile cropURL"
                        p_annotation = self.get_annotation(annot.id)
                        p = loads(p_annotation.location)
                        minx, miny, maxx, maxy = int(p.bounds[0]), int(p.bounds[1]), int(p.bounds[2]), int(p.bounds[3])    
                        image = self.get_image_instance(p_annotation.image)
                        for t in range(0,translate):
                            original_cropURL = get_image_url_func(annot, desired_zoom, desired_max_size)
                            print "original cropURL = %s" %original_cropURL
                            cropURL = self.__protocol + self.__host + self.__base_path + Annotation.get_annotation_crop_tiled_translated(annot,minx,maxx,miny,maxy,p_annotation.image,image.height,tile_size,translate)
                            print "tiled cropURL: %s" %cropURL
                            filename = "%s/%d_%d_%d_translated_%d.png" % (termPath, annot.image,annot.id, tile_size,t)
                            queue.put((cropURL, filename, annot))
                                                
                    else:   
                        #use original cropURL (smallest bounding box around the annotation)
                        if self.__verbose:
                            print "Get crop at zoom %d" %desired_zoom
                        cropURL = get_image_url_func(annot, desired_zoom, desired_max_size)
                        if self.__verbose:
                            print "cropURL: %s" %cropURL
                        queue.put((cropURL, filename, annot))

        queue.join()
        if self.__verbose:
            pbar.finish()

        return annotations
	

    def get_project_users(self, id_project):
        users = UserCollection()
        users.project = id_project
        return self.fetch(users)

    def get_project_image_instances(self, id_project):
        image_instances = ImageInstanceCollection()
        image_instances.project = id_project
        return self.fetch(image_instances)
        
    def get_term(self,id_term):
        term = Term()
        term.id = id_term
        return self.fetch(term)

    # Check / for destPath
    def dump_project_images(self, id_project=None, dest_path="imageinstances/", override=False, image_instances=None, max_size=None):
        images = []
        if not (os.path.exists(self.__working_path)):
            print "Working path (%s) does not exist" % self.__working_path
            return False
        projectPath = self.__working_path + dest_path
        if not (os.path.exists(projectPath)):
            os.mkdir(projectPath)
        projectPath += str(id_project)
        if not (os.path.exists(projectPath)):
            os.mkdir(projectPath)
        if not (image_instances): #fetch all images from project
            image_instances = ImageInstanceCollection()
            image_instances.project = id_project
            image_instances = self.fetch(image_instances)
            image_instances = image_instances.data() #acces to models
        pbar = ProgressBar(maxval=len(image_instances)).start()
        i = 0
        for image_instance in image_instances:
            filename = projectPath + "/" + str(image_instance.id) + ".jpg"
            setattr(image_instance, "filename", filename)
            images.append(image_instance)
            if (not (os.path.exists(filename)) or (os.path.exists(filename) and override)):
                if (type(max_size) is int):
                    url = image_instance.preview[0:image_instance.preview.index('?')] + "?maxSize=" + str(max_size)
                elif(max_size):
                    url = image_instance.preview[0:image_instance.preview.index('?')] + "?maxSize=" + str(max(image_instance.width,image_instance.height))
                else:
                    url = image_instance.preview
                self.fetch_url_into_file(url, filename, override)
            pbar.update(i)
        pbar.finish()
        return images

    def upload_job_data_file(self, job_data, filename):
        from poster.encode import multipart_encode
        from poster.streaminghttp import register_openers

        url = 'jobdata/%d/upload' % job_data.id

        # Build the request
        register_openers()
        file_header = {"files[]": open(filename, "rb")}
        datagen, headers = multipart_encode(file_header.items())
        #get the content_type
        for header in headers.items():
            if header[0] == "Content-Type":
                content_type = header[1]

        self.__authorize("POST", url=url, content_type=content_type)
        fullHeaders = dict(headers.items() + self.__headers.items())
        fullURL = self.__protocol + self.__host + self.__base_path + url
        #poster incompatible with httplib2 so we use urllib2
        request = urllib2.Request(fullURL, datagen, fullHeaders)
        response = urllib2.urlopen(request, timeout=self.__timeout).read()
        json_response = json.loads(response)
        return json_response

    def upload_mask(self, url, filename):
        #poster
        register_openers()
        content_type = ""
        file_header = {"mask": open(filename, "rb")}
        datagen, headers = multipart_encode(file_header.items())
        #get the content_type
        for header in headers.items():
            if header[0] == "Content-Type":
                content_type = header[1]

        #post boundary
        self.__authorize("POST", url=url, content_type=content_type)
        fullHeaders = dict(headers.items() + self.__headers.items())
        fullURL = self.__protocol + self.__host + self.__base_path + url
        print "fullURL : %s " % fullURL
        #poster incompatible with httplib2 so we use urllib2
        request = urllib2.Request(fullURL, datagen, fullHeaders)
        response = urllib2.urlopen(request, timeout=self.__timeout)
        json_response = json.loads(response.read())
        return json_response['polygons']               

    def prog_callback(self, param, current, total):        
        pct = 100 - ((total - current ) *100 )/ (total) 
        self.pbar.update(pct)

        
    def upload_image(self, filename, project, storage, cytomine_host, sync = False,properties = None):
        import urllib
        from poster.encode import multipart_encode
        from poster.streaminghttp import register_openers

        query_params = {"idStorage": storage, "cytomine" : cytomine_host,"sync" : sync}

        if properties:
            keys = []
            values = []
            for k, v in properties.iteritems():
                keys.append(k)
                values.append(v)
            query_params["keys"] = ','.join(keys)
            query_params["values"] = ','.join(values)
		
        if project:
			query_params["idProject"] = project


        upload_query = "/upload?%s" % urllib.urlencode(query_params)

        #poster
        register_openers()
        content_type = ""
        file_header = {"files[]": open(filename, "rb")}
        
        datagen, headers = multipart_encode(file_header.items(), cb=self.prog_callback)
        #get the content_type
        for header in headers.items():
            if header[0] == "Content-Type":
                content_type = header[1]

        #post boundary
        self.__authorize("POST", url=upload_query, content_type=content_type, sign_with_base_path = False)
        fullHeaders = dict(headers.items() + self.__headers.items())
        fullURL = self.__protocol + self.__host + upload_query

        self.pbar = ProgressBar(100)
        self.pbar.start()
        #poster incompatible with httplib2 so we use urllib2
        request = urllib2.Request(fullURL, datagen, fullHeaders)
        response = urllib2.urlopen(request, timeout=self.__timeout)
        json_response = json.loads(response.read())
        self.pbar.finish()
        return {'status' : json_response[0].get('status'), 'uploaded_file' : json.loads(json_response[0].get('uploadFile'))}

    def get_sample(self, id_sample):
        sample = Sample()
        sample.id = id_sample
        return self.fetch(sample)

    def add_sample(self, name, index):
        sample = Sample()
        sample.name = name
        sample.index = index
        return self.save(sample)

    def edit_sample(self, id, name, index):
        sample = self.get_sample(id)
        sample.name = name
        sample.index = index
        return self.update(sample)

    def delete_sample(self, id):
        sample = self.get_sample(id)
        return self.delete(sample)

    def get_image(self, id_image):
        image = Image()
        image.id = id_image
        return self.fetch(image)

#    def edit_image(self, id_image, filename, path, mime):
#        image = self.get_image(id_image)
#        image.filename = filename
#        image.path = path
#        image.mime = mime
#        return self.update(image)

    def edit_image(self, id_image, filename = None, path = None, mime = None, id_sample = None, id_scanner = None, magnification = None, resolution = None):
        image = self.get_image(id_image)
        if filename:
            image.filename = filename
        if path:
	    image.path = path
	if mime:
            image.mime = mime
        if id_sample:
            image.sample = id_sample
	if id_scanner:
            image.scanner = id_scanner
        if magnification:
            image.magnification = magnification
	if resolution:
            image.resolution = resolution
        return self.update(image)

    def delete_image(self, id_image):
        image = self.get_image(id_image)
        return self.delete(image)

    def union_polygons(self, id_user, id_image, id_term, min_intersection_length, area, buffer_length = None):
        annotation_union = AnnotationUnion()
        annotation_union.id_user = id_user
        annotation_union.id_image = id_image
        annotation_union.id_term = id_term
        annotation_union.min_intersection_length = min_intersection_length
        annotation_union.buffer_length = buffer_length
        annotation_union.area = area
        #return self.update(annotation_union)        
        return self.fetch(annotation_union)

    def included_annotations(self, id_image, id_user, id_annotation_roi, id_terms = [], reviewed_only = False):
        annotations = AnnotationCollection()
        annotations.included = True
        annotations.imageinstance = id_image
        #annotations.id_user = id_user
        #annotations.id_annotation_roi = id_annotation_roi
        #terms...
        if id_terms:
            query = "annotation=%d&user=%d&terms=%s" % (id_annotation_roi, id_user,str(id_terms).strip('[]').replace(' ',''))
        else:
            query = "annotation=%d&user=%d" % (id_annotation_roi, id_user)

        if reviewed_only:
            query = query + "&reviewed=true"
        annotations = self.fetch(annotations,query=query)
        return annotations

    
    def init_storage_for_user(self, id): #tmp method pour storage creation
        url = "storage/create/%d" % id
        self.__authorize("POST", url=url, content_type='application/json')
        if self.__verbose: print "POST %s..." % (self.__base_path + url)
        self.__conn.request("POST", self.__base_path + url, body="",
                            headers=dict(self.__headers.items() + [('content-type', 'application/json')]))
        response = self.__conn.getresponse()
        response_text = response.read()
        if self.__verbose: print "response_text : %s" % response_text

    def build_token_key(self, username, validity):
        upload_query = "token.json?username=%s&validity=%d" % (username,validity)
        fullURL = self.__protocol + self.__host + self.__base_path + upload_query
        resp, content = self.fetch_url(fullURL)
        print "%s => %s" % (resp,content)
        json_response = json.loads(content)
        return json_response.get('token')

    def __getstate__(self):  # Make cytomine client serializable
        self.__conn = None
        return self.__dict__
