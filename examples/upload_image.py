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
from cytomine.models import Project, StorageCollection, UploadedFile

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
    parser.add_argument('--cytomine_id_project', dest='id_project', required=False,
                        help="The project from which we want the images (optional)")
    parser.add_argument('--filepath', dest='filepath',
                        help="The filepath (on your file system) of the file you want to upload")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:

        # Check that the file exists on your file system
        if not os.path.exists(params.filepath):
            raise ValueError("The file you want to upload does not exist")

        # Check that the given project exists
        if params.id_project:
            project = Project().fetch(params.id_project)
            if not project:
                raise ValueError("Project not found")

        # To upload the image, we need to know the ID of your Cytomine storage.
        storages = StorageCollection().fetch()
        my_storage = next(filter(lambda storage: storage.user == cytomine.current_user.id, storages))
        if not my_storage:
            raise ValueError("Storage not found")

        uploaded_file = cytomine.upload_image(filename=params.filepath,
                                              id_storage=my_storage.id,
                                              id_project=params.id_project)

        print(uploaded_file)
