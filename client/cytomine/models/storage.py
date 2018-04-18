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

class Storage(Model):

    def __init__(self, params = None):
        super(Storage, self).__init__(params)
        self._callback_identifier = "storage"

    def to_url(self):
        if hasattr(self, "id"):
            return "storage/%d.json" % self.id
        else:
            return "storage.json"

    def __str__( self ):
        return str(self.id) + " : " + str(self.name)
        
class UploadedFile(Model):
    def __init__(self, params = None):
        super(UploadedFile, self).__init__(params)
        self._callback_identifier = "uploadedfile"

    def to_url(self):
        if hasattr(self, "id"):
            return "uploadedfile/%d.json" % self.id
        else:
            return "uploadedfile.json"

    def __str__( self ):
        return "Uploadedfile : " + str(self.id)


class AttachedFile(Model):
    def __init__(self, params=None):
        super(AttachedFile, self).__init__(params)
        self._callback_identifier = "attachedfile"

    def to_url(self):
        if hasattr(self, "id"):
            return "attachedfile/%d.json" % self.id
        else:
            return "attachedfile.json"

    def __str__(self):
        return "AttachedFile : " + str(self.id) + " " + str(self.filename)


class AttachedFileCollection(Collection):
    def __init__(self, params=None):
        super(AttachedFileCollection, self).__init__(AttachedFile, params)

    def to_url(self):
        if hasattr(self, "domainClassName") and hasattr(self, "domainIdent"):
            return "domain/{}/{}/attachedfile.json".format(self.domainClassName, self.domainIdent)
        return "attachedfile.json"
