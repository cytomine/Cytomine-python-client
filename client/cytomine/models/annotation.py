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
import random

class Annotation(Model):

    def __init__(self, params = None):
        super(Annotation, self).__init__(params)
        self._callback_identifier = "annotation"

    def to_url(self):
        if hasattr(self, "id"):
            return "annotation/%d.json" % self.id
        else:
            return "annotation.json"

    def get_annotation_crop_url(self, desired_zoom = None, max_size = None):
        if desired_zoom:
            return self.cropURL.replace(".jpg",".png?zoom=%d" % desired_zoom)
        elif max_size:
            return self.cropURL.replace(".jpg",".png?max_size=%d" % max_size)  
        else:
            return self.cropURL.replace(".jpg",".png")  

    def get_annotation_crop_tiled_translated(self,minx,maxx,miny,maxy,id_image,image_height,tile_size,translate):
        #original annotation bounding box width & height
        w_width=maxx-minx
        w_height=maxy-miny
        if translate: 
            #maximum shift is predefined, it is determined by half of the size of the object such that at least half is still included
            translate_x = random.randrange(-w_width/2, w_width/2)
            translate_y = random.randrange(-w_height/2, w_height/2)
            print "translate_x: %d translate_y: %d" %(translate_x,translate_y)
            minx = minx + translate_x
            maxx = maxx + translate_x
            miny = miny + translate_y
            maxy = maxy + translate_y
        
        #we construct new coordinates (for dimension(s) < tile_size) so that we finally have image dimensions at least of tile_size
        #e.g. tile_size=512, if annotation 400x689 it becomes 512x689, if annotation 234x123 it becomes 512x512
        if w_width < tile_size:
            displace_x = tile_size - w_width
            minx = minx - displace_x/2
            maxx = minx + tile_size
        if w_height < tile_size:
            displace_y = tile_size - w_height
            miny = miny - displace_y/2
            maxy = miny + tile_size
        windowURL = "imageinstance/%d/window-%d-%d-%d-%d.jpg" %(id_image,minx,image_height-maxy,maxx-minx,maxy-miny)

        return windowURL



    def get_annotation_alpha_crop_url(self, desired_zoom = None, max_size = None):
        if desired_zoom:
            return self.cropURL.replace("crop.jpg","alphamask.png?zoom=%d" % (desired_zoom))
        elif max_size:
            return self.cropURL.replace("crop.jpg","alphamask.png?max_size=%d" % (max_size))
        else:
            return self.cropURL.replace("crop.jpg", "alphamask.png")

    def get_annotation_mask_url(self, desired_zoom = None, max_size = None):
        if desired_zoom:
            return self.cropURL.replace("crop.jpg","mask.png?zoom=%d" % (desired_zoom))
        elif max_size:
            return self.cropURL.replace("crop.jpg","mask.png?max_size=%d" % (max_size))
        else:
            return self.cropURL.replace("crop.jpg", "mask.png")

    def __str__( self ):
        return "Annotation : " + str(self.id)

class AnnotationUnion(Model):

    def __init__(self, params = None):
        super(AnnotationUnion, self).__init__(params)
        self._callback_identifier = "annotationunion"

    def to_url(self):
        if self.buffer_length: 
            return "algoannotation/union.json?idUser=%d&idImage=%d&idTerm=%d&minIntersectionLength=%d&bufferLength=%d" % (self.id_user, self.id_image, self.id_term, self.min_intersection_length,self.buffer_length)
        else:
            return "algoannotation/union.json?idUser=%d&idImage=%d&idTerm=%d&minIntersectionLength=%d" % (self.id_user, self.id_image, self.id_term, self.min_intersection_length)

    def __str__( self ):
        return "Annotation Union %d,%d,%d,%d " % (self.id_user, self.id_image, self.id_term, self.min_intersection_length)   


class AnnotationTerm(Model):

    def __init__(self, params = None):
        super(AnnotationTerm, self).__init__(params)
        self._callback_identifier = "annotationterm"

    def to_url(self):
        if hasattr(self, "annotation") and hasattr(self, "term"):
            return "annotation/%d/term/%d.json" % (self.annotation, self.term)
        elif hasattr(self, "annotation"):
            return "annotation/%d/term.json" % (self.annotation)

    def __str__( self ):
        return "Annotation : " + str(self.id)

class AlgoAnnotationTerm(AnnotationTerm):

    def __init__(self, params = None):
        super(AlgoAnnotationTerm, self).__init__(params)
        self._callback_identifier = "algoannotationterm"

class AnnotationProperty(Model):

    def __init__(self, params = None):
        super(AnnotationProperty, self).__init__(params)
        self._callback_identifier = "property"

    def to_url(self):
        if hasattr(self, "domainIdent") and not hasattr(self, "id"):#new
            return "annotation/%d/property.json" % self.domainIdent
        elif hasattr(self, "domainIdent") and hasattr(self, "id"):
            return "annotation/%d/property/%d.json" % (self.domainIdent, self.id)        

    def __str__( self ):
        return "Annotation Property %d,%d " % (self.annotation, self.id)

class AnnotationPropertyCollection(Collection):

    def __init__(self, params = None):
        super(AnnotationPropertyCollection, self).__init__(AnnotationProperty, params)        

    def to_url(self):
        if hasattr(self, "annotation_id"):
            return "annotation/%d/property.json" % self.annotation_id
        else:
            return None        

    def __str__( self ):
        return "Annotation Properties"  

#class AnnotationCollection(Collection):    
    
#    def __init__(self, params = None):
 #       super(AnnotationCollection, self).__init__(Annotation, params)

 #   def to_url(self):
  #      if hasattr(self, "project"):
   #         return "project/" + str(self.project) + "/annotation.json"
   #     elif hasattr(self, "user") and hasattr(self, "imageinstance"):
    #        return "user/" + str(self.user) + "/imageinstance/" + str(self.imageinstance) +  "/annotation.json"
    #    elif hasattr(self, "imageinstance"):
    #        return "imageinstance/" + str(self.imageinstance) +  "/userannotation.json"
    #    else:
    #        return "annotation.json"



class AnnotationCollection(Collection):

    def __init__(self, params = None):
        super(AnnotationCollection, self).__init__(Annotation, params)

    def to_url(self):
        if hasattr(self, "project") and hasattr(self,"term"):
            return "term/" + str(self.term) + "/project/" + str(self.project) + "/annotation.json"
        elif hasattr(self, "project"):
            return "project/" + str(self.project) + "/annotation.json"
        elif hasattr(self, "included") and hasattr(self, "imageinstance"):
            return "imageinstance/" + str(self.imageinstance) + "/annotation/" + "included.json"
        elif hasattr(self, "user") and hasattr(self, "imageinstance"):
            return "user/" + str(self.user) + "/imageinstance/" + str(self.imageinstance) +  "/annotation.json"
        elif hasattr(self, "imageinstance"):
            return "imageinstance/" + str(self.imageinstance) +  "/userannotation.json"
        else:
            return "annotation.json"



class ReviewedAnnotationCollection(Collection):
    
    def __init__(self, params = None):
        super(ReviewedAnnotationCollection, self).__init__(Annotation, params)

    def to_url(self):
        if hasattr(self, "project"):
            return "project/" + str(self.project) + "/reviewedannotation.json"
        elif hasattr(self, "user") and hasattr(self, "imageinstance"):
            return "user/" + str(self.user) + "/imageinstance/" + str(self.imageinstance) +  "/reviewedannotation.json"
        elif hasattr(self, "imageinstance"):
            return "imageinstance/" + str(self.imageinstance) +  "/reviewedannotation.json"
        else:
            return "reviewedannotation.json"
