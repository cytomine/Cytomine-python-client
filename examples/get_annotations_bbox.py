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

from shapely import wkt

from cytomine import Cytomine
from cytomine.models import *

__author__ = "Rubens Ulysse <urubens@uliege.be>"


def get_by_id(haystack, needle):
    return next((item for item in haystack if item.id == needle), None)


logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine connection parameters
    parser.add_argument('--cytomine_host', dest='host',
                        default='demo.cytomine.be', help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key',
                        help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key',
                        help="The Cytomine private key")

    # Cytomine project ID
    parser.add_argument('--cytomine_id_project', dest='id_project',
                        help="The project from which we want the annotations")

    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:

        project = Project().fetch(params.id_project)
        image_instances = ImageInstanceCollection().fetch_with_filter("project", params.id_project)
        terms = TermCollection().fetch_with_filter("project", params.id_project)

        # We want all annotations in a given project.
        annotations = AnnotationCollection()
        annotations.project = params.id_project  # Add a filter: only annotations from this project
        annotations.showWKT = True  # Ask to return WKT location (geometry) in the response
        annotations.showMeta = True  # Ask to return meta information (id, ...) in the response
        annotations.showGIS = True  # Ask to return GIS information (perimeter, area, ...) in the response
        annotations.showTerm = True
        annotations.fetch()  # => Fetch annotations from the server with the given filters.

        for annotation in annotations:
            # Find the image instance object related to the current annotation
            annot_image = get_by_id(image_instances, annotation.image)

            # Find the term objects related to the current annotation
            # An annotation can have 0, 1 or several terms so list is used
            annot_terms = [get_by_id(terms, t) for t in annotation.term]

            # Get the annotation geometry as a Shapely object (https://shapely.readthedocs.io/en/latest/manual.html)
            geometry = wkt.loads(annotation.location)
            bbox = geometry.bounds  # See https://shapely.readthedocs.io/en/latest/manual.html#object.bounds
            print(
                f"ID: {annotation.id} | "
                f"Image: {annot_image.originalFilename} | "
                f"Project: {project.name} | "
                f"Terms: {[t.name for t in annot_terms]} | "
                f"Area: {annotation.area} | "
                f"Perimeter: {annotation.perimeter} | "
                f"Bbox: {bbox}"
            )
