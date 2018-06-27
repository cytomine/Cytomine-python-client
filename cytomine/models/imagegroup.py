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

import re
import os

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model

import numpy as np


class ImageGroup(Model):
    def __init__(self, name=None, id_project=None, **attributes):
        super(ImageGroup, self).__init__()
        self.name = name
        self.project = id_project
        self.populate(attributes)

    def characteristics(self):
        uri = "imagegroup/{}/characteristics.json".format(self.id)
        return Cytomine.get_instance().get(uri)

    def download(self, dest_pattern="{name}", override=True, parent=False):
        """
        Download the original image.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        parent : bool, optional
            True to download image parent if the image is a part of a multidimensional file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot download file with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        parameters = {"parent": parent}

        destination = os.path.dirname(dest_pattern)
        if not os.path.exists(destination):
            os.makedirs(destination)

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     dest_pattern, override, parameters)


class ImageGroupCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageGroupCollection, self).__init__(ImageGroup, filters, max, offset)
        self._allowed_filters = ["project"]
        self.set_parameters(parameters)


class ImageGroupHDF5(Model):
    def __init__(self, id_group=None, filename=None, **attributes):
        super(ImageGroupHDF5, self).__init__()
        self.group = id_group
        self.groupName = None
        self.filename = filename
        self.progress = None
        self.status = None
        self.populate(attributes)

    @property
    def callback_identifier(self):
        return "imagegroupHDF5"

    def pixel(self, x, y):
        uri = "imagegroupHDF5/{}/{}/{}/pixel.json".format(self.id, x, y)
        return np.asarray([[Cytomine.get_instance().get(uri)["spectra"]]])

    def rectangle(self, x, y, width, height):
        uri = "imagegroupHDF5/{}/{}/{}/{}/{}/rectangle.json".format(self.id, x, y, width, height)
        collection = Cytomine.get_instance().get(uri)["collection"]
        spectrum = np.array([data["spectra"] for data in collection])
        spectrum = np.expand_dims(spectrum, axis=1)
        _, _, depth = spectrum.shape
        return spectrum.reshape((width, height, depth))


# class ImageGroupHDF5Collection(Collection):
#     def __init__(self, filters=None, max=0, offset=0, **parameters):
#         super(ImageGroupHDF5Collection, self).__init__(ImageGroupHDF5, filters, max, offset)
#         self._allowed_filters = ["project"]
#         self.set_parameters(parameters)
#
#     @property
#     def callback_identifier(self):
#         return "imagegroupHDF5"


class ImageSequence(Model):
    def __init__(self, id_image_group=None, id_image_instance=None, z_stack=None,
                 slice=None, time=None, channel=None, **attributes):
        super(ImageSequence, self).__init__()
        self.imageGroup = id_image_group
        self.image = id_image_instance
        self.zStack = z_stack
        self.slice = slice
        self.time = time
        self.channel = channel
        self.model = None
        self.populate(attributes)

    def __str__(self):
        return "[{}] {} : Group {} - Image {} {}/{}/{}/{} ".format(self.callback_identifier,
                                                                   self.id, self.imageGroup, self.image,
                                                                   self.channel, self.zStack, self.slice, self.time)


class ImageSequenceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageSequenceCollection, self).__init__(ImageSequence, filters, max, offset)
        self._allowed_filters = ["imagegroup", "imageinstance"]
        self.set_parameters(parameters)
