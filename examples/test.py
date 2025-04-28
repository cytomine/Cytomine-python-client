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

# * This script is just a simple example used to verify if the 
# * Cytomine Python Client is correctly installed.
# * Using a correct Cytomine instance URL, and keys of a user, it will just fetch his username.

import sys
from argparse import ArgumentParser

if __name__ == '__main__':
    from cytomine import Cytomine
    from cytomine.models.user import *

    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine
    parser.add_argument('--cytomine_host', dest='host', default='demo.cytomine.be', help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key', help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key', help="The Cytomine private key")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        # Get the connected user
        user = CurrentUser().fetch()
        print(user)