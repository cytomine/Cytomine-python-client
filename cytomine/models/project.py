# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2022. Authors: see NOTICE file.
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

from cytomine import Cytomine

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Project(Model):
    def __init__(self, name=None, id_ontology=None, **attributes):
        super(Project, self).__init__()
        self.name = name
        self.ontology = id_ontology
        self.ontologyName = None
        self.discipline = None
        self.blindMode = None
        self.disciplineName = None
        self.numberOfSlides = None
        self.numberOfImages = None
        self.numberOfAnnotations = None
        self.numberOfJobAnnotations = None
        self.retrievalProjects = None
        self.numberOfReviewedAnnotations = None
        self.retrievalDisable = None
        self.retrievalAllOntology = None
        self.isClosed = None
        self.isReadOnly = None
        self.hideUsersLayers = None
        self.hideAdminsLayers = None

        self.admins = None
        self.users = None
        self.mode = None
        self.populate(attributes)

    def add_user(self, id_user, admin=False):
        if admin:
            return Cytomine.get_instance().post("project/{}/user/{}/admin.json".format(self.id, id_user))
        else:
            return Cytomine.get_instance().post("project/{}/user/{}.json".format(self.id, id_user))

    def delete_user(self, id_user, admin=False):
        if admin:
            return Cytomine.get_instance().delete("project/{}/user/{}/admin.json".format(self.id, id_user))
        else:
            return Cytomine.get_instance().delete("project/{}/user/{}.json".format(self.id, id_user))


class ProjectCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ProjectCollection, self).__init__(Project, filters, max, offset)
        self._allowed_filters = [None, "user", "software", "ontology"]
        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a project collection by client.")


class Discipline(Model):
    def __init__(self, name=None, **attributes):
        super(Discipline, self).__init__()
        self.name = name
        self.populate(attributes)


class DisciplineCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(DisciplineCollection, self).__init__(Discipline, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)
