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

# pylint: disable=unused-argument

from cytomine.models import (
    CurrentUser,
    Role,
    RoleCollection,
    User,
    UserCollection,
    UserRole,
    UserRoleCollection,
)
from tests.conftest import random_string


class TestUser:
    def test_user(self, connect, dataset):
        name = random_string()
        user = User(
            name,
            random_string(),
            random_string(),
            "mail@cytomine.be",
            random_string(),
        ).save()
        assert isinstance(user, User)
        assert user.username == name

        user = User().fetch(user.id)
        assert isinstance(user, User)
        assert user.username == name

        name = random_string()
        user.username = name
        user.update()
        assert isinstance(user, User)
        assert user.username == name

        user.delete()
        assert not User().fetch(user.id)

    def test_users(self, connect, dataset):
        users = UserCollection().fetch()
        assert isinstance(users, UserCollection)

        users = UserCollection()
        users.append(
            User(
                random_string(),
                random_string(),
                random_string(),
                "mail@cytomine.be",
                random_string(),
            )
        )
        assert users.save()

    def test_users_by_project(self, connect, dataset):
        users = UserCollection().fetch_with_filter("project", dataset["project"].id)
        assert isinstance(users, UserCollection)

    def test_users_by_ontology(self, connect, dataset):
        users = UserCollection().fetch_with_filter("ontology", dataset["ontology"].id)
        assert isinstance(users, UserCollection)


class TestCurrentUser:
    def test_current_user(self, connect, dataset):
        user = CurrentUser().fetch()
        assert isinstance(user, CurrentUser)
        assert user.__dict__ == connect.current_user.__dict__

    def test_current_user_keys(self, connect, dataset):
        keys = connect.current_user.keys()
        assert keys["privateKey"] == connect.current_user.privateKey

    def test_current_user_signature(self, connect, dataset):
        assert connect.current_user.signature()


class TestRole:
    def test_roles(self, connect, dataset):
        roles = RoleCollection().fetch()
        assert isinstance(roles, RoleCollection)

    def test_role(self, connect, dataset):
        roles = RoleCollection().fetch()
        if len(roles) > 0:
            role = Role().fetch(roles[0].id)
            assert isinstance(role, Role)
            assert role.id == roles[0].id


class TestUserRole:
    def test_user_role(self, connect, dataset):
        roles = RoleCollection().fetch()
        if len(roles) > 0:
            user_role = UserRole(dataset["user"].id, roles[-1].id).save()
            assert isinstance(user_role, UserRole)
            assert user_role.user == dataset["user"].id

            user_role = UserRole().fetch(dataset["user"].id, roles[-1].id)
            assert isinstance(user_role, UserRole)

            user_role.delete()
            assert not UserRole().fetch(dataset["user"].id, roles[-1].id)

    # def test_user_roles(self, connect, dataset):
    #     user_roles = UserRoleCollection().fetch()
    #     assert(isinstance(user_roles, UserRoleCollection))

    def test_user_roles_by_user(self, connect, dataset):
        user_roles = UserRoleCollection().fetch_with_filter("user", dataset["user"].id)
        assert isinstance(user_roles, UserRoleCollection)
