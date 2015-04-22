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


import numpy as np
import cv
import cv2

class ObjectFinder_(object):

    def __init__(self, cv_image):
        self.cv_image = cv_image
        cv_size = cv.GetSize(cv_image)
        self.width = cv_size[0]
        self.height = cv_size[1]

    def find_components(self, contours_retrieval_mode = cv.CV_RETR_CCOMP):
        #CV_RETR_EXTERNAL to only get external contours.
        storage = cv.CreateMemStorage()
        contours = cv.FindContours(self.cv_image, storage, contours_retrieval_mode, cv.CV_CHAIN_APPROX_SIMPLE)
        #cv.Zero(self.cv_image)
        components = []
        while contours:
            component = []
            points = list(contours)
             
            if len(points) > 3 :
                for point in points:
                    component.append((point[0], point[1]))
                components.append(component)

            contours = contours.h_next()

        del contours
        return components

class ObjectFinder(object):

    def __init__(self, np_image):
        self.np_image = np.asarray(np_image[:])
        np_size = self.np_image.shape
        self.width = np_size[1]
        self.height = np_size[0]
        
        
    def find_components(self):
        #CV_RETR_EXTERNAL to only get external contours.
        contours, hierarchy = cv2.findContours(self.np_image.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        
        components = []
        if (len(contours) > 0):
            top_index = 0
            tops_remaining = True
            while tops_remaining:
                exterior = contours[top_index][:,0,:].tolist()
                
                interiors = []
                # check if there are childs and process if necessary
                if (hierarchy[0][top_index][2] != -1):
                    sub_index = hierarchy[0][top_index][2]
                    subs_remaining = True
                    while subs_remaining:
                        interiors.append(contours[sub_index][:,0,:].tolist())
                        
                        # check if there is another sub contour
                        if (hierarchy[0][sub_index][0] != -1):
                            sub_index = hierarchy[0][sub_index][0]
                        else:
                            subs_remaining = False
                
                # add component tupple to components only if exterior is a polygon
                if (len(exterior) > 3):
                    components.append( (exterior, interiors) )
                
                # check if there is another top contour
                if (hierarchy[0][top_index][0] != -1):
                    top_index = hierarchy[0][top_index][0]
                else:
                    tops_remaining = False

        del contours
        del hierarchy
        return components
   
