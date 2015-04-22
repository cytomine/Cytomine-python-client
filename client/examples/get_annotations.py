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


from cytomine import Cytomine
from cytomine.models import *


#Cytomine connection parameters
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"

#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#Replace XXX by your values
id_user=XXX
id_project=XXX
#If you want to filter by image or term, uncomment the following line and in the get_annotations call
#If you want not to filter by user, comment the previous line
#id_image=XXX
#id_term=XXX


#This retrieve the JSON description of existing annotations with full details (wkt, GIS information)
#If you don't need full details (e.g. only to count the number of annotations), comment showWKT,showMeta,showGIS
#to speed up the query
annotations = conn.get_annotations(
                                   id_project = id_project,
                                   id_user = id_user, 
                                   #id_image = id_image, 
                                   #id_term = id_term, 
                                   showWKT=True, 
                                   showMeta=True,
                                   showGIS=True,
                                   reviewed_only = False)
#Note: this will correspond to
#http://cytomine_host/api/annotation.json?&project=id_project&users=id_user&showGIS=true&showWKT=true&showMeta=true&showTerm=true&max=0&offset=0

print "Number of annotations: %d" %len(annotations.data())
for a in annotations.data():
        print "annotation id: %d image: %d project: %d term: %s user: %d area: %d perimeter: %s wkt: %s" %(a.id,a.image,a.project,a.term,a.user,a.area,a.perimeter,a.location)
        #If you want further details about a specific annotation, you can call get_annotation(annotation.id):
        #annotation = conn.get_annotation(a.id)
        #print "annotation centroid: %s" %annotation.centroid
        #print "annotation wkt: %s" %annotation.location



#If you want to dump annotations (get original images crops):
dump_type=1 #1: original image, 2: with alpha mask
zoom_level=3  #0 is maximum resolution
output_dir="/bigdata/tmp/cytomine/test/" #local directory where to dump annotation cropped images
if dump_type==1:
        annotation_get_func = Annotation.get_annotation_crop_url
elif dump_type==2:
        annotation_get_func = Annotation.get_annotation_alpha_crop_url
else:
        annotation_get_func = Annotation.get_annotation_crop_url  
#Note: if file already exists locally, they will not be requested again
print "Downloading annotations into %s ..." %output_dir
dump_annotations=conn.dump_annotations(annotations = annotations, 
                                       get_image_url_func = annotation_get_func, 
                                       dest_path =  output_dir,
                                       desired_zoom = zoom_level)

                                       
                                       





