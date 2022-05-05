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

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

import math
import random


class WholeSlide(object):
    def __init__(self, image, tile_size=256):
        self.image = image
        self.depth = image.zoom if image.zoom is not None else image.depth
        self.width = image.width
        self.height = image.height
        self.server_urls = image.image_servers()
        self.mime = image.reference_slice().mime
        self.tile_size = tile_size
        self.num_tiles = 0
        self.levels = []

        for i in range(self.depth + 1):
            level_width = int(self.width / 2 ** i)
            level_height = int(self.height / 2 ** i)
            x_tiles = int(math.ceil(float(level_width) / (float(tile_size))))
            y_tiles = int(math.ceil(float(level_height) / float(tile_size)))
            level_num_tiles = x_tiles * y_tiles
            self.num_tiles += level_num_tiles
            self.levels.append({'zoom': i,
                                'level_width': level_width,
                                'level_height': level_height,
                                'x_tiles': x_tiles,
                                'y_tiles': y_tiles,
                                'level_num_tiles': level_num_tiles
                                })

    def random_server_url(self):
        return random.choice(self.server_urls)

    def convert_to_real_coordinates(self, components, bounds, zoom):
        converted_components = []
        for component in components:
            converted_exterior = [self.convert_point_to_real_coordinates(point, bounds, zoom) for point in component[0]]
            converted_interiors = [[self.convert_point_to_real_coordinates(point, bounds, zoom) for point in interior]
                                   for interior in component[1]]
            converted_components.append((converted_exterior, converted_interiors))
        return converted_components

    def convert_point_to_real_coordinates(self, point, bounds, zoom):
        x, y = point[0], point[1]
        x_at_current_zoom = bounds.x + x
        y_at_current_zoom = bounds.y + y
        zoom_factor = pow(2, zoom)
        x_at_maximum_zoom = x_at_current_zoom * zoom_factor
        y_at_maximum_zoom = self.height - (y_at_current_zoom * zoom_factor)
        return int(x_at_maximum_zoom), int(y_at_maximum_zoom)

    def convert_to_local_coordinates(self, components, bounds, zoom):
        converted_components = []
        for component in components:
            converted_exterior = [self.convert_point_to_local_coordinates(point, bounds, zoom) for point in component[0]]
            converted_interiors = [[self.convert_point_to_local_coordinates(point, bounds, zoom) for point in interior]
                                   for interior in component[1]]
            converted_components.append((converted_exterior, converted_interiors))
        return converted_components

    def convert_point_to_local_coordinates(self, point, bounds, zoom):
        zoom_factor = pow(2, zoom)
        x = (point[0] / zoom_factor) - bounds.x
        y = ((self.height - point[1]) / zoom_factor) - bounds.y
        return int(x), int(y)

    def get_roi_with_real_coordinates(self, roi):
        roi_x = self.width * roi[0]
        roi_y = self.height * roi[1]
        roi_width = self.width * roi[2]
        roi_height = self.height * roi[3]
        return roi_x, roi_y, roi_width, roi_height
