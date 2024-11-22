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

from typing import Any, Dict

from cytomine.cytomine import Cytomine
from cytomine.models import Project, ProjectCollection
from tests.conftest import random_string


class TestProject:
    def test_project(self, connect: Cytomine, dataset: Dict[str, Any]) -> None:
        name = random_string()
        project = Project(name, dataset["ontology"].id).save()
        assert isinstance(project, Project)
        assert project.name == name

        project = Project().fetch(project.id)
        assert isinstance(project, Project)
        assert project.name == name

        name = random_string()
        project.name = name
        project.update()
        assert isinstance(project, Project)
        assert project.name == name

        project.delete()
        assert not Project().fetch(project.id)

    def test_projects(self, connect: Cytomine, dataset: Dict[str, Any]) -> None:
        projects = ProjectCollection().fetch()
        assert isinstance(projects, ProjectCollection)

    def test_projects_by_user(
        self,
        connect: Cytomine,
        dataset: Dict[str, Any],
    ) -> None:
        projects = ProjectCollection().fetch_with_filter("user", dataset["user"].id)
        assert isinstance(projects, ProjectCollection)

    def test_projects_by_ontology(
        self,
        connect: Cytomine,
        dataset: Dict[str, Any],
    ) -> None:
        projects = ProjectCollection().fetch_with_filter(
            "ontology",
            dataset["ontology"].id,
        )
        assert isinstance(projects, ProjectCollection)
