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

import numpy as np
import cv2

from shapely.geometry.polygon import Polygon


#  TODO: Clean & Update

def get_geometries(components, min_area=None, max_area=None):
    locations = []
    for component in components:
        p = Polygon(component[0], component[1])
        if min_area and max_area:
            if min_area < p.area < max_area:
                locations.append(p.wkt)
        else:
            locations.append(p.wkt)

    return locations


class ObjectFinder(object):
    def __init__(self, np_image):
        self.np_image = np.asarray(np_image[:])
        np_size = self.np_image.shape
        self.width = np_size[1]
        self.height = np_size[0]

    def _find_components(self, mode, method):
        results = cv2.findContours(self.np_image.copy(), mode, method)
        if len(results) == 3:
            _, contours, hierarchy = results
        else:
            # OpenCV 4+
            contours, hierarchy = results

        components = []
        if len(contours) > 0:
            top_index = 0
            tops_remaining = True
            while tops_remaining:
                exterior = contours[top_index][:, 0, :].tolist()

                interiors = []
                # check if there are children and process if necessary
                if hierarchy[0][top_index][2] != -1:
                    sub_index = hierarchy[0][top_index][2]
                    subs_remaining = True
                    while subs_remaining:
                        interiors.append(contours[sub_index][:, 0, :].tolist())

                        # check if there is another sub contour
                        if hierarchy[0][sub_index][0] != -1:
                            sub_index = hierarchy[0][sub_index][0]
                        else:
                            subs_remaining = False

                # add component tuple to components only if exterior is a polygon
                if len(exterior) > 3:
                    components.append((exterior, interiors))

                # check if there is another top contour
                if hierarchy[0][top_index][0] != -1:
                    top_index = hierarchy[0][top_index][0]
                else:
                    tops_remaining = False
        return components

    def find_components_list(self):
        return self._find_components(cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    def find_components(self):
        return self._find_components(cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
