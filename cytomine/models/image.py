# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2024. Authors: see NOTICE file.
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

# pylint: disable=invalid-name,unused-argument

import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from cytomine.cytomine import Cytomine, deprecated
from cytomine.models.collection import Collection
from cytomine.models.model import Model

from ._utilities import generic_image_dump


class ImageServer(Model):
    def __init__(
        self,
        name: Optional[str] = None,
        url: Optional[str] = None,
        available: bool = False,
        base_path: Optional[str] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.name = name
        self.url = url
        self.available = available
        self.base_path = base_path


class ImageServerCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(ImageServer, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class AbstractImage(Model):
    def __init__(
        self,
        filename: Optional[str] = None,
        id_uploaded_file: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
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
        self._image_servers: Optional[List[ImageServer]] = None

    @deprecated
    def image_servers(self) -> Optional[List[ImageServer]]:
        if not self._image_servers:
            uri = f"{self.callback_identifier}/{self.id}/imageservers.json"
            data = Cytomine.get_instance().get(uri)
            self._image_servers = data["imageServersURLs"]  # type: ignore

        return self._image_servers

    def download(
        self,
        dest_pattern: str = "{originalFilename}",
        override: bool = True,
        **kwargs: Any,
    ) -> bool:
        """
        Download the original image.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        def dump_url_fn(model: Model, file_path: str, **kwargs: Any) -> str:
            return f"{model.callback_identifier}/{model.id}/download"

        files = generic_image_dump(
            dest_pattern,
            self,
            dump_url_fn,
            override=override,
            check_extension=False,
        )
        return len(files) > 0

    def __str__(self) -> str:
        return f"[{self.callback_identifier}] {self.id} : {self.originalFilename}"


class AbstractImageCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(AbstractImage, filters, max, offset)
        self._allowed_filters = [None]  # "project"]
        self.set_parameters(parameters)


class AbstractSlice(Model):
    def __init__(
        self,
        id_image: Optional[int] = None,
        id_uploaded_file: Optional[int] = None,
        mime: Optional[str] = None,
        channel: Optional[int] = None,
        z_stack: Optional[int] = None,
        time: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
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
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(AbstractSlice, filters, max, offset)
        self._allowed_filters = ["abstractimage", "uploadedfile"]
        self.set_parameters(parameters)


class ImageInstance(Model):
    def __init__(
        self,
        id_abstract_image: Optional[int] = None,
        id_project: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.baseImage = id_abstract_image
        self.project = id_project
        self.user = None
        self.originalFilename: Optional[str] = None
        self.instanceFilename: Optional[str] = None
        self.path: Optional[str] = None
        self.contentType: Optional[str] = None

        self.filename: Optional[str] = None
        self.filenames: Optional[List[str]] = None

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
        self.numberOfReviewedAnnotations = None
        self.reviewed = None
        self.populate(attributes)
        self._image_servers = None
        self._reference_slice: Optional[SliceInstance] = None

        self.x: Optional[int] = None
        self.y: Optional[int] = None
        self.w: Optional[int] = None
        self.h: Optional[int] = None

    @deprecated
    def image_servers(self) -> Any:
        if not self._image_servers:
            data = Cytomine.get_instance().get(
                f"abstractimage/{self.baseImage}/imageservers.json"
            )
            self._image_servers = data["imageServersURLs"]  # type: ignore
        return self._image_servers

    def reference_slice(self) -> Optional[Union[bool, "SliceInstance"]]:
        if self.id is None:
            raise ValueError("Cannot get the reference slice of an image with no ID.")

        if not self._reference_slice:
            data = Cytomine.get_instance().get(
                f"imageinstance/{self.id}/sliceinstance/reference.json"
            )
            if not isinstance(data, dict):
                return False

            self._reference_slice = SliceInstance().populate(data)  # type: ignore

        return self._reference_slice

    def dump(
        self,
        dest_pattern: str = "{id}.jpg",
        override: bool = True,
        max_size: Optional[Union[int, Tuple[int, ...]]] = None,
        bits: int = 8,
        contrast: Optional[float] = None,
        gamma: Optional[float] = None,
        colormap: Optional[int] = None,
        inverse: Optional[bool] = None,
    ) -> bool:
        """
        Download the *reference* slice image with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
            The extension must be jpg, png or tif.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        max_size : int, tuple, optional
            Maximum size (width or height) of returned image. None to get original size.
        bits : int (8,16,32) or str ("max"), optional
            Bit depth (bit per channel) of returned image.
            "max" returns the original image bit depth
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
            True if everything happens correctly, False otherwise.
            As a side effect, object attribute "filename"
            is filled with downloaded file path.
        """
        if self.id is None:
            raise ValueError("Cannot dump an image with no ID.")

        parameters: Dict[str, Any] = {
            "maxSize": max(max_size) if isinstance(max_size, tuple) else max_size,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits,
        }

        def dump_url_fn(model: Model, file_path: str, **kwargs: Any) -> str:
            extension = os.path.basename(file_path).split(".")[-1]
            return f"{model.callback_identifier}/{model.id}/thumb.{extension}"

        files = generic_image_dump(
            dest_pattern,
            self,
            dump_url_fn,
            override=override,
            **parameters,
        )

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True

    def download(
        self,
        dest_pattern: str = "{originalFilename}",
        override: bool = True,
        **kwargs: Any,
    ) -> bool:
        """
        Download the original image.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise.
        """
        if self.id is None:
            raise ValueError("Cannot download image with no ID.")

        def dump_url_fn(model: Model, file_path: str, **kwargs: Any) -> str:
            return f"{model.callback_identifier}/{model.id}/download"

        files = generic_image_dump(
            dest_pattern,
            self,
            dump_url_fn,
            override=override,
            check_extension=False,
        )
        return len(files) > 0

    def __str__(self) -> str:
        return f"[{self.callback_identifier}] {self.id} : {self.instanceFilename}"

    def window(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        dest_pattern: str = "{id}-{x}-{y}-{w}-{h}.jpg",
        override: bool = True,
        mask: Optional[bool] = None,
        alpha: Optional[bool] = None,
        bits: int = 8,
        annotations: Optional[List[int]] = None,
        terms: Optional[List[int]] = None,
        users: Optional[List[int]] = None,
        reviewed: Optional[bool] = None,
        complete: bool = True,
        projection: Optional[str] = None,
        max_size: Optional[Union[int, Tuple[int, ...]]] = None,
        zoom: Optional[int] = None,
    ) -> bool:
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
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        mask : bool, optional
            True if a binary mask based on given annotations must be returned,
            False otherwise.
        alpha : bool, optional
            True if image background (outside annotations) must be transparent,
            False otherwise.
        bits : int (8/16/32), optional
            Optional output bit depth of returned images
        annotations : list of int, optional
            If mask or alpha is True, annotation ids that must be taken into account for masking
        terms : list of int, optional
            If mask or alpha is True, term ids that must be taken into account for masking.
            Ignored if 'annotations' is used.
        users : list of int, optional
            If mask or alpha is True, user ids that must be taken into account for masking.
            Ignored if 'annotations' is used.
        reviewed : bool, optional
            If mask or alpha is True, specify if only reviewed annotations are used for masking.
            Ignored if 'annotations' is used.
        complete : bool, optional. Default: True
            If mask or alpha is True, use the annotations without simplification for masking
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
        dest_pattern = re.sub(
            pattern,
            lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")),
            dest_pattern,
        )
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
            mask = str(mask).lower()  # type: ignore

        if alphamask is not None:
            alphamask = str(alphamask).lower()  # type: ignore
        # ===

        parameters = {
            "annotations": (
                ",".join(str(item) for item in annotations) if annotations else None
            ),
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

        file_path = os.path.join(destination, f"{filename}.{extension}")

        return Cytomine.get_instance().download_file(
            f"{self.callback_identifier}/{self.id}/window-{x}-{y}-{w}-{h}.{extension}",
            file_path,
            override,
            parameters,
        )


class ImageInstanceCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(ImageInstance, filters, max, offset)
        self._allowed_filters = ["project", "imagegroup"]  # "user"
        self.set_parameters(parameters)

    def save(self, *args: Any, **kwargs: Any) -> Union[bool, Collection]:
        raise NotImplementedError("Cannot save an imageinstance collection by client.")


class SliceInstance(Model):
    def __init__(
        self,
        id_project: Optional[int] = None,
        id_image: Optional[int] = None,
        id_base_slice: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
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

        # Used to store local filename(s) after dump on disk.
        self.filename: Optional[str] = None
        self.filenames: Optional[List[str]] = None

        self.x: Optional[int] = None
        self.y: Optional[int] = None
        self.w: Optional[int] = None
        self.h: Optional[int] = None

        self.populate(attributes)

    def dump(
        self,
        dest_pattern: str = "{id}.jpg",
        override: bool = True,
        max_size: Optional[Union[int, Tuple[int, ...]]] = None,
        bits: int = 8,
        contrast: Optional[float] = None,
        gamma: Optional[float] = None,
        colormap: Optional[int] = None,
        inverse: Optional[bool] = None,
    ) -> bool:
        """
        Download the slice image with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
            The extension must be jpg, png or tif.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        max_size : int, tuple, optional
            Maximum size (width or height) of returned image. None to get original size.
        bits : int (8,16,32) or str ("max"), optional
            Bit depth (bit per channel) of returned image.
            "max" returns the original image bit depth
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
            True if everything happens correctly, False otherwise.
            As a side effect, object attribute "filename"
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
            "bits": bits,
        }

        def dump_url_fn(model: Model, file_path: str, **kwargs: Any) -> str:
            extension = os.path.basename(file_path).split(".")[-1]
            return f"{model.callback_identifier}/{model.id}/thumb.{extension}"

        files = generic_image_dump(
            dest_pattern,
            self,
            dump_url_fn,
            override=override,
            **parameters,  # type: ignore
        )

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True

    def window(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        dest_pattern: str = "{id}-{x}-{y}-{w}-{h}.jpg",
        override: bool = True,
        mask: Optional[bool] = None,
        alpha: Optional[bool] = None,
        bits: int = 8,
        annotations: Optional[List[int]] = None,
        terms: Optional[List[int]] = None,
        users: Optional[List[int]] = None,
        reviewed: Optional[bool] = None,
        complete: bool = True,
        max_size: Optional[Union[int, Tuple[int, ...]]] = None,
        zoom: Optional[int] = None,
    ) -> bool:
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
            Destination path for the downloaded image.
            "{X}" patterns are replaced by the value of X attribute if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        mask : bool, optional
            True if a binary mask based on given annotations must be returned, False otherwise.
        alpha : bool, optional
            True if image background (outside annotations) must be transparent, False otherwise.
        bits : int (8/16/32), optional
            Optional output bit depth of returned images
        annotations : list of int, optional
            If mask or alpha is True, annotation ids that must be taken into account for masking
        terms : list of int, optional
            If mask or alpha is True, term ids that must be taken into account for masking.
            Ignored if 'annotations' is used.
        users : list of int, optional
            If mask or alpha is True, user ids that must be taken into account for masking.
            Ignored if 'annotations' is used.
        reviewed : bool, optional
            If mask or alpha is True, only reviewed annotations should be used for masking.
            Ignored if 'annotations' is used.
        complete : bool, optional. Default: True
            If mask or alpha is True, use the annotations without simplification for masking
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
        dest_pattern = re.sub(
            pattern,
            lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")),
            dest_pattern,
        )
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
            mask = str(mask).lower()  # type: ignore

        if alphamask is not None:
            alphamask = str(alphamask).lower()  # type: ignore
        # ===

        parameters = {
            "annotations": (
                ",".join(str(item) for item in annotations) if annotations else None
            ),
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

        file_path = os.path.join(destination, f"{filename}.{extension}")

        return Cytomine.get_instance().download_file(
            f"{self.callback_identifier}/{self.id}/window-{x}-{y}-{w}-{h}.{extension}",
            file_path,
            override,
            parameters,
        )


class SliceInstanceCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(SliceInstance, filters, max, offset)
        self._allowed_filters = ["imageinstance"]
        self.set_parameters(parameters)
