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

from typing import Any, Dict, Optional, Union

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class CytomineUser:
    def __init__(self) -> None:
        self.username: Optional[str] = None
        self.origin = None

    def keys(self) -> Optional[Union[bool, Dict[str, str]]]:
        # Only works if you are superadmin.
        if hasattr(self, "id") and self.id:
            return Cytomine.get_instance().get(f"user/{self.id}/keys.json")

        return None


class User(Model, CytomineUser):
    def __init__(
        self,
        username: Optional[str] = None,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        language: Optional[str] = None,
        is_developer: Optional[str] = None,
        **attributes: Any,
    ) -> None:
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

    def __str__(self) -> str:
        return f"[{self.callback_identifier}] {self.id} : {self.username}"


class CurrentUser(User):
    def __init__(self) -> None:
        super().__init__()
        self.id = 0
        self.publicKey = None
        self.privateKey = None

    def uri(self) -> str:
        return "user/current.json"

    def keys(self) -> Union[bool, Dict[str, str]]:
        return Cytomine.get_instance().get(f"userkey/{self.publicKey}/keys.json")

    def signature(self) -> Union[bool, Dict[str, str]]:
        return Cytomine.get_instance().get("signature.json")

    def __str__(self) -> str:
        return (
            f"[{self.callback_identifier}] CURRENT USER - {self.id} : {self.username}"
        )


class UserCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, str]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(User, filters, max, offset)
        self._allowed_filters = [None, "project", "ontology"]

        self.admin = None  # Only works with project filter
        self.online = None
        self.publicKey = None

        self.set_parameters(parameters)

    def uri(self, without_filters: bool = False) -> str:
        uri = super().uri(without_filters)
        if "project" in self.filters and self.admin:
            uri = uri.replace("user", "admin")
        return uri


class Role(Model):
    def __init__(self) -> None:
        super().__init__()
        self.authority = None

    def save(self, *args: Any, **kwargs: Any) -> Union[bool, Model]:
        raise NotImplementedError("Cannot save a new role by client.")

    def delete(self, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError("Cannot delete a role by client.")

    def update(self, *args: Any, **kwargs: Any) -> Union[bool, Model]:
        raise NotImplementedError("Cannot update a role by client.")

    def __str__(self) -> str:
        return f"[{self.callback_identifier}] {self.id} : {self.authority}"


class RoleCollection(Collection):
    def __init__(self) -> None:
        super().__init__(Role)
        self._allowed_filters = [None]


class UserRole(Model):
    def __init__(
        self,
        id_user: Optional[int] = None,
        id_role: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.user = id_user
        self.role = id_role
        self.authority = None
        self.populate(attributes)

    @property
    def callback_identifier(self) -> str:
        return "secusersecrole"

    def uri(self) -> str:
        if self.is_new():
            return f"user/{self.user}/role.json"

        return f"user/{self.user}/role/{self.role}.json"

    def fetch(
        self,
        id_user: Optional[int] = None,
        id_role: Optional[int] = None,
    ) -> Union[bool, Model]:
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

    def update(self, *args: Any, **kwargs: Any) -> Union[bool, Model]:
        raise NotImplementedError("Cannot update a user-role.")

    def __str__(self) -> str:
        return (
            f"[{self.callback_identifier}] {self.id} : "
            f"User {self.user} - Role {self.role}"
        )


class UserRoleCollection(Collection):
    def __init__(self, filters: Optional[Dict[str, str]] = None) -> None:
        super().__init__(UserRole, filters)
        self._allowed_filters = ["user"]

    @property
    def callback_identifier(self) -> str:
        return "role"
