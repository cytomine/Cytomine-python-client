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

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Track(Model):
    def __init__(self, name=None, id_image=None, color=None, **attributes):
        super(Track, self).__init__()
        self.name = name
        self.image = id_image
        self.color = color
        self.populate(attributes)


class TrackCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(TrackCollection, self).__init__(Track, filters, max, offset)
        self._allowed_filters = ["project", "imageinstance"]
        self.set_parameters(parameters)


class AnnotationTrack(Model):
    def __init__(self, annotation_class_name=None, id_annotation=None, id_track=None, **attributes):
        super(AnnotationTrack, self).__init__()
        self.annotationClassName = annotation_class_name
        self.annotationIdent = id_annotation
        self.track = id_track
        self.populate(attributes)

    def uri(self):
        return "annotationtrack/{}/{}.json".format(self.annotationIdent, self.track)

    def fetch(self, id_annotation=None, id_track=None):
        self.id = -1

        if self.annotationIdent is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.track is None and id_track is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.annotationIdent = id_annotation

        if id_track is not None:
            self.track = id_track

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a annotation-track.")

    def __str__(self):
        return "[{}] Annotation {} - Track {}".format(self.callback_identifier, self.annotationIdent, self.track)