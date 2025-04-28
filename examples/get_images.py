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

import logging
import os
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models.image import ImageInstanceCollection

# This example script allows you to get the list of images (metadata) in a given project.
# If a download path is provided, it downloads all original images like they have been uploaded to Cytomine.

logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine
    parser.add_argument('--cytomine_host', dest='host',
                        default='demo.cytomine.be', help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key',
                        help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key',
                        help="The Cytomine private key")
    parser.add_argument('--cytomine_id_project', dest='id_project',
                        help="The project from which we want the images")
    parser.add_argument('--download_path', required=False,
                        help="Where to store images")
    params, other = parser.parse_known_args(sys.argv[1:])

    if params.download_path:
        original_path = os.path.join(params.download_path, "original")
        dump_path = os.path.join(params.download_path, "dump")

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        image_instances = ImageInstanceCollection().fetch_with_filter("project", params.id_project)
        print(image_instances)

        if params.download_path:
            f = open(params.download_path + "images-" + params.id_project + ".csv", "w+")
            f.write("ID;Width;Height;Resolution;Magnification;Filename \n")
            for image in image_instances:
                f.write(
                    f"{image.id};"
                    f"{image.width};"
                    f"{image.height};"
                    f"{image.physicalSizeX};"
                    f"{image.magnification};"
                    f"{image.filename}\n"
                )

        for image in image_instances:
            print(
                f"Image ID: {image.id} | "
                f"Width: {image.width} | "
                f"Height: {image.height} | "
                f"Resolution: {image.physicalSizeX} | "
                f"Magnification: {image.magnification} | "
                f"Filename: {image.filename}"
            )

            if params.download_path:
                # We will dump the images in a specified /dump directory. Filename fo this dump will be the original
                # file name with an added .jpg extension max_size is set to 512 (in pixels) by default. Without
                # max_size it download a dump of the same size that the original image.
                image.dump(os.path.join(dump_path, str(params.id_project), "{originalFilename}.jpg"), max_size=512)
                # To download the original files that have been uploaded to Cytomine
                image.download(os.path.join(original_path, str(params.id_project), "{originalFilename}"))
