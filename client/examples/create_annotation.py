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
from shapely.geometry.polygon import Polygon
from shapely.geometry import Polygon,Point,box


#Cytomine connection parameters
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"


#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#Replace XXX by your values
id_image=XXX
id_term=XXX


#Create one geometrical object locally (using shapely)
#circle = Point(100,100).buffer(1000)
#annotation.location=circle.wkt
#rectangle = box(100, 100, 200, 200, ccw=True)
#annotation.location=rectangle.wkt
point = Point(1000,1000)  #point at position (1000,1000) where (0,0) is bottom left corner
annotation.location=point.wkt

#Add annotation to cytomine server
new_annotation = conn.add_annotation(annotation.location, id_image)
#Add term from the project's ontology
conn.add_user_annotation_term(new_annotation.id, term=id_term)
#Add property,value to the annotation
annotation_property = conn.add_annotation_property(new_annotation.id, "my_property", 10)
