# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2018. Authors: see NOTICE file.
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
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

import re
import os

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class AbstractImage(Model):
    def __init__(self, filename=None, mime=None, **attributes):
        super(AbstractImage, self).__init__()
        self.filename = filename
        self.path = filename
        self.mime = mime
        self.originalFilename = None
        self.width = None
        self.height = None
        self.resolution = None
        self.magnification = None
        self.bitdepth = None
        self.colorspace = None

        self.thumb = None
        self.preview = None

        self.populate(attributes)
        self._image_servers = None

    def image_servers(self):
        if not self._image_servers:
            data = Cytomine.get_instance().get("{}/{}/imageservers.json".format(self.callback_identifier, self.id))
            self._image_servers = data["imageServersURLs"]
        return self._image_servers

    def download(self, dest_pattern="{originalFilename}", override=True, parent=False):
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        parameters = {"parent": parent}

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     dest_pattern, override, parameters)

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.filename)

    # def get_property_url(self, extract=False):
    #     if extract:
    #         return "abstractimage/%d/property.json?extract=true" % self.id
    #     else:
    #         return "abstractimage/%d/property.json" % self.id


class AbstractImageCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AbstractImageCollection, self).__init__(AbstractImage, filters, max, offset)
        self._allowed_filters = [None]  # "project"]
        self.set_parameters(parameters)


class ImageInstance(Model):
    def __init__(self, id_abstract_image=None, id_project=None, **attributes):
        super(ImageInstance, self).__init__()
        self.baseImage = id_abstract_image
        self.project = id_project
        self.user = None
        self.filename = None
        self.originalFilename = None
        self.instanceFilename = None
        self.path = None
        self.mime = None
        self.width = None
        self.height = None
        self.resolution = None
        self.magnification = None
        self.bitdepth = None
        self.colorspace = None
        self.preview = None
        self.thumb = None
        self.numberOfAnnotations = None
        self.numberOfJobAnnotations = None
        self.numberOfReviewedAnnotations = None
        self.reviewed = None
        self.populate(attributes)
        self._image_servers = None

    def image_servers(self):
        if not self._image_servers:
            data = Cytomine.get_instance().get("abstractimage/{}/imageservers.json".format(self.baseImage))
            self._image_servers = data["imageServersURLs"]
        return self._image_servers

    def download(self, dest_pattern="{originalFilename}", override=True, parent=False):
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        parameters = {"parent": parent}

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     dest_pattern, override, parameters)

    def dump(self, dest_pattern="{id}.jpg", override=True, max_size=None):
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)

        destination = os.path.dirname(dest_pattern)
        filename, extension = os.path.splitext(os.path.basename(dest_pattern))

        if extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        if not os.path.exists(destination):
            os.makedirs(destination)

        if isinstance(max_size, tuple):
            max_size = max(self.width, self.height)

        parameters = {
            "maxSize": max_size,
        }

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        url = self.preview[:self.preview.index("?")]
        url = url.replace(".png", ".{}".format(extension))
        result = Cytomine.get_instance().download_file(url, file_path, override, parameters)
        if result:
            self.filename = file_path
        return result

    # def get_crop_url(self, position):
    #     return "imageinstance/%d/window-%d-%d-%d-%d.png" % (
    #     self.id, position['x'], position['y'], position['w'], position['h'])
    #
    # def get_crop_geometry_url(self, geometry):
    #     return "imageinstance/%d/cropgeometry?geometry=%s" % (self.id, geometry.replace(" ", "%20"))

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.filename)


class ImageInstanceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageInstanceCollection, self).__init__(ImageInstance, filters, max, offset)
        self._allowed_filters = ["project"]  # "user"
        self.set_parameters(parameters)
