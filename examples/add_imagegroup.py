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

import logging
import re
import sys
from argparse import ArgumentParser

import os

from cytomine import Cytomine
from cytomine.models import ImageSequence, ImageGroup
from cytomine.models.image import ImageInstanceCollection

__author__ = "Rubens Ulysse <urubens@uliege.be>"

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

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key,
                  verbose=logging.INFO) as cytomine:
        image_instances = ImageInstanceCollection().fetch_with_filter("project", params.id_project)
        print(image_instances)

        # This script will create an image group from image instances in the specified project.
        # The position of the image in the group is inferred from its filename.
        # The following patterns are supported:
        # For time: -t123 / -T123 / _t123 / _T123
        # For channel: -c123 / -C123 / _c123 / _C123
        # For z stack: -z123 / -Z123 / _z123 / _Z123
        # Triplets (Z, C, T) must be unique.

        # Examples:
        # myfile-z1-c2-t3.png => image in position Z=1, C=2, T=3
        # otherfile-c3.jpg => image in position Z=0, C=3, T=0

        patterns = {
            "z": re.compile("[-_]z[0-9]*"),
            "c": re.compile("[-_]c[0-9]*"),
            "t": re.compile("[-_]t[0-9]*")
        }

        group = ImageGroup(name=params.group_name, id_project=params.cytomine_id_project).save()

        for image in image_instances:
            print("Image ID: {} | Width: {} | Height: {} | Filename: {}".format(
                image.id, image.width, image.height, image.filename))

            sequence = {}
            for dimension in ["z", "c", "t"]:
                match = re.findall(patterns[dimension], image.instanceFilename.lower())
                sequence[dimension] = match[0][2:] if len(match) > 0 and len(match[0]) > 2 else 0

            print(sequence)
            image_sequence = ImageSequence(group.id, image.id, z_stack=sequence["z"], channel=sequence["c"],
                                           time=sequence["t"]).save()
            print(image_sequence)

