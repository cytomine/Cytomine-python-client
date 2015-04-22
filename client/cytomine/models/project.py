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


from model import Model
from collection import Collection

class Project(Model):

    def __init__(self, params = None):
        super(Project, self).__init__(params)
        self._callback_identifier = "project"

    def to_url(self):
        if hasattr(self, "id"):
            return "project/%d.json" % self.id
        else:
            return "project.json"

    def __str__( self ):
        return "%s : %s " % (self.id, self.name)

class ProjectCollection(Collection):

    def __init__(self, params = None):
        super(ProjectCollection, self).__init__(Project, params)

    def to_url(self):
        return "project.json"



class ProjectProperty(Model):

    def __init__(self, params = None):
        super(ProjectProperty, self).__init__(params)
        self._callback_identifier = "property"

    def to_url(self):
        if (hasattr(self, "domainIdent") and not hasattr(self, "id")):#new
            return "project/%d/property.json" % self.domainIdent
        elif (hasattr(self, "domainIdent") and hasattr(self, "id")):
            return "project/%d/property/%d.json" % (self.domainIdent, self.id)        

    def __str__( self ):
        return "Project Property %d,%d " % (self.project, self.id)        
