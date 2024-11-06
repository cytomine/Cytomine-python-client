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

import os

from shapely import wkt
from shapely.affinity import affine_transform

from cytomine import Cytomine
from cytomine.models import AnnotationCollection, ImageInstanceCollection




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

    # Download path
    parser.add_argument('--download_path', required=False,
                        help="Where to store annotation crops. "
                             "It is only required if you want Cytomine generate annotation crops.")

    # Show coordinates using OpenCV coordinate system.
    parser.add_argument('--opencv', dest='opencv', action='store_true',
                        help="Print the annotation geometry using OpenCV coordinate system for points.")

    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:

        if params.opencv:
            image_instances = ImageInstanceCollection().fetch_with_filter("project", params.id_project)

        # We want all annotations in a given project.
        annotations = AnnotationCollection()
        annotations.project = params.id_project  # Add a filter: only annotations from this project
        # You could add other filters:
        # annotations.image = id_image => Add a filter: only annotations from this image
        # annotations.images = [id1, id2] => Add a filter: only annotations from these images
        # annotations.user = id_user => Add a filter: only annotations from this user
        # ...
        annotations.showWKT = True  # Ask to return WKT location (geometry) in the response
        annotations.showMeta = True  # Ask to return meta information (id, ...) in the response
        annotations.showGIS = True  # Ask to return GIS information (perimeter, area, ...) in the response
        # ...
        # => Fetch annotations from the server with the given filters.
        annotations.fetch()
        print(annotations)

        for annotation in annotations:
            print(
                f"ID: {annotation.id} | "
                f"Image: {annotation.image} | "
                f"Project: {annotation.project} | "
                f"Term: {annotation.term} | "
                f"User: {annotation.user} | "
                f"Area: {annotation.area} | "
                f"Perimeter: {annotation.perimeter} | "
                f"WKT: {annotation.location}"
            )

            # Annotation location is the annotation geometry in WKT format.
            # See https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry

            # You can use Shapely library to read geometry in WKT format. See https://shapely.readthedocs.io/en/latest/
            # See 'shapely.wkt.loads(wkt)' function in Shapely library.
            geometry = wkt.loads(annotation.location)
            print(f"Geometry from Shapely: {geometry}")

            # In Cytomine, geometries are referenced using a cartesian coordinate system !
            # See 'shapely.affinity.affine_transform(geom, matrix)' function in Shapely library if needed
            if params.opencv:
                # In OpenCV, the y-axis is reversed for points. (https://stackoverflow.com/a/47510950)
                # x' = ax + by + x_off => x' = x
                # y' = dx + ey + y_off => y' = -y + image.height
                # matrix = [a, b, d, e, x_off, y_off]
                image = get_by_id(image_instances, annotation.image)
                geometry_opencv = affine_transform(geometry, [1, 0, 0, -1, 0, image.height])
                print(f"Geometry with OpenCV coordinate system: {geometry_opencv}")

            if params.download_path:
                # max_size is set to 512 (in pixels). Without max_size parameter, it download a dump of the same size that the annotation.
                # Dump a rectangular crop containing the annotation
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "crop", "{id}.jpg"), max_size=512)
                # Dumps a rectangular mask containing the annotation
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "mask", "{id}.jpg"), mask=True, max_size=512)
                # Dumps the annotation crop where pixels oustide it are transparent.
                annotation.dump(dest_pattern=os.path.join(params.download_path, "{project}", "alpha", "{id}.png"), mask=True, alpha=True, max_size=512)
