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

__author__          = "Marée Raphaël <raphael.maree@ulg.ac.be>"
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine import Cytomine
from cytomine.models import *
from shapely.geometry import Point
from shapely.wkt import loads


#Cytomine connection parameters, replace XXX by your values
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"

#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= False)

#Project, user, ontology, replace XXX by your values
id_user=XXX
id_ontology=XXX
id_project=XXX

#Get the project ontology terms
print "Ontology:"
ontology_terms = conn.get_terms(id_ontology=id_ontology)
d = dict()
for t in ontology_terms.data():
        d[t.id] = t.name
        print d[t.id]
print "Number of terms in ontology: %d" %len(ontology_terms.data())


#Print the output header (csv style)
print "imageid,annotationid,landmarkterm,x,y"

#Get project images
images = conn.get_project_image_instances(id_project)
for i in images:
        image = conn.get_image_instance(i.id)
        #Get annotations in this image
        annotations = conn.get_annotations(
                id_project = id_project,
                id_user = id_user, 
                id_image = image.id, 
                showWKT=True, 
                reviewed_only = False) #True if you want to export reviewed annotations

        #Print landmark positions in this image
        for a in annotations.data():
                landmark = Point(loads(a.location))
                print "%s,%s,%d,%d" %(image.originalFilename,d[a.term[0]],landmark.x,image.height-landmark.y)
        





