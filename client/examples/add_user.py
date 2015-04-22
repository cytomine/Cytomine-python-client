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
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium"



from cytomine import Cytomine


#Connection parameters to Cytomine
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"
id_project=0
#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#Local list of users to create
users = [
	{'username' : 'demo1', 'firstname' : 'Demo', 'lastname' : 'Demo1', 'email' : 'demo@demo.fr', 'password' : 'demo2015'},
	{'username' : 'demo2', 'firstname' : 'Demo', 'lastname' : 'Demo2', 'email' : 'demo@demo.fr', 'password' : 'demo2015'},
]

#Roles attributed to users
role_user = conn.get_roles("ROLE_USER")
assert(role_user.authority == "ROLE_USER")
#role_admin = conn.get_roles("ROLE_ADMIN")
#assert(role_admin.authority == "ROLE_ADMIN")
#role_super_admin = conn.get_roles("ROLE_SUPER_ADMIN")
#assert(role_super_admin.authority == "ROLE_SUPER_ADMIN")
#role_guest = conn.get_roles("ROLE_GUEST")
#assert(role_guest.authority == "ROLE_GUEST")

#Local listing
for user_data in users:	
	print "%s %s : %s / %s" % (user_data['firstname'],user_data['lastname'], user_data['username'], user_data['password'])

#Create users on cytomine and attribute role and storage
for user_data in users:	
    user = conn.add_user(user_data['username'],user_data['firstname'],user_data['lastname'],user_data['email'],user_data['password'])
    if user:
        user_role = conn.add_user_role(user.id, role_user.id)
#        user_role = conn.add_user_role(user.id, role_admin.id)
        conn.init_storage_for_user(user.id)
        print "%s %s : %s / %s" % (user_data['firstname'],user_data['lastname'], user_data['username'], user_data['password'])


#Other operations
#delete USER role
#user_role = conn.delete_user_role(user.id, role_user.id)
#add ADMIN role
#user_role = conn.add_user_role(user.id, role_admin.id)
#delete ADMIN role
#user_role = conn.delete_user_role(user.id, role_admin.id)
#DELETE user
#conn.delete_user(user.id)


##Add user job (a running instance of a cytomine software)
#id_software=XXX
#your_parameters['key'] = "value"
#user_job = conn.add_user_job(id_software, id_project)
##Switch to job credentials
#conn.set_credentials(str(user_job.publicKey), str(user_job.privateKey))
#job = conn.get_job(user_job.job)  
##Set job parameter values (must be compatible with software parameter definition)
#parameters_values = conn.add_job_parameters(user_job.job, conn.get_software(id_software), your_parameters)
##Update job status (visible in Cytomine web UI)
#job = conn.update_job_status(job, status = job.RUNNING, status_comment = "Run...", progress = 0)
#job = conn.update_job_status(job, status = job.TERMINATED, status_comment = "Finish", progress = 100)
