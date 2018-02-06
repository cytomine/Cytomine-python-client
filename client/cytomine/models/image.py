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
import re

import os

from client.cytomine.cytomine import Cytomine

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"

from client.cytomine.models.collection import Collection
from client.cytomine.models.model import Model


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

        self.thumb = None
        self.preview = None

        self.populate(attributes)

    def fetch_with_image_servers(self, id):
        self.fetch(id)
        self.imageServersURLs = ImageServersURL.fetch(self.id).imageServersURLs
        return self

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
        self._allowed_filters = ["project"]
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
        self.preview = None
        self.thumb = None
        self.numberOfAnnotations = None
        self.numberOfJobAnnotations = None
        self.numberOfReviewedAnnotations = None
        self.reviewed = None
        self.populate(attributes)

    def fetch_with_image_servers(self, id):
        self.fetch(id)
        self.imageServersURLs = ImageServersURL.fetch(self.baseImage).imageServersURLs
        return self

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


class ImageServersURL(Model):
    def __init__(self):
        super(ImageServersURL, self).__init__()
        self.id = None
        self.imageServersURLs = None
        self._callback_identifier = "imageServersURLs"

    def uri(self):
        return "abstractimage/{}/imageservers.json".format(self.id)

    def __str__(self):
       return "ImageInstanceServersURL"
