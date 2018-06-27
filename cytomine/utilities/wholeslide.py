# -*- coding: utf-8 -*-

#
# * Copyright (c) 2009-2015. Authors: see NOTICE file.
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
# */


__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"
__version__ = '0.1'

import math


class WholeSlide(object):

    def __init__(self, image, tile_size=256, roi=(0, 0, 1, 1)):  # tile size should be in JSON of imageinstance
        self.image = image
        self.depth = image.depth
        self.width = image.width
        self.height = image.height
        self.server_urls = image.server_urls
        self.tile_size = tile_size
        self.num_tiles = 0
        self.levels = []
        self.mime = image.mime

        for i in range(0, self.image.depth):
            level_width = int(self.image.width / 2 ** i)
            level_height = int(self.image.height / 2 ** i)
            x_tiles = int(math.ceil(float(level_width) / (float(tile_size))))
            y_tiles = int(math.ceil(float(level_height) / float(tile_size)))
            level_num_tiles = x_tiles * y_tiles
            self.levels.append({'zoom': i,
                                'level_width': level_width,
                                'level_height': level_height,
                                'x_tiles': x_tiles,
                                'y_tiles': y_tiles,
                                'level_num_tiles': level_num_tiles
                                })

            self.num_tiles += level_num_tiles

    def convert_to_real_coordinates_(self, whole_slide, components, bounds, zoom):
        converted_components = []
        for component in components:
            converted_component = []
            for point in component:
                x = point[0]
                y = point[1]
                x_at_current_zoom = bounds.x + x
                y_at_current_zoom = bounds.y + y
                zoom_factor = pow(2, zoom)
                x_at_maximum_zoom = x_at_current_zoom * zoom_factor
                y_at_maximum_zoom = whole_slide.height - (y_at_current_zoom * zoom_factor)
                point = (int(x_at_maximum_zoom), int(y_at_maximum_zoom))
                converted_component.append(point)

            converted_components.append(converted_component)
        return converted_components

    def convert_to_real_coordinates(self, whole_slide, components, bounds, zoom):
        converted_components = []
        for component in components:
            # process exterior
            converted_exterior = []
            for point in component[0]:
                converted_point = self.__convert_point_to_real_coordinates(whole_slide, point, bounds, zoom)
                converted_exterior.append(converted_point)

            # process interiors
            converted_interiors = []
            for interior in component[1]:
                converted_interior = []
                for point in interior:
                    converted_point = self.__convert_point_to_real_coordinates(whole_slide, point, bounds, zoom)
                    converted_interior.append(converted_point)
                converted_interiors.append(converted_interior)

            converted_components.append((converted_exterior, converted_interiors))

        return converted_components

    def __convert_point_to_real_coordinates(self, whole_slide, point, bounds, zoom):
        x = point[0]
        y = point[1]
        x_at_current_zoom = bounds.x + x
        y_at_current_zoom = bounds.y + y
        zoom_factor = pow(2, zoom)
        x_at_maximum_zoom = x_at_current_zoom * zoom_factor
        y_at_maximum_zoom = whole_slide.height - (y_at_current_zoom * zoom_factor)
        return (int(x_at_maximum_zoom), int(y_at_maximum_zoom))

    def convert_to_local_coordinates(self, whole_slide, components, bounds, zoom):
        converted_components = []
        for component in components:
            # process exterior
            converted_exterior = []
            for point in component[0]:
                converted_point = self.__convert_point_to_local_coordinates(whole_slide, point, bounds, zoom)
                converted_exterior.append(converted_point)

            # process interiors
            converted_interiors = []
            for interior in component[1]:
                converted_interior = []
                for point in interior:
                    converted_point = self.__convert_point_to_local_coordinates(whole_slide, point, bounds, zoom)
                    converted_interior.append(converted_point)
                converted_interiors.append(converted_interior)

            converted_components.append((converted_exterior, converted_interiors))

        return converted_components

    def __convert_point_to_local_coordinates(self, whole_slide, point, bounds, zoom):
        zoom_factor = pow(2, zoom)
        x = (point[0] / zoom_factor) - bounds.x
        y = ((whole_slide.height - point[1]) / zoom_factor) - bounds.y
        return (int(x), int(y))

    def get_roi_with_real_coordinates(self, roi):
        roi_x = self.width * roi[0]
        roi_y = self.height * roi[1]
        roi_width = self.width * roi[2]
        roi_height = self.height * roi[3]
        return roi_x, roi_y, roi_width, roi_height
