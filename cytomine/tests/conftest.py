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

from cytomine.cytomine import Cytomine
from cytomine.models.annotation import Annotation
from cytomine.models.image import AbstractImage, ImageInstance
from cytomine.models.imagegroup import ImageGroup
from cytomine.models.ontology import Ontology, Term
from cytomine.models.project import Project
from cytomine.models.software import Software
from cytomine.models.user import User

__author__ = "Rubens Ulysse <urubens@uliege.be>"


import pytest
import string
import random
import logging


def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def pytest_addoption(parser):
    parser.addoption("--host", action="store")
    parser.addoption("--public_key", action="store")
    parser.addoption("--private_key", action="store")


@pytest.fixture(scope="session")
def connect(request):
    c = Cytomine.connect(request.config.getoption("--host"),
                         request.config.getoption("--public_key"),
                         request.config.getoption("--private_key"),
                         logging.DEBUG)
    return c


@pytest.fixture(scope="session")
def dataset(request):
    data = {}
    data["ontology"] = Ontology(random_string()).save()
    data["term1"] = Term(random_string(), data["ontology"].id, "#000000").save()
    data["term2"] = Term(random_string(), data["ontology"].id, "#000000").save()
    data["project"] = Project(random_string(), data["ontology"].id).save()
    data["abstract_image"] = AbstractImage(random_string(), "tiff").save()
    data["image_instance"] = ImageInstance(data["abstract_image"].id, data["project"].id).save()
    data["annotation"] = Annotation("POLYGON ((0 0, 0 20, 20 20, 20 0, 0 0))", data["image_instance"].id, [data["term1"].id]).save()
    data["image_group"] = ImageGroup(random_string(), data["project"].id).save()
    data["user"] = User(random_string(), random_string(), random_string(), "mail@cytomine.org", random_string()).save()
    data["software"] = Software(random_string(), random_string(), random_string(), random_string()).save()

    def teardown():
        ImageInstance().delete(data["image_instance"].id)
        Annotation().delete(data["annotation"].id)
        ImageGroup().delete(data["image_group"].id)
        AbstractImage().delete(data["abstract_image"].id)
        Term().delete(data["term1"].id)
        Term().delete(data["term2"].id)
        Project().delete(data["project"].id)
        Ontology().delete(data["ontology"].id)
        User().delete(data["user"].id)
        # Software().delete(data["software"].id)
    # request.addfinalizer(teardown)

    return data
