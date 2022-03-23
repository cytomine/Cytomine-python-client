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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

import os
import re

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection, CollectionPartialUploadException
from cytomine.models.model import Model
from ._utilities import generic_image_dump, generic_download, is_false


class Annotation(Model):
    def __init__(self, location=None, id_image=None, id_terms=None, id_project=None, id_tracks=None, id_slice=None,
                 **attributes):
        super(Annotation, self).__init__()
        self.location = location
        self.image = id_image
        self.slice = id_slice
        self.project = id_project
        self.term = id_terms
        self.track = id_tracks
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
             zoom=None, max_size=None, increase_area=None, contrast=None, gamma=None, colormap=None, inverse=None,
             complete=True):
        """
        Download the annotation crop, with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists. The extension must be jpg, png or tif.
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
        max_size : int, optional
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
        complete: bool, optional. Default: True
            True to use the annotation without simplification in masks and alphaMasks

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise. As a side effect, object attribute "filename"
            is filled with downloaded file path.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        parameters = {
            "zoom": zoom,
            "maxSize": max_size,
            "increaseArea": increase_area,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits,
            "complete": complete
        }

        def dump_url_fn(model, file_path, **kwargs):
            extension = os.path.basename(file_path).split(".")[-1]
            if mask and alpha:
                image = "alphamask"
                if extension == "jpg":
                    extension = "png"
            elif mask:
                image = "mask"
            else:
                image = "crop"
            return model.cropURL.replace("crop.png", "{}.{}".format(image, extension)).replace("crop.jpg", "{}.{}".format(image, extension))

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, **parameters)

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True

    def profile(self):
        if self.id is None:
            raise ValueError("Cannot review an annotation with no ID.")

        data = Cytomine.get_instance().get("{}/{}/profile.json".format(self.callback_identifier, self.id))
        return data['collection'] if "collection" in data else data

    def profile_projections(self, axis=None, csv=False, csv_dest_pattern="projections-annotation-{id}.csv"):
        """
        Get profile projections (min, max, average) for the given annotation.

        Parameters
        ----------
        axis The axis along which the projections (min, max, average) are performed. By default last axis is used.
        To project along spatial X, Y axes, use special value "xy" or "spatial".
        csv True to return result in a CSV file.
        csv_dest_pattern The CSV destination pattern.

        """
        if self.id is None:
            raise ValueError("Cannot review an annotation with no ID.")

        uri = "{}/{}/profile/projections.{}".format(self.callback_identifier, self.id, "csv" if csv else "json")
        if csv:
            pattern = re.compile("{(.*?)}")
            destination = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), csv_dest_pattern)

            return Cytomine.get_instance().download_file(uri, destination, payload={"axis": axis})

        data = Cytomine.get_instance().get(uri, {"axis": axis})
        return data['collection'] if "collection" in data else data

    def profile_projection(self, projection='max',  dest_pattern="{id}.png", override=True):
        if self.id is None:
            raise ValueError("Cannot review an annotation with no ID.")

        def dump_url_fn(model, file_path, **kwargs):
            extension = os.path.basename(file_path).split(".")[-1]
            return "{}/{}/profile/{}-projection.{}".format(self.callback_identifier, model.id, projection, extension)

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override)

        if len(files) == 0:
            return False

        return True

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
        self.showTrack = None
        self.showAlgo = None
        self.showUser = None
        self.showImage = None
        self.showSlice = None
        self.showImageGroup = None
        self.showLink = None
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

        self.slice = None
        self.slices = None

        self.term = None
        self.terms = None
        self.suggestedTerm = None
        self.userForTermAlgo = None
        self.jobForTermAlgo = None

        self.track = None
        self.tracks = None

        self.group = None
        self.groups = None

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

    def dump_crops(self, dest_pattern, n_workers=0, override=True, **dump_params):
        """Download the crops of the annotations
        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        n_workers: int
            Number of workers to use (default: uses all the available processors)
        dump_params: dict
            Parameters for dumping the annotations (see Annotation.dump)

        Returns
        -------
        annotations: AnnotationCollection
            Annotations that have been successfully downloaded (containing a `filenames` attribute)
        """

        def dump_crop(an):
            if is_false(an.dump(dest_pattern=dest_pattern, override=override, **dump_params)):
                return False
            else:
                return an

        results = generic_download(self, download_instance_fn=dump_crop, n_workers=n_workers)

        # check errors
        count_fail = 0
        failed = list()
        for in_annot, out_annot in results:
            if is_false(out_annot):
                count_fail += 1
                failed.append(in_annot.id)

        logger = Cytomine.get_instance().logger
        if count_fail > 0:
            n_annots = len(self)
            ratio = 100 * count_fail / float(n_annots)
            logger.info(
                "Failed to download crops for {}/{} annotations ({:3.2f} %).".format(count_fail, n_annots, ratio))
            logger.debug("Annotation with crop download failure: {}".format(failed))

        collection = AnnotationCollection()
        collection.extend([an for _, an in results if not isinstance(an, bool) or an])
        return collection


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

