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
__copyright__       = "Copyright 2010-2016 University of Liège, Belgium, http://www.cytomine.be/"


from cytomine import Cytomine
from cytomine.models import *

#Cytomine connection parameters
cytomine_host=""
cytomine_public_key=""
cytomine_private_key=""
#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)



#Adapt with your parameters
id_project=10529443 #project id
new_magnification=40 #new image magnification
new_resolution=0.65 #new image resolution


#Get image instances from project
image_instances = ImageInstanceCollection()
image_instances.project  =  id_project
image_instances  =  conn.fetch(image_instances)
images = image_instances.data()
print "Nb images in project: %d" %len(images)

for image in images:
	print image
	abstractimage = conn.get_image(image.baseImage)
	conn.edit_image(image.baseImage,magnification=new_magnification,resolution=new_resolution)
	abstractimage = conn.get_image(image.baseImage)
	#print "after: %d" %abstractimage.magnification
