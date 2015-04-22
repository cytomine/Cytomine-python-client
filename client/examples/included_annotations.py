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


from cytomine import Cytomine
import sys,time
import os
from array import *

#Connection parameters to Cytomine
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"
#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)

#Replace XXX values by the project identifier, term id of the ROI where you want to count object (of type id_object_term) created by user id_user
id_project=XXX
id_roi_term=XXX
id_object_term=XXX
id_user=XXX

#Replace XXX by identifiers of images where you want to compute statistics
images=array('i', [XXX,XXX])

for id_image in images:
    #Retrieve image instance
    image_instance = conn.get_image_instance(id_image)

    #Retrieve ROI annotations (e.g. sections)
    roi_annotations = conn.get_annotations(id_image = id_image,
                                           id_term = id_roi_term,
                                           id_project= id_project,
                                           id_user=id_user,
                                           reviewed_only=False)

    #Retrieve annotations that are included in ROI annotations
    for roi_annotation in roi_annotations.data():
        included_annotations = conn.included_annotations(id_image, id_user, roi_annotation.id,id_object_term)
        print "Image ID %d name: %s number of annotations of term %d included in ROI : %d" %(id_image,image_instance.originalFilename,id_object_term,len(included_annotations.data()))

print "END."
