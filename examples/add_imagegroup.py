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

import logging
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models import ImageGroup, ImageGroupImageInstance
from cytomine.models.image import ImageInstanceCollection

__author__ = "Rubens Ulysse <urubens@uliege.be>"

from models import ImageGroupCollection

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
    parser.add_argument('--group_name', help="Name of the future image group", default="GROUP")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        image_instances = ImageInstanceCollection().fetch_with_filter("project", params.id_project)
        print(image_instances)

        # This script will create an image group from image instances in the specified project.
        group = ImageGroup(name=params.group_name, id_project=params.id_project).save()

        # It adds the 3 first images of the project into the image group as example
        for image in image_instances[:3]:
            print(
                f"Image ID: {image.id} | "
                f"Width: {image.width} | "
                f"Height: {image.height} | "
                f"Filename: {image.filename}"
            )
            igii = ImageGroupImageInstance(group.id, image.id).save()
            print(igii)

        # We list all image groups in the project
        image_groups = ImageGroupCollection().fetch_with_filter("project", params.id_project)
        for image_group in image_groups:
            print(f"Group {image_group.id} has name {image_group.name} and following images: ")
            for image in ImageInstanceCollection().fetch_with_filter("imagegroup", image_group.id):
                print(f" * {image.filename}")
