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

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

import cv2


#  TODO: Move to related datamining application

class Filter(object):
    def __init__(self):
        return

    def process(self, image):
        raise NotImplementedError("Should have implemented this")


class AdaptiveThresholdFilter(Filter):
    def __init__(self, block_size=71, c=3):
        super(Filter, self).__init__()
        self.block_size = block_size
        self.c = c

    def process(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.adaptiveThreshold(image_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV,
                                           self.block_size, self.c)
        return image_gray


class BinaryFilter(Filter):
    def __init__(self, threshold=128):
        super(Filter, self).__init__()
        self.threshold = threshold

    def process(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.threshold(image_gray, self.threshold, 255, cv2.THRESH_BINARY_INV)
        return image_gray


class OtsuFilter(Filter):
    def __init__(self, threshold=128):
        super(Filter, self).__init__()
        self.threshold = threshold

    def process(self, image):
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.threshold(image_gray, self.threshold, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return image_gray
