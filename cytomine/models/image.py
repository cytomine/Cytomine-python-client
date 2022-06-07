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

import re
import os

from cytomine.cytomine import Cytomine, deprecated
from cytomine.models.collection import Collection
from cytomine.models.model import Model
from ._utilities import generic_image_dump


class AbstractImage(Model):
    def __init__(self, filename=None, id_uploaded_file=None, **attributes):
        super(AbstractImage, self).__init__()
        self.originalFilename = filename
        self.uploadedFile = id_uploaded_file
        self.width = None
        self.height = None
        self.depth = None
        self.duration = None
        self.channels = None

        self.physicalSizeX = None
        self.physicalSizeY = None
        self.physicalSizeZ = None
        self.fps = None
        self.bitPerSample = None
        self.samplePerPixel = None
        self.colorspace = None
        self.magnification = None

        # Read only fields
        self.path = None
        self.contentType = None
        self.zoom = None
        self.dimensions = None
        self.thumb = None
        self.preview = None

        self.populate(attributes)
        self._image_servers = None

    @deprecated
    def image_servers(self):
        if not self._image_servers:
            data = Cytomine.get_instance().get("{}/{}/imageservers.json".format(self.callback_identifier, self.id))
            self._image_servers = data["imageServersURLs"]
        return self._image_servers

    def download(self, dest_pattern="{originalFilename}", override=True, **kwargs):
        """
        Download the original image.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        def dump_url_fn(model, file_path, **kwargs):
            return "{}/{}/download".format(model.callback_identifier, model.id)

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, check_extension=False)
        return len(files) > 0

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.originalFilename)


class AbstractImageCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AbstractImageCollection, self).__init__(AbstractImage, filters, max, offset)
        self._allowed_filters = [None]  # "project"]
        self.set_parameters(parameters)


class ImageServer(Model):
    def __init__(self, name=None, url=None, available=False, base_path=None, **attributes):
        super(ImageServer, self).__init__()
        self.name = name
        self.url = url
        self.available = available
        self.base_path = base_path


class ImageServerCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageServerCollection, self).__init__(ImageServer, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class AbstractSlice(Model):
    def __init__(self, id_image=None, id_uploaded_file=None, mime=None, channel=None, z_stack=None, time=None,
                 **attributes):
        super(AbstractSlice, self).__init__()
        self.image = id_image
        self.uploadedFile = id_uploaded_file
        self.mime = mime
        self.channel = channel
        self.zStack = z_stack
        self.time = time
        self.path = None
        self.rank = None
        self.populate(attributes)


class AbstractSliceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AbstractSliceCollection, self).__init__(AbstractSlice, filters, max, offset)
        self._allowed_filters = ["abstractimage", "uploadedfile"]
        self.set_parameters(parameters)


class ImageInstance(Model):
    def __init__(self, id_abstract_image=None, id_project=None, **attributes):
        super(ImageInstance, self).__init__()
        self.baseImage = id_abstract_image
        self.project = id_project
        self.user = None
        self.originalFilename = None
        self.instanceFilename = None
        self.path = None
        self.contentType = None

        self.width = None
        self.height = None
        self.depth = None
        self.duration = None
        self.channels = None

        self.physicalSizeX = None
        self.physicalSizeY = None
        self.physicalSizeZ = None
        self.fps = None
        self.bitPerSample = None
        self.samplePerPixel = None
        self.colorspace = None
        self.magnification = None

        self.path = None
        self.contentType = None
        self.zoom = None
        self.thumb = None
        self.preview = None
        self.numberOfAnnotations = None
        self.numberOfJobAnnotations = None
        self.numberOfReviewedAnnotations = None
        self.reviewed = None
        self.populate(attributes)
        self._image_servers = None
        self._reference_slice = None

    @deprecated
    def image_servers(self):
        if not self._image_servers:
            data = Cytomine.get_instance().get("abstractimage/{}/imageservers.json".format(self.baseImage))
            self._image_servers = data["imageServersURLs"]
        return self._image_servers

    def reference_slice(self):
        if self.id is None:
            raise ValueError("Cannot get the reference slice of an image with no ID.")

        if not self._reference_slice:
            data = Cytomine.get_instance().get("imageinstance/{}/sliceinstance/reference.json".format(self.id))
            self._reference_slice = SliceInstance().populate(data) if data else False

        return self._reference_slice

    def dump(self, dest_pattern="{id}.jpg", override=True, max_size=None, bits=8, contrast=None, gamma=None,
             colormap=None, inverse=None):
        """
        Download the *reference* slice image with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists. The extension must be jpg, png or tif.
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
            raise ValueError("Cannot dump an image with no ID.")

        parameters = {
            "maxSize": max(max_size) if isinstance(max_size, tuple) else max_size,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits
        }

        def dump_url_fn(model, file_path, **kwargs):
            extension = os.path.basename(file_path).split(".")[-1]
            return "{}/{}/thumb.{}".format(model.callback_identifier, model.id, extension)

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, **parameters)

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True

    def download(self, dest_pattern="{originalFilename}", override=True, **kwargs):
        """
        Download the original image.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot download image with no ID.")

        def dump_url_fn(model, file_path, **kwargs):
            return "{}/{}/download".format(model.callback_identifier, model.id)

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, check_extension=False)
        return len(files) > 0

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.instanceFilename)

    def profile(self, x, y, width=None, height=None):
        import numpy as np
        from shapely.geometry import Point, box

        geometry = box(x, y, x + width, y + height) if (width and height) else Point(x, y)

        uri = "{}/{}/profile.json".format(self.callback_identifier, self.id)
        data = Cytomine.get_instance().get(uri, {"geometry": geometry})

        if width and height:
            data = data["collection"]
            depth = len(data[0]["profile"])
            profile = np.empty((height, width, depth), dtype=np.uint)
            for p in data:
                row = p["point"][1] - y
                col = p["point"][0] - x
                profile[row, col, :] = p["profile"]
            return profile
        else:
            return np.asarray([[data["profile"]]])

    def window(self, x, y, w, h, dest_pattern="{id}-{x}-{y}-{w}-{h}.jpg", override=True, mask=None, alpha=None,
               bits=8, annotations=None, terms=None, users=None, reviewed=None, complete=True, projection=None,
               max_size=None, zoom=None):
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
            If mask=True or alpha=True, term identifiers that must be taken into account for masking. Ignored if 'annotations' is used.
        users : list of int, optional
            If mask=True or alpha=True, user identifiers that must be taken into account for masking. Ignored if 'annotations' is used.
        reviewed : bool, optional
            If mask=True or alpha=True, indicate if only reviewed annotations mut be taken into account for masking. Ignored if 'annotations' is used.
        complete : bool, optional. Default: True
            If mask=True or alpha=True, use the annotations without simplification for masking
        projection: string, optional
            For 3D image with a profile, get the given projection (min, max, average)
        max_size : int, optional
            Maximum size (width or height) of returned image. None to get original size.
        zoom : int, optional
            Optional image zoom number

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

        if destination and not os.path.exists(destination):
            os.makedirs(destination)

        if alpha is None:
            alphamask = None
        elif alpha:
            mask = None
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
            "alphaMask": alphamask,
            "complete": complete,
            "projection": projection,
            "zoom": zoom,
            "maxSize": max(max_size) if isinstance(max_size, tuple) else max_size,
        }

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        return Cytomine.get_instance().download_file("{}/{}/window-{}-{}-{}-{}.{}".format(
            self.callback_identifier, self.id, x, y, w, h, extension), file_path, override, parameters)


class ImageInstanceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(ImageInstanceCollection, self).__init__(ImageInstance, filters, max, offset)
        self._allowed_filters = ["project", "imagegroup"]  # "user"
        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save an imageinstance collection by client.")


class SliceInstance(Model):
    def __init__(self, id_project=None, id_image=None, id_base_slice=None, **attributes):
        super(SliceInstance, self).__init__()
        self.project = id_project
        self.image = id_image
        self.baseSlice = id_base_slice
        self.imageServerUrl = None
        self.mime = None
        self.channel = None
        self.zStack = None
        self.time = None
        self.path = None
        self.rank = None

        self.filename = None  # Used to store local filename after dump on disk.
        self.filenames = None  # Used to store local filenames after dump on disk.

        self.populate(attributes)

    def dump(self, dest_pattern="{id}.jpg", override=True, max_size=None, bits=8, contrast=None, gamma=None,
             colormap=None, inverse=None):
        """
        Download the slice image with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists. The extension must be jpg, png or tif.
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
            raise ValueError("Cannot dump an image with no ID.")

        parameters = {
            "maxSize": max(max_size) if isinstance(max_size, tuple) else max_size,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits
        }

        def dump_url_fn(model, file_path, **kwargs):
            extension = os.path.basename(file_path).split(".")[-1]
            return "{}/{}/thumb.{}".format(model.callback_identifier, model.id, extension)

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, **parameters)

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True

    def window(self, x, y, w, h, dest_pattern="{id}-{x}-{y}-{w}-{h}.jpg", override=True, mask=None, alpha=None,
               bits=8, annotations=None, terms=None, users=None, reviewed=None, complete=True, max_size=None, zoom=None):
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
            If mask=True or alpha=True, term identifiers that must be taken into account for masking. Ignored if 'annotations' is used.
        users : list of int, optional
            If mask=True or alpha=True, user identifiers that must be taken into account for masking. Ignored if 'annotations' is used.
        reviewed : bool, optional
            If mask=True or alpha=True, indicate if only reviewed annotations mut be taken into account for masking. Ignored if 'annotations' is used.
        complete : bool, optional. Default: True
            If mask=True or alpha=True, use the annotations without simplification for masking
        max_size : int, optional
            Maximum size (width or height) of returned image. None to get original size.
        zoom : int, optional
            Optional image zoom number

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

        if destination and not os.path.exists(destination):
            os.makedirs(destination)

        if alpha is None:
            alphamask = None
        elif alpha:
            mask = None
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
            "alphaMask": alphamask,
            "complete": complete,
            "zoom": zoom,
            "maxSize": max(max_size) if isinstance(max_size, tuple) else max_size,
        }

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        return Cytomine.get_instance().download_file("{}/{}/window-{}-{}-{}-{}.{}".format(
            self.callback_identifier, self.id, x, y, w, h, extension), file_path, override, parameters)


class SliceInstanceCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(SliceInstanceCollection, self).__init__(SliceInstance, filters, max, offset)
        self._allowed_filters = ["imageinstance"]
        self.set_parameters(parameters)
