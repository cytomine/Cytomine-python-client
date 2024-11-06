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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models import ImageInstance, Tag, TagDomainAssociation, TagDomainAssociationCollection



logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine
    parser.add_argument('--cytomine_host', dest='host',
                        help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key',
                        help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key',
                        help="The Cytomine private key")

    parser.add_argument('--cytomine_id_image_instance', dest='id_image_instance',
                        help="The image to which the tag will be added")
    parser.add_argument('--cytomine_id_tag', dest='id_tag',
                        help="The tag that will be added to the image")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        image = ImageInstance().fetch(params.id_image_instance)
        tag = Tag().fetch(params.id_tag)

        tda = TagDomainAssociation(object=image, tag=tag.id).save()

        # Get the list of tags for the image:
        print(f"Image {image.instanceFilename} has tags:")
        tdac = TagDomainAssociationCollection(object=image).fetch()
        for tda in tdac:
            print(f"- {tda.tagName}")
