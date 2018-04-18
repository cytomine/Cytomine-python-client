# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2017. Authors: see NOTICE file.
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

from __future__ import print_function
from cytomine import *

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__copyright__ = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"


cytomine_domain = {
    "project": "be.cytomine.project.Project",
    "abstractImage": "be.cytomine.image.AbstractImage",
    "imageInstance": "be.cytomine.image.ImageInstance",
    "userAnnotation": "be.cytomine.ontology.UserAnnotation",
    "algoAnnotation": "be.cytomine.ontology.AlgoAnnotation",
    "imageGroup": "be.cytomine.image.multidim.ImageGroup"
}


# Example 1: Get information about an attached file
def example1(conn):
    id_attached_file = 0
    attached_file = conn.get_attached_file(id_attached_file)
    print(attached_file)


# Example 2: Get info & download an attached file
def example2(conn):
    id_attached_file = 0
    destination_path = "/tmp/example.txt"
    override = False
    attached_file = conn.get_and_download_attached_file(id_attached_file, destination_path, override)
    print(attached_file)


# Example 3: Get the list of attached files for a specific project
def example3(conn):
    domain_name = cytomine_domain["project"]
    domain_id = 0
    attached_files = conn.get_attached_files(domain_name, domain_id)
    for af in attached_files.data():
        print(af)


# Example 4: Add and upload a new attached file
def example4(conn):
    filename = "/tmp/example.txt"
    domain_name = cytomine_domain["project"]
    domain_id = 0
    attached_file = conn.add_and_upload_attached_file(filename, domain_name, domain_id)
    print(attached_file)


if __name__ == '__main__':
    # Replace connection XXX parameters
    cytomine_host = "XXX"
    cytomine_public_key = "XXX"
    cytomine_private_key = "XXX"

    # Connection to Cytomine Core
    conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key,
                    base_path='/api/', working_path='/tmp/', verbose=True)

    example1(conn)
