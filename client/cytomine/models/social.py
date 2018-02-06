# -*- coding: utf-8 -*-


#
# * Copyright (c) 2009-2017. Authors: see NOTICE file.
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

__author__          = "Marée Raphaël <raphael.maree@ulg.ac.be>"
__copyright__       = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"


from client.cytomine.models.collection import Collection
from client.cytomine.models.model import Model


class Position(Model):
    def __init__(self):
        super(Position, self).__init__()
        self.user = None
        self.image = None
        self.project = None
        self.session = None
        self.location = None
        self.zoom = None
        self.x = None
        self.y = None


class PositionCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(PositionCollection, self).__init__(Position, filters, max, offset)
        self._allowed_filters = ["imageinstance"]

        self.user = None
        self.afterThan = None
        self.beforeThan = None
        self.showDetails = True
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        return "positions"


class AnnotationAction(Model):
    def __init__(self):
        super(AnnotationAction, self).__init__()
        self.user = None
        self.image = None
        self.project = None
        self.annotationClassName = None
        self.annotationIdent = None
        self.annotationCreator = None
        self.action = None


class AnnotationActionCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AnnotationActionCollection, self).__init__(AnnotationAction, filters, max, offset)
        self._allowed_filters = ["imageinstance"]

        self.user = None
        self.afterThan = None
        self.beforeThan = None
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        return "annotationactions"
