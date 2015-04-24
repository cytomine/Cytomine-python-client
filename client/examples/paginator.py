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
from cytomine.models import ProjectCollection
from cytomine.models import Collection
import logging


cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"

#establish a Cytomine connection
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#create a new Collection
projects = ProjectCollection()

#init paginator method: 
# - First argument is the number of result per page. 
# - The second is the page index
#if not used, the fetch() returns the full collection into one page
projects.init_paginator(10, 0)


#This will request "pages" (per 10) of projects
while True: 
    projects  = conn.fetch(projects)
    if not(projects.next_page()):
        break

