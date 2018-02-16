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


#Replace connection XXX parameters
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"

#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#Replace XXX with Identifiers of image, project, annotation
annotation_id = XXX
image_id = XXX
project_id = XXX


#Methods to add properties to an existing annotation
#add
annotation_property = conn.add_annotation_property(annotation_id, "key_prop", "value_prop")
assert annotation_property != None
#get one property
annotation_property2 = conn.get_annotation_property(annotation_id, annotation_property.id)
assert annotation_property != None
#get property collection
annotation_properties = conn.get_annotation_properties(annotation_id)
for annotation_property in annotation_properties.data():
	print "%s => %s" % (annotation_property.key, annotation_property.value)
#edit
annotation_property = conn.edit_annotation_property(annotation_id, annotation_property.id, "key_prop", "value_prop2")
assert annotation_property != None
#delete
#success = annotation_property = conn.delete_annotation_property(annotation_id, annotation_property.id)
#assert(success == True)

