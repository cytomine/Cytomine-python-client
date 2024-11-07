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

logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    from cytomine import Cytomine
    from cytomine.models.user import *

    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine
    parser.add_argument('--cytomine_host', dest='host',
                        default='demo.cytomine.be', help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key',
                        help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key',
                        help="The Cytomine private key")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        # Get the list of existing users
        users = UserCollection().fetch()
        print(users)
        for user in users:
            print(user)

        # Create a new user and add it to database
        new_user = User("jdoe", "John", "Doe", "jdoe@mail.com", "123456").save()
        print(new_user)

        # Get the list of existing users, updated with jdoe.
        users.fetch()
        print(users)
        for user in users:
            print(user)

        # Update user
        new_user.email = "jdoe@mail.net"
        new_user.update()

        # Delete user
        new_user.delete()
