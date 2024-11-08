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

import os
from shutil import copyfile

from cytomine import Cytomine

from .parallel import makedirs
from .pattern_matching import resolve_pattern


class DumpError(Exception):
    """A class for image dump errors"""


def generic_image_dump(
    dest_pattern,
    model,
    url_fn,
    override=True,
    check_extension=True,
    **parameters,
):
    """A generic function for 'dumping' a model as an image (crop, windows,...).
    Parameters
    ----------
    dest_pattern: str
        The destination pattern for the image.
    model: Model
        A Cytomine model
    url_fn: callable
        A function for generating the url of the image.
        The function call would be like the following: url_fn(model, file_path, **parameters)
        where model is the cytomine model,
        file_path is the destination filepath and paramters are the dump parameters.
    override: bool
        True for overriding the file. False
    check_extension: bool
        True if the extension must be internally validated
    parameters: dict

    Returns
    -------
    downloaded: iterable
        The list of downloaded files

    Raises
    ------
    DumpError:
        When the download fails.
    """
    # generate download path(s)
    files_to_download = []
    for file_path in resolve_pattern(dest_pattern, model):
        destination = os.path.dirname(file_path)
        filename, extension = os.path.splitext(os.path.basename(file_path))
        extension = extension[1:]

        if check_extension and extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        if destination:
            makedirs(destination, exist_ok=True)
        files_to_download.append(os.path.join(destination, f"{filename}.{extension}"))

    if len(files_to_download) == 0:
        raise ValueError("Couldn't generate a dump path.")

    # download once
    file_path = files_to_download[0]
    url = url_fn(model, file_path, **parameters)

    if not Cytomine.get_instance().download_file(url, file_path, override, parameters):
        raise DumpError("Could not dump the image.")

    # copy the file to the other paths (if any)
    for dest_file_path in files_to_download[1:]:
        if override or not os.path.isfile(dest_file_path):
            copyfile(file_path, dest_file_path)

    return files_to_download
