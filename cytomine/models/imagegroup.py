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

import re
import os

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class ImageGroup(Model):
    def __init__(self, name=None, id_project=None, **attributes):
        super(ImageGroup, self).__init__()
        self.name = name
        self.project = id_project
        self.populate(attributes)


class ImageGroupCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageGroupCollection, self).__init__(ImageGroup, filters, max, offset)
        self._allowed_filters = ["project"]
        self.set_parameters(parameters)


class ImageGroupImageInstance(Model):
    def __init__(self, id_image_group=None, id_image_instance=None, **attributes):
        super(ImageGroupImageInstance, self).__init__()
        self.group = id_image_group
        self.image = id_image_instance
        self.populate(attributes)

    def uri(self):
        return f"imagegroup/{self.group}/imageinstance/{self.image}.json"

    def fetch(self, id_image_group=None, id_image_instance=None):
        self.id = -1

        if self.group is None and id_image_group is None:
            raise ValueError("Cannot fetch a model with no image group ID.")
        elif self.image is None and id_image_instance is None:
            raise ValueError("Cannot fetch a model with no image instance ID.")

        if id_image_group is not None:
            self.group = id_image_group

        if id_image_instance is not None:
            self.image = id_image_instance

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a image group-image instance relation.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] {self.id} : Group {self.group} "
            f"- Image {self.image}"
        )


class ImageGroupImageInstanceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageGroupImageInstanceCollection, self).__init__(ImageGroupImageInstance, filters, max, offset)
        self._allowed_filters = ["imagegroup", "imageinstance"]
        self.set_parameters(parameters)
