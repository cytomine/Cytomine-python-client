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
import cytomine.models
import time


#Replace XXX values by your values
# the web url of cytomine instance, always without the  protocol
# your public & private keys of your account on Cytomine (can be found on your Account details on Cytomine)
protocol = 'http://'
cytomine_core_path="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"
#the web url of cytomine upload server, always without the  protocol
cytomine_IMS_path = 'XXX'

# the absolute local path of the image to upload
file_path = '/home/XXX/test.jpg'
file_path_2 = '/home/XXX/test2.jpg'


# the storage_id of your user, see http://$CORE_URL/api/storage.json
id_storage = XXX

# if you want that images be linked automatically with a project, set the ID of the project otherwise use None
id_project = XXX # optional

# check connection to the Cytomine instance
core_conn = Cytomine(cytomine_core_path,cytomine_public_key,cytomine_private_key, verbose= False)
# check that the storage exists
storage = core_conn.get_storage(id_storage)
assert(storage.id == id_storage) 
if (id_project):
    project = core_conn.get_project(id_project)
    assert(project.id == id_project)
# at this point, we are sure that the parameters for the Cytomine instance works 
# and that the storage and the project (if provided) exists                                  

# create the connection to the image management system (where you upload the images)
ims_conn = Cytomine(cytomine_IMS_path, cytomine_public_key, cytomine_private_key, verbose= False)

# the properties/metadata you want to attach to the image 
properties = {'key1':'value1','key2':'value2'}

##################  
# OPTION 1 (SYNC UPLOAD)
# With Sync = True, the server will answer once everything (copy, convert, deploy) is done the server
# Therefore, you receive directly the UPLOADED_FILE with the ID of the created image
# END OF OPTION 1
##################   
sync = True
response = ims_conn.upload_image(file_path_2, id_project, id_storage, "%s%s" % (protocol, cytomine_core_path), sync, properties) #sync True 
uploaded_file_info = response.get('uploaded_file')
uploaded_file_id = uploaded_file_info.get('id')
uploaded_file = core_conn.get_uploaded_file(uploaded_file_id)
assert(uploaded_file.image)
image_properties = core_conn.get_abstract_image_properties(uploaded_file.image)
print "OK (sync)"


##################  
# OPTION 2 (ASYNC UPLOAD)
# the server will give you an answer as soon as it received the file you uploaded. 
# The others operations (copy, convert, deploy) are done in a asynchronously way.  
# The response contains the ID of an UPLOADED_FILE that allow you to check the status.
sync = False
response = ims_conn.upload_image(file_path, id_project, id_storage, "%s%s" % (protocol, cytomine_core_path), sync, properties ) #sync False (async)

assert(response.get('status') == 200) #uploaded worked as expected
uploaded_file_info = response.get('uploaded_file')
uploaded_file_id = uploaded_file_info.get('id')
uploaded_file = core_conn.get_uploaded_file(uploaded_file_id)
while (not(uploaded_file.image)):
    time.sleep(3) #wait 10 seconds    
    uploaded_file = core_conn.get_uploaded_file(uploaded_file_id)    
#we have the image. let's verify if we can recover the properties
image_properties = core_conn.get_abstract_image_properties(uploaded_file.image)





