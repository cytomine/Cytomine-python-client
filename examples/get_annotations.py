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
import sys
from argparse import ArgumentParser

import os

from cytomine import Cytomine
from cytomine.models import AnnotationCollection

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
                        help="The project from which we want the crop")
    parser.add_argument('--download_path', required=False,
                        help="Where to store images")
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key,
                  verbose=logging.INFO) as cytomine:
        annotations = AnnotationCollection()
        annotations.project = params.id_project
        annotations.showWKT = True
        annotations.showMeta = True
        annotations.showGIS = True
        annotations.fetch()
        print(annotations)

        if params.download_path:
            f= open(params.download_path+"/"+params.id_project+".csv","w+")
            f.write("ID;Image;Project;Term;User;Area;Perimeter;WKT \n")
            for annotation in annotations:
                f.write("{};{};{};{};{};{};{};{}\n".format(annotation.id,annotation.image,annotation.project,annotation.term,annotation.user,annotation.area,annotation.perimeter,annotation.location))

        for annotation in annotations:
            print("ID: {} | Image: {} | Project: {} | Term: {} | User: {} | Area: {} | Perimeter: {} | WKT: {}".format(
                annotation.id,
                annotation.image,
                annotation.project,
                annotation.term,
                annotation.user,
                annotation.area,
                annotation.perimeter,
                annotation.location
            ))

            if params.download_path:
                # max_size is set to 512 (in pixels). Without max_size parameter, it download a dump of the same size that the annotation.
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "crop", "{id}.jpg"), max_size = 512)
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "mask", "{id}.jpg"), mask=True, max_size = 512)
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "alpha", "{id}.png"), mask=True, alpha=True, max_size = 512)
