# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2018. Authors: see NOTICE file.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class CytomineUser:
    def __init__(self):
        self.username = None
        self.algo = False


class User(Model, CytomineUser):
    def __init__(self, username=None, firstname=None, lastname=None, email=None, password=None, **attributes):
        super(User, self).__init__()
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.user = None
        self.admin = None
        self.guest = None
        self.populate(attributes)

    def keys(self, public_key):
        return Cytomine.get_instance().get("userkey/{}/keys.json".format(public_key))

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.username)


class CurrentUser(User):
    def __init__(self):
        super(CurrentUser, self).__init__()
        self.id = 0
        self.publicKey = None
        self.privateKey = None

    def uri(self):
        return "user/current.json"

    def signature(self):
        return Cytomine.get_instance().get("signature.json")

    def __str__(self):
        return "[{}] CURRENT USER - {} : {}".format(self.callback_identifier, self.id, self.username)


class UserCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(UserCollection, self).__init__(User, filters, max, offset)
        self._allowed_filters = ["project", "ontology"]

        self.online = None
        self.showJob = None
        self.publicKey = None

        self.set_parameters(parameters)


class UserJob(Model, CytomineUser):
    def __init__(self):
        super(UserJob, self).__init__()
        self.algo = True
        self.humanUsername = None
        self.publicKey = None
        self.privateKey = None
        self.job = None
        self.software = None
        self.project = None
        self.publicKey = None
        self.privateKey = None

    @property
    def callback_identifier(self):
        return "userjob"


class UserJobCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(UserJobCollection, self).__init__(UserJob, filters, max, offset)
        self._allowed_filters = ["project"]

        self.image = None
        self.tree = None

        self.set_parameters(parameters)


class Group(Model):
    def __init__(self, name=None, gid=None, **attributes):
        super(Group, self).__init__()
        self.name = name
        self.gid = gid
        self.populate(attributes)


class GroupCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(GroupCollection, self).__init__(Group, filters, max, offset)
        self.withUser = None
        self.set_parameters(parameters)


class UserGroup(Model):
    def __init__(self, id_user=None, id_group=None, **attributes):
        super(UserGroup, self).__init__()
        self.user = id_user
        self.group = id_group
        self.populate(attributes)

    def uri(self):
        if self.is_new():
            return "user/{}/group.json".format(self.user)
        else:
            return "user/{}/group/{}.json".format(self.user, self.group)

    def fetch(self, id_user=None, id_group=None):
        if self.user is None and id_user is None:
            raise ValueError("Cannot fetch a model with no user ID.")
        elif self.group is None and id_group is None:
            raise ValueError("Cannot fetch a model with no group ID.")

        if id_user is not None:
            self.user = id_user

        if id_group is not None:
            self.group = id_group

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def __str__(self):
        return "[{}] {} : User {} - Group {}".format(self.callback_identifier, self.id, self.user, self.group)


class UserGroupCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(UserGroupCollection, self).__init__(UserGroup, filters, max, offset)
        self._allowed_filters = ["user"]
        self.set_parameters(parameters)


class Role(Model):
    def __init__(self):
        super(Role, self).__init__()
        self.authority = None

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.authority)


class RoleCollection(Collection):
    def __init__(self):
        super(RoleCollection, self).__init__(Role)


class UserRole(Model):
    def __init__(self, id_user=None, id_role=None, **attributes):
        super(UserRole, self).__init__()
        self.user = id_user
        self.role = id_role
        self.authority = None
        self.populate(attributes)

    @property
    def callback_identifier(self):
        return "secusersecrole"

    def uri(self):
        if self.is_new():
            return "user/{}/role.json".format(self.user)
        else:
            return "user/{}/role/{}.json".format(self.user, self.role)

    def fetch(self, id_user=None, id_role=None):
        if self.user is None and id_user is None:
            raise ValueError("Cannot fetch a model with no user ID.")
        elif self.group is None and id_role is None:
            raise ValueError("Cannot fetch a model with no role ID.")

        if id_user is not None:
            self.user = id_user

        if id_role is not None:
            self.role = id_role

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def __str__(self):
        return "[{}] {} : User {} - Role {}".format(self.callback_identifier, self.id, self.user, self.role)


class UserRoleCollection(Collection):
    def __init__(self, filters=None):
        super(UserRoleCollection, self).__init__(UserRole, filters)
        self._allowed_filters = ["user"]
