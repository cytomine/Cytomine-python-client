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


from model import Model
from collection import Collection



class ImageGroup(Model):

    def __init__(self, params = None):
        super(ImageGroup, self).__init__(params)
        self._callback_identifier = "imagegroup"

    def to_url(self):
        if hasattr(self, "id"):
            return "imagegroup/%d.json" % self.id
        else:
            return "imagegroup.json"

    def __str__( self ):
        return str(self.id) + " : " + str(self.name)


class Image(Model):

    def __init__(self, params = None):
        super(Image, self).__init__(params)
        self._callback_identifier = "abstractimage"

    def to_url(self):
        if hasattr(self, "id"):
            return "abstractimage/%d.json" % self.id
        else:
            return "abstractimage.json"
   
    def get_property_url(self, extract = False):
        if extract:
            return "abstractimage/%d/property.json?extract=true" % self.id
        else:
            return "abstractimage/%d/property.json" % self.id

    def __str__( self ):
        return str(self.id) + " : " + str(self.name)

class ImageInstance(Model):

    def __init__(self, params = None):
        super(ImageInstance, self).__init__(params)
        self._callback_identifier = "imageinstance"

    def to_url(self):
        if hasattr(self, "id"):
            return "imageinstance/%d.json" % self.id
        else:
            return "imageinstance.json"

    def get_crop_url(self, position):
        return "imageinstance/%d/window-%d-%d-%d-%d.png" % (self.id, position['x'], position['y'], position['w'], position['h'])

    def get_crop_geometry_url(self, geometry):
        return "imageinstance/%d/cropgeometry?geometry=%s" % (self.id, geometry.replace(" ", "%20"))

    def __str__( self ):
        return "ImageInstance : " + str(self.id)

class NestedImage(Model):

    def __init__(self, params = None):
        super(NestedImage, self).__init__(params)
        self._callback_identifier = "nestedimageinstance"

    def to_url(self):
        if hasattr(self, "id"):
            return "imageinstance/%d/nested/%d.json" % (self.parent, self.id)
        else:
            return "imageinstance/%d/nested.json" % self.parent

    def __str__( self ):
        return "NestedImageInstance : " + str(self.id)

class ImageInstanceServersURL(Model):
    def __init__(self, params = None):
        super(ImageInstanceServersURL, self).__init__(params)
        self._callback_identifier = "imageServersURLs"

    def to_url(self):
        return "abstractimage/%d/imageservers.json" % self.id

    def __str__( self ):
       return "ImageInstanceServersURL : " 


class AbstractImageGroup(Model):
	
    def __init__(self, params = None):
        super(AbstractImageGroup, self).__init__(params)
        self._callback_identifier = "abstractImageGroup"

    def to_url(self):
        if hasattr(self, "group") and hasattr(self, "abstractimage"):
            return "abstractimage/%d/group/%d.json" % (self.group, self.abstractimage)
        else:
            return "404.json" #does not exists

    def __str__( self ):
        return str(self.group) + " & " + str(self.abstractimage)	

class ImageInstanceCollection(Collection):    

    def __init__(self, params = None):
        super(ImageInstanceCollection, self).__init__(ImageInstance, params)

    def to_url(self):
        if hasattr(self, "project"):
            return "project/" + str(self.project) + "/imageinstance.json"
        else:
            return "imageinstance.json"

