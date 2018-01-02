# -*- coding: utf-8 -*-


#
# * Copyright (c) 2009-2017. Authors: see NOTICE file.
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

__author__          = "Marée Raphaël <raphael.maree@ulg.ac.be>"
__copyright__       = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"


from model import Model
from collection import Collection


class AnnotationAction(Model):
    def __init__(self, params = None):
        super(AnnotationAction, self).__init__(params)
        self._callback_identifier = "annotationactions"

    def to_url(self):
        if hasattr(self, "id"):
            return "annotationactions/%d.json" % self.id
        else:
            return "annotationactions.json"


class AnnotationActionCollection(Collection):

    def __init__(self, params = None):
        super(AnnotationActionCollection, self).__init__(AnnotationAction, params)

    def to_url(self):
        if hasattr(self, "imageinstance"):
            return "imageinstance/" + str(self.imageinstance) + "/annotationactions.json"
        else:
            return "imageinstance.json"