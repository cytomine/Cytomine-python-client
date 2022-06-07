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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Position(Model):
    def __init__(self):
        super(Position, self).__init__()
        self.user = None
        self.image = None
        self.slice = None
        self.project = None
        self.broadcast = None
        self.location = None
        self.zoom = None
        self.rotation = None
        self.x = None
        self.y = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a new position by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete a position.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a position.")


class PositionCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(PositionCollection, self).__init__(Position, filters, max, offset)
        self._allowed_filters = ["imageinstance", "sliceinstance"]

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
        self.slice = None
        self.project = None
        self.annotationClassName = None
        self.annotationIdent = None
        self.annotationCreator = None
        self.action = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a new annotation action by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete an annotation action.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update an annotation action.")

    @property
    def callback_identifier(self):
        return "annotation_action"


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
        return "annotation_action"
