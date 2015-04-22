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


__author__          = "Stévens Benjamin <b.stevens@ulg.ac.be>" 
__contributors__    = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]                
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"
__version__         = '0.1'


from shapely.geometry.polygon import Polygon
from shapely.wkt import dumps

class Utils_(object):

    def get_geometries(self, components, min_area = None, max_area = None):
        locations = []
        for component in components:
            p = Polygon(component)
            if min_area and max_area:
                #print p.area
                if p.area > min_area and p.area < max_area:
                    locations.append(p.wkt)
            else:
                locations.append(p.wkt)

        return locations


class Utils(object):

    def get_geometries(self, components, min_area = None, max_area = None):
        locations = []
        for component in components:
            p = Polygon(component[0], component[1])
            if min_area and max_area:
                #print p.area
                if p.area > min_area and p.area < max_area:
                    locations.append(p.wkt)
            else:
                locations.append(p.wkt)

        return locations
