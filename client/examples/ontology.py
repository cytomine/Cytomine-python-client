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



from cytomine import *
import logging


#Replace connection XXX parameters
cytomine_host="XXX"
cytomine_public_key="XXX"
cytomine_private_key="XXX"


#Connection to Cytomine Core
conn = Cytomine(cytomine_host, cytomine_public_key, cytomine_private_key, base_path = '/api/', working_path = '/tmp/', verbose= True)


#To create a new ontology with the following term structure:
# TERM1
# CATEGORY1
#    TERM2
#    TERM3
ontology = conn.add_ontology("_MY_ONTOLOGY_NAME_")
term1 = conn.add_term("TERM1", ontology.id, "#00FF00")
cat1 = conn.add_term("CATEGORY1", ontology.id, "#000000")
term2 = conn.add_term("TERM2", ontology.id, "#FF0000")
term3 = conn.add_term("TERM3", ontology.id, "#0000FF")
conn.add_relation_term(cat1.id, term2.id)
conn.add_relation_term(cat1.id, term3.id)

#Methods in order to delete term, relation and ontology. 
#Note that delete_ontology method will automatically delete everything	
#conn.delete_relation_term(cat1.id, term2.id)	
#conn.delete_term(term2.id)
#conn.delete_ontology(ontology.id)

