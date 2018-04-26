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
            True to download image parent if the abstract image is a part of a multidimensional file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        parameters = {"parent": parent}

        destination = os.path.dirname(dest_pattern)
        if not os.path.exists(destination):
            os.makedirs(destination)

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     dest_pattern, override, parameters)

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.filename)


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
            raise ValueError("Cannot download image with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        parameters = {"parent": parent}

        destination = os.path.dirname(dest_pattern)
        if not os.path.exists(destination):
            os.makedirs(destination)

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     dest_pattern, override, parameters)

    def dump(self, dest_pattern="{id}.jpg", override=True, max_size=None, bits=8, contrast=None, gamma=None,
             colormap=None, inverse=None):
        """
        Download the image with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        max_size : int, tuple, optional
            Maximum size (width or height) of returned image. None to get original size.
        bits : int (8,16,32) or str ("max"), optional
            Bit depth (bit per channel) of returned image. "max" returns the original image bit depth
        contrast : float, optional
            Optional contrast applied on returned image.
        gamma : float, optional
            Optional gamma applied on returned image.
        colormap : int, optional
            Cytomine identifier of a colormap to apply on returned image.
        inverse : bool, optional
            True to inverse color mapping, False otherwise.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise. As a side effect, object attribute "filename"
            is filled with downloaded file path.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)

        destination = os.path.dirname(dest_pattern)
        filename, extension = os.path.splitext(os.path.basename(dest_pattern))
        extension = extension[1:]

        if extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        if not os.path.exists(destination):
            os.makedirs(destination)

        if isinstance(max_size, tuple) or max_size is None:
            max_size = max(self.width, self.height)

        parameters = {
            "maxSize": max_size,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits
        }

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        url = self.preview[:self.preview.index("?")]
        url = url.replace(".png", ".{}".format(extension))
        result = Cytomine.get_instance().download_file(url, file_path, override, parameters)
        if result:
            self.filename = file_path
        return result

    def window(self, x, y, w, h, dest_pattern="{id}-{x}-{y}-{w}-{h}.jpg", override=True, mask=None, alpha=None,
               bits=8, annotations=None, terms=None, users=None, reviewed=None):
        """
        Extract a window (rectangle) from an image and download it.

        Parameters
        ----------
        x : int
            The X position of window top-left corner. 0 is image left.
        y : int
            The Y position of window top-left corner. 0 is image top.
        w : int
            The window width
        h : int
            The window height
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        mask : bool, optional
            True if a binary mask based on given annotations must be returned, False otherwise.
        alpha : bool, optional
            True if image background (outside annotations) must be transparent, False otherwise.
        bits : int (8/16/32), optional
            Optional output bit depth of returned images
        annotations : list of int, optional
            If mask=True or alpha=True, annotation identifiers that must be taken into account for masking
        terms : list of int, optional
            If mask=True or alpha=True, term identifiers that must be taken into account for masking
        users : list of int, optional
            If mask=True or alpha=True, user identifiers that must be taken into account for masking
        reviewed : bool, optional
            If mask=True or alpha=True, indicate if only reviewed annotations mut be taken into account for masking

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)
        del self.x
        del self.y
        del self.w
        del self.h

        destination = os.path.dirname(dest_pattern)
        filename, extension = os.path.splitext(os.path.basename(dest_pattern))
        extension = extension[1:]

        if extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        if not os.path.exists(destination):
            os.makedirs(destination)

        if mask is None and alpha is None:
            alphamask = None
        elif mask and alpha:
            alphamask = True
            if extension == "jpg":
                extension = "png"
        else:
            alphamask = False

        # Temporary fix due to Cytomine-core
        if mask is not None:
            mask = str(mask).lower()

        if alphamask is not None:
            alphamask = str(alphamask).lower()
        # ===

        parameters = {
            "annotations": ",".join(str(item) for item in annotations) if annotations else None,
            "terms": ",".join(str(item) for item in terms) if terms else None,
            "users": ",".join(str(item) for item in users) if users else None,
            "reviewed": reviewed,
            "bits": bits,
            "mask": mask,
            "alphaMask": alphamask
        }

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        return Cytomine.get_instance().download_file("{}/{}/window-{}-{}-{}-{}.{}".format(
            self.callback_identifier, self.id, x, y, w, h, extension), file_path, override, parameters)

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.filename)


class ImageInstanceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageInstanceCollection, self).__init__(ImageInstance, filters, max, offset)
        self._allowed_filters = ["project"]  # "user"
        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save an imageinstance collection by client.")
