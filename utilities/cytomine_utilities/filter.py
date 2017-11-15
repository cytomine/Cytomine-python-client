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


import cv2
import numpy as np

class Filter(object):

    def __init__(self):
        return

    def process(self, image):
        raise NotImplementedError( "Should have implemented this" )

class AdaptiveThresholdFilter(Filter):

    def __init__(self, block_size = 71, c = 3):
        super(Filter, self).__init__()
        self.block_size = block_size
        self.c = c

    def process(self, image):
        image_gray = np.array((image.shape[0], image.shape[1]))
        cv2.cvtColor(image,image_gray, cv2.COLOR_BGR2GRAY)
        cv2.adaptiveThreshold(image_gray, image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, self.block_size, self.c)
        return image_gray

class BinaryFilter(Filter):

    def __init__(self, threshold = 128):
        super(Filter, self).__init__()
        self.threshold = threshold


    def process(self, image):
        image_gray = np.array((image.shape[0], image.shape[1]))
        cv2.cvtColor(image, image_gray, cv2.COLOR_BGR2GRAY)
        cv2.threshold( image_gray, image_gray, self.threshold, 255, cv2.THRESH_BINARY_INV)
        return image_gray

class OtsuFilter(Filter):

    def __init__(self, threshold = 128):
        super(Filter, self).__init__()
        self.threshold = threshold


    def process(self, image):
        image_gray = np.array((image.shape[0], image.shape[1]))
        cv2.cvtColor(image, image_gray, cv2.COLOR_BGR2GRAY)
        cv2.threshold( image_gray, image_gray, self.threshold, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return image_gray
