# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2022. Authors: see NOTICE file.
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

from cytomine.models.project import *
from cytomine.tests.conftest import random_string

__author__ = "Rubens Ulysse <urubens@uliege.be>"


class TestProject:
    def test_project(self, connect, dataset):
        name = random_string()
        project = Project(name, dataset["ontology"].id).save()
        assert(isinstance(project, Project))
        assert(project.name == name)

        project = Project().fetch(project.id)
        assert(isinstance(project, Project))
        assert(project.name == name)

        name = random_string()
        project.name = name
        project.update()
        assert(isinstance(project, Project))
        assert(project.name == name)

        project.delete()
        assert(not Project().fetch(project.id))

    def test_projects(self, connect, dataset):
        projects = ProjectCollection().fetch()
        assert(isinstance(projects, ProjectCollection))
        
    def test_projects_by_user(self, connect, dataset):
        projects = ProjectCollection().fetch_with_filter("user", dataset["user"].id)
        assert(isinstance(projects, ProjectCollection))
        
    def test_projects_by_ontology(self, connect, dataset):
        projects = ProjectCollection().fetch_with_filter("ontology", dataset["ontology"].id)
        assert(isinstance(projects, ProjectCollection))
        
    def test_projects_by_software(self, connect, dataset):
        projects = ProjectCollection().fetch_with_filter("software", dataset["software"].id)
        assert(isinstance(projects, ProjectCollection))


class TestDiscipline:
    def test_discipline(self, connect, dataset):
        name = random_string()
        discipline = Discipline(name).save()
        assert (isinstance(discipline, Discipline))
        assert (discipline.name == name)

        discipline = Discipline().fetch(discipline.id)
        assert (isinstance(discipline, Discipline))
        assert (discipline.name == name)

        name = random_string()
        discipline.name = name
        discipline.update()
        assert (isinstance(discipline, Discipline))
        assert (discipline.name == name)

        discipline.delete()
        assert (not Discipline().fetch(discipline.id))

    def test_disciplines(self, connect, dataset):
        disciplines = DisciplineCollection().fetch()
        assert (isinstance(disciplines, DisciplineCollection))

        disciplines = DisciplineCollection()
        disciplines.append(Discipline(random_string()))
        assert (disciplines.save())
