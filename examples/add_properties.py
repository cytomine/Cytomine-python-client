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
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models import Annotation, ImageInstance, Project, Property

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

    parser.add_argument('--key', help="the property key")
    parser.add_argument('--value', help="the property value")

    parser.add_argument('--cytomine_id_project', dest='id_project', required=False,
                        help="The project to which the property will be added (optional)")
    parser.add_argument('--cytomine_id_image_instance', dest='id_image_instance', required=False,
                        help="The image to which the property will be added (optional)")
    parser.add_argument('--cytomine_id_annotation', dest='id_annotation', required=False,
                        help="The annotation to which the property will be added (optional)")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        obj = None

        if params.id_project:
            obj = Project().fetch(params.id_project)
            prop = Property(obj, key=params.key, value=params.value).save()
            print(prop)

        if params.id_image_instance:
            obj = ImageInstance().fetch(params.id_image_instance)
            prop = Property(obj, key=params.key, value=params.value).save()
            print(prop)

        if params.id_annotation:
            obj = Annotation().fetch(params.id_annotation)
            prop = Property(obj, key=params.key, value=params.value).save()
            print(prop)
            
        # Get the property from the API using property ID
        fetched_prop = Property(obj).fetch(prop.id)
        print(fetched_prop)
        
        # Get the property from the API using property key
        fetched_prop = Property(obj).fetch(key=params.key)
        print(fetched_prop)

        """
        You can add property to any Cytomine domain.
        You can also attach a file (see AttachedFile) or add a description (see Description) to any Cytomine domain.
        """
