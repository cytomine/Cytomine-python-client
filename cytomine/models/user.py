# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2024. Authors: see NOTICE file.
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

# pylint: disable=invalid-name

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class CytomineUser:
    def __init__(self):
        self.username = None
        self.origin = None

    def keys(self):
        # Only works if you are superadmin.
        if hasattr(self, "id") and self.id:
            return Cytomine.get_instance().get(f"user/{self.id}/keys.json")

        return None


class User(Model, CytomineUser):
    def __init__(
        self,
        username=None,
        firstname=None,
        lastname=None,
        email=None,
        password=None,
        language=None,
        is_developer=None,
        **attributes,
    ):
        super().__init__()
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.language = language
        self.isDeveloper = is_developer
        self.user = None
        self.admin = None
        self.guest = None
        self.populate(attributes)

    def __str__(self):
        return f"[{self.callback_identifier}] {self.id} : {self.username}"


class CurrentUser(User):
    def __init__(self):
        super().__init__()
        self.id = 0
        self.publicKey = None
        self.privateKey = None

    def uri(self):
        return "user/current.json"

    def keys(self):
        return Cytomine.get_instance().get(f"userkey/{self.publicKey}/keys.json")

    def signature(self):
        return Cytomine.get_instance().get("signature.json")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] CURRENT USER - {self.id} : {self.username}"
        )


class UserCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(User, filters, max, offset)
        self._allowed_filters = [None, "project", "ontology"]

        self.admin = None  # Only works with project filter
        self.online = None
        self.publicKey = None

        self.set_parameters(parameters)

    def uri(self, without_filters=False):
        uri = super().uri(without_filters)
        if "project" in self.filters and self.admin:
            uri = uri.replace("user", "admin")
        return uri


class Role(Model):
    def __init__(self):
        super().__init__()
        self.authority = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a new role by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete a role by client.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a role by client.")

    def __str__(self):
        return f"[{self.callback_identifier}] {self.id} : {self.authority}"


class RoleCollection(Collection):
    def __init__(self):
        super().__init__(Role)
        self._allowed_filters = [None]


class UserRole(Model):
    def __init__(self, id_user=None, id_role=None, **attributes):
        super().__init__()
        self.user = id_user
        self.role = id_role
        self.authority = None
        self.populate(attributes)

    @property
    def callback_identifier(self):
        return "secusersecrole"

    def uri(self):
        if self.is_new():
            return f"user/{self.user}/role.json"

        return f"user/{self.user}/role/{self.role}.json"

    def fetch(self, id_user=None, id_role=None):
        self.id = -1

        if self.user is None and id_user is None:
            raise ValueError("Cannot fetch a model with no user ID.")

        if self.role is None and id_role is None:
            raise ValueError("Cannot fetch a model with no role ID.")

        if id_user is not None:
            self.user = id_user

        if id_role is not None:
            self.role = id_role

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a user-role.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] {self.id} : "
            f"User {self.user} - Role {self.role}"
        )


class UserRoleCollection(Collection):
    def __init__(self, filters=None):
        super().__init__(UserRole, filters)
        self._allowed_filters = ["user"]

    @property
    def callback_identifier(self):
        return "role"
