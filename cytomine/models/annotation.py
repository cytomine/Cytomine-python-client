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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

import os
import re

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model, DomainModel


class Annotation(Model):
    def __init__(self, location=None, id_image=None, id_terms=None, id_project=None, **attributes):
        super(Annotation, self).__init__()
        self.location = location
        self.image = id_image
        self.project = id_project
        self.term = id_terms
        self.geometryCompression = None
        self.area = None
        self.areaUnit = None
        self.perimeter = None
        self.perimeterUnit = None
        self.cropURL = None

        self.populate(attributes)

    def __str__(self):
        return "[{}] {}".format(self.callback_identifier, self.id)

    def review(self, id_terms=None):
        if self.id is None:
            raise ValueError("Cannot review an annotation with no ID.")

        if not id_terms:
            id_terms = []
        data = {"id": self.id, "terms": id_terms}
        return Cytomine.get_instance().post("{}/{}/review.json".format(self.callback_identifier, self.id), data)

    def dump(self, dest_pattern="{id}.jpg", override=True, mask=False, alpha=False, bits=8,
             zoom=None, max_size=None, increase_area=None, contrast=None, gamma=None, colormap=None, inverse=None):
        """
        Download the annotation crop, with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        mask : bool, optional
            True if a binary mask based on given annotations must be returned, False otherwise.
        alpha : bool, optional
            True if image background (outside annotations) must be transparent, False otherwise.
        zoom : int, optional
            Optional image zoom number
        bits : int (8,16,32) or str ("max"), optional
            Bit depth (bit per channel) of returned image. "max" returns the original image bit depth
        max_size : int, tuple, optional
            Maximum size (width or height) of returned image. None to get original size.
        increase_area : float, optional
            Increase the crop size. For example, an annotation whose bounding box size is (w,h) will have
            a crop dimension of (w*increase_area, h*increase_area).
        contrast : float, optional
            Optional contrast applied on returned image.
        gamma : float, optional
            Optional gamma applied on returned image.
        colormap : int, optional
            Cytomine identifier of a colormap to apply on returned image.
        inverse : bool, optional
            True to inverse color mapping, False otherwise.

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise. As a side effect, object attribute "filename"
            is filled with downloaded file path.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        pattern = re.compile("{(.*?)}")
        dest_pattern = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), dest_pattern)

        destination = os.path.dirname(dest_pattern)
        filename, extension = os.path.splitext(os.path.basename(dest_pattern))
        extension = extension[1:]

        if extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        if not os.path.exists(destination):
            os.makedirs(destination)

        parameters = {
            "zoom": zoom,
            "maxSize": max_size,
            "increaseArea": increase_area,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits
        }

        if mask and alpha:
            image = "alphamask"
            if extension == "jpg":
                extension = "png"
        elif mask:
            image = "mask"
        else:
            image = "crop"

        file_path = os.path.join(destination, "{}.{}".format(filename, extension))

        url = self.cropURL.replace("crop.jpg", "{}.{}".format(image, extension))
        result = Cytomine.get_instance().download_file(url, file_path, override, parameters)
        if result:
            self.filename = file_path
        return result

    """
    Deprecated functions. Still here for backwards compatibility.
    """
    get_annotation_crop_url = None
    get_annotation_crop_tiled_translated = None
    get_annotation_alpha_crop_url = None
    get_annotation_mask_url = None
    # def get_annotation_crop_tiled_translated(self,minx,maxx,miny,maxy,id_image,image_height,tile_size,translate):
    #     #original annotation bounding box width & height
    #     w_width=maxx-minx
    #     w_height=maxy-miny
    #     if translate:
    #         #maximum shift is predefined, it is determined by half of the size of the object such
    # that at least half is still included
    #         translate_x = random.randrange(-w_width/2, w_width/2)
    #         translate_y = random.randrange(-w_height/2, w_height/2)
    #         print "translate_x: %d translate_y: %d" %(translate_x,translate_y)
    #         minx = minx + translate_x
    #         maxx = maxx + translate_x
    #         miny = miny + translate_y
    #         maxy = maxy + translate_y
    #
    #     #we construct new coordinates (for dimension(s) < tile_size) so that we finally have image dimensions
    #  at least of tile_size
    #     #e.g. tile_size=512, if annotation 400x689 it becomes 512x689, if annotation 234x123 it becomes 512x512
    #     if w_width < tile_size:
    #         displace_x = tile_size - w_width
    #         minx = minx - displace_x/2
    #         maxx = minx + tile_size
    #     if w_height < tile_size:
    #         displace_y = tile_size - w_height
    #         miny = miny - displace_y/2
    #         maxy = miny + tile_size
    #     windowURL = "imageinstance/%d/window-%d-%d-%d-%d.jpg" %(id_image,minx,image_height-maxy,maxx-minx,maxy-miny)
    #
    #     return windowURL


class AnnotationCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AnnotationCollection, self).__init__(Annotation, filters, max, offset)
        self._allowed_filters = [None]

        self.showBasic = True
        self.showMeta = True
        self.showWKT = None
        self.showGIS = None
        self.showTerm = None
        self.showAlgo = None
        self.showUser = None
        self.showImage = None
        self.reviewed = None
        self.noTerm = None
        self.noAlgoTerm = None
        self.multipleTerm = None

        self.project = None

        self.job = None
        self.user = None
        self.users = None

        self.image = None
        self.images = None

        self.term = None
        self.terms = None
        self.suggestedTerm = None
        self.userForTermAlgo = None
        self.jobForTermAlgo = None

        self.bbox = None
        self.bboxAnnotation = None
        self.baseAnnotation = None
        self.maxDistanceBaseAnnotation = None

        self.included = False
        self.annotation = None

        self.set_parameters(parameters)

    def uri(self, without_filters=False):
        if self.included:
            self.add_filter("imageinstance", self.image)
        uri = super(AnnotationCollection, self).uri(without_filters)
        if self.included:
            return uri.replace(".json", "/included.json")

        return uri


class AnnotationTerm(Model):
    def __init__(self, id_annotation=None, id_term=None, **attributes):
        super(AnnotationTerm, self).__init__()
        self.userannotation = id_annotation
        self.term = id_term
        self.user = None
        self.populate(attributes)

    def uri(self):
        return "annotation/{}/term/{}.json".format(self.userannotation, self.term)

    def fetch(self, id_annotation=None, id_term=None):
        self.id = -1

        if self.userannotation is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.term is None and id_term is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.userannotation = id_annotation

        if id_term is not None:
            self.term = id_term

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a annotation-term.")

    def __str__(self):
        return "[{}] Annotation {} - Term {}".format(self.callback_identifier, self.userannotation, self.term)


class AlgoAnnotationTerm(Model):
    def __init__(self, id_annotation=None, id_term=None, id_expected_term=None, rate=1.0, **attributes):
        super(AlgoAnnotationTerm, self).__init__()
        self.annotation = id_annotation
        self.annotationIdent = id_annotation
        self.term = id_term
        self.expectedTerm = id_expected_term
        self.user = None
        self.rate = rate
        self.populate(attributes)

    def uri(self):
        return "annotation/{}/term/{}.json".format(self.annotation, self.term)

    def fetch(self, id_annotation=None, id_term=None):
        self.id = -1

        if self.annotation is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.term is None and id_term is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.annotation = id_annotation

        if id_term is not None:
            self.term = id_term

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a annotation-term.")

    def __str__(self):
        return "[{}] Annotation {} - Term {}".format(self.callback_identifier, self.annotation, self.term)


class AnnotationFilter(Model):
    def __init__(self, name=None, users=None, terms=None, **attributes):
        super(AnnotationFilter, self).__init__()
        self.name = name
        self.users = users
        self.terms = terms
        self.populate(attributes)


class AnnotationFilterCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(AnnotationFilterCollection, self).__init__(AnnotationFilter, filters, max, offset)
        self._allowed_filters = [None]
        self.project = None
        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save an annotation filter collection by client.")