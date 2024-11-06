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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import sys
from argparse import ArgumentParser

from shapely.geometry import Point, box

from cytomine import Cytomine
from cytomine.models import Annotation, AnnotationCollection, \
    ImageGroupImageInstanceCollection, AnnotationGroup, AnnotationLink

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

    parser.add_argument('--cytomine_id_project', dest='id_project',
                        help="The project from which we want the images")
    parser.add_argument('--cytomine_id_image_instance1', dest='id_image_instance1',
                        help="The image to which the annotation will be added"),
    parser.add_argument('--cytomine_id_image_instance2', dest='id_image_instance2',
                        help="The image to which the linked annotation will be added"),
    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:

        # Sanity check: the 2 images must be in the same image group.
        igii1 = ImageGroupImageInstanceCollection().fetch_with_filter("imageinstance", params.id_image_instance1)
        igii2 = ImageGroupImageInstanceCollection().fetch_with_filter("imageinstance", params.id_image_instance2)
        if len(igii1) != 1 or len(igii2) != 1 or igii1[0].group != igii2[0].group:
            raise ValueError("Images are not in the same image group !")
        id_image_group = igii1[0].group

        # We first add a point in (10,10) in both images
        point = Point(10, 10)
        annotation_point1 = Annotation(location=point.wkt, id_image=params.id_image_instance1).save()
        annotation_point2 = Annotation(location=point.wkt, id_image=params.id_image_instance2).save()

        # Now we will link them.
        # 1) First I need to create an annotation group
        annotation_group = AnnotationGroup(id_project=params.id_project, id_image_group=id_image_group).save()
        print(annotation_group)

        # 2) I add the 2 annotations into the group to create links
        al1 = AnnotationLink(id_annotation=annotation_point1.id, id_annotation_group=annotation_group.id).save()
        print(al1)
        al2 = AnnotationLink(id_annotation=annotation_point2.id, id_annotation_group=annotation_group.id).save()
        print(al2)

        # List all annotations in that annotation group:
        annots = AnnotationCollection()
        annots.project = 682669
        annots.showLink = True
        annots.group = annotation_group.id
        annots.fetch()
        print(annots)
        for annot in annots:
            n_links = len(annot.annotationLink)
            # n_links will be 2 as it contains links al1->annotation_group and al2->annotation_group
            linked_annot_ids = [al['annotation'] for al in annot.annotationLink]

            print(
                f"Annotation {annot.id} in image {annot.image} | "
                f"has {n_links} links | "
                f"(annotations: {linked_annot_ids})"
            )

        # ---------------
        # How to speed up the process when we have more data ?
        # We will create points (5, 5) in every image and link them
        # We will create rectangle (20, 20, 100, 100) in every image and link them
        point = Point(5, 5)
        rectangle = box(20, 20, 100, 100)

        # I need 2 annotation groups:
        annot_group_ids = []
        for i in range(2):
            ag = AnnotationGroup(id_project=params.id_project, id_image_group=id_image_group).save()
            annot_group_ids.append(ag.id)

        # We will create all annotations in one request.
        annotations = AnnotationCollection()
        image_ids = [params.id_image_instance1, params.id_image_instance2]
        for image_id in image_ids:
            for i, geometry in enumerate([point, rectangle]):
                annotations.append(
                    Annotation(location=geometry.wkt, id_project=params.id_project, id_image=image_id,
                               id_group=annot_group_ids[i])
                )

        annotations.save()
        # In the end, we have:
        # - a point in image 1, linked to a point in image 2
        # - a rectangle in image 1, linked to a rectangle in image 2
        # - a point in image 2, linked to a point in image 1
        # - a rectangle in image 2, linked to a rectangle in image 1
