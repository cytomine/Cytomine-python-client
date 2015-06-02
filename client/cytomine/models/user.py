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

class User(Model):

    def __init__(self, params = None):
        super(User, self).__init__(params)
        self._callback_identifier = "user"

    def to_url(self):
        if hasattr(self, "id"):
            return "user/%d.json" % self.id
        elif hasattr(self, "software"):
            self._callback_identifier = "userJob"
            return "userJob.json"
        elif hasattr(self, "current"):
            return "user/current.json"
        else:
            return "user.json"

    def __str__( self ):
        return "User : " + str(self.id)

class Group(Model):

    def __init__(self, params = None):
        super(Group, self).__init__(params)
        self._callback_identifier = "group"

    def to_url(self):
        if hasattr(self, "id"):
            return "group/%d.json" % self.id
        else:
            return "group.json"

    def __str__( self ):
        return "group : " + str(self.id)

class UserGroup(Model):

    def __init__(self, params = None):
        super(UserGroup, self).__init__(params)
        self._callback_identifier = "usergroup"

    def to_url(self):
        if hasattr(self, "user") and not hasattr(self, "id"):#new
            return "user/%d/group.json" % self.user
        elif hasattr(self, "user") and hasattr(self, "group"):
            return "user/%d/group/%d.json" % (self.user, self.group)
        elif not hasattr(self, "user") and hasattr(self, "group") :
            return "group/%d.json" % self.group

    def __str__( self ):
        return "UserGroup : " + str(self.id)

class Role(Model):

    def __init__(self, params = None):
        super(Role, self).__init__(params)        

    def to_url(self):
        if hasattr(self, "id"):
            return "role/%d.json" % self.id
        else:
            return "role.json"

    def __str__( self ):
        return "Role : " + str(self.id)    

class UserRole(Model):
    def __init__(self, params = None):
        super(UserRole, self).__init__(params)        
        self._callback_identifier = "secusersecrole"
        
    def to_url(self):
        if hasattr(self, "user") and not hasattr(self, "id"):#new
            return "user/%d/role.json" % self.user
        elif hasattr(self, "user") and hasattr(self, "role"):
            return "user/%d/role/%d.json" % (self.user, self.role)
        
    def __str__( self ):
        return "UserRole : " + str(self.id)     

class GroupCollection(Collection):
    def __init__(self, params = None):
        super(GroupCollection, self).__init__(Group, params)

    def to_url(self):
        if hasattr(self, "group"):
            return "group/" + str(self.group) + ".json"
        else:
            return "group.json"

class UserRoleCollection(Collection):
    def __init__(self, params = None):
        super(UserRoleCollection, self).__init__(UserRole, params)

    def to_url(self):
        return "user/%d/role.json" % self.user

class RoleCollection(Collection):
    def __init__(self, params = None):
        super(RoleCollection, self).__init__(Role, params)

    def to_url(self):
        return "role.json"

class UserCollection(Collection):
    def __init__(self, params = None):
        super(UserCollection, self).__init__(User, params)

    def to_url(self):
        return "user.json"                        
