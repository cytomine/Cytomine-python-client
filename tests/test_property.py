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

import os

from cytomine.models import (
    AttachedFile,
    AttachedFileCollection,
    Description,
    Property,
    PropertyCollection,
    Tag,
    TagCollection,
    TagDomainAssociation,
    TagDomainAssociationCollection,
)
from tests.conftest import random_string


class TestProperty:
    def test_property(self, connect, dataset):
        value = random_string()
        property = Property(  # pylint: disable=redefined-builtin
            dataset["project"],
            "key",
            value,
        ).save()
        assert isinstance(property, Property)
        assert property.value == value

        property = Property(dataset["project"]).fetch(property.id)
        assert isinstance(property, Property)
        assert property.value == value

        property = Property(dataset["project"]).fetch(key="key")
        assert isinstance(property, Property)
        assert property.value == value

        value = random_string()
        property.value = value
        property.update()
        assert isinstance(property, Property)
        assert property.value == value

        property.delete()
        assert not Property(dataset["project"]).fetch(property.id)

    def test_properties(self, connect, dataset):
        properties = PropertyCollection(dataset["project"]).fetch()
        assert isinstance(properties, PropertyCollection)


class TestAttachedFile:
    def test_attached_file(self, connect, dataset):
        filename = os.path.dirname(__file__) + "/data/attached_file.txt"
        filename_base = os.path.basename(filename)
        attached_file = AttachedFile(dataset["project"], filename).save()
        assert isinstance(attached_file, AttachedFile)
        assert attached_file.filename == filename_base

        attached_file = AttachedFile(dataset["project"]).fetch(attached_file.id)
        assert isinstance(attached_file, AttachedFile)
        assert attached_file.filename == filename_base

        # TODO: Download

        # filename = "data/attached_file2.txt"
        # filename_base = os.path.basename(filename)
        # attached_file.filename = filename
        # attached_file.update()
        # assert (isinstance(attached_file, AttachedFile))
        # assert (attached_file.filename == filename_base)

        # TODO: No delete on Cytomine-core
        # attached_file.delete()
        # assert (not AttachedFile(dataset["project"]).fetch(attached_file.id))

    def test_attached_files(self, connect, dataset):
        attached_files = AttachedFileCollection(dataset["project"]).fetch()
        assert isinstance(attached_files, AttachedFileCollection)


class TestDescription:
    def test_description(self, connect, dataset):
        data = random_string()
        description = Description(dataset["project"], data).save()
        assert isinstance(description, Description)
        assert description.data == data

        description = Description(dataset["project"]).fetch(description.id)
        assert isinstance(description, Description)
        assert description.data == data

        data = random_string()
        description.data = data
        description.update()
        assert isinstance(description, Description)
        assert description.data == data

        description.delete()
        assert not Description(dataset["project"]).fetch(description.id)


class TestTag:
    def test_tag(self, connect, dataset):
        name = random_string()
        tag = Tag(name).save()
        assert isinstance(tag, Tag)
        assert tag.name == name

        tag = Tag().fetch(tag.id)
        assert isinstance(tag, Tag)
        assert tag.name == name

        name = random_string()
        tag.name = name
        tag.update()
        assert isinstance(tag, Tag)
        assert tag.name == name

        tag.delete()
        assert not Tag().fetch(tag.id)

        tag = Tag().save()
        assert tag is False

    def test_tags(self, connect, dataset):
        tags = TagCollection().fetch()
        assert isinstance(tags, TagCollection)


class TestTagDomainAssociation:
    def test_tag_domain_association(self, connect, dataset):
        tda = TagDomainAssociation(dataset["project"], dataset["tag"].id).save()
        assert isinstance(tda, TagDomainAssociation)
        assert tda.tag == dataset["tag"].id
        assert tda.domainIdent == dataset["project"].id

        tag = TagDomainAssociation(dataset["project"]).fetch(tda.id)
        assert isinstance(tag, TagDomainAssociation)
        assert tag.domainIdent == dataset["project"].id

        tda.delete()
        assert not TagDomainAssociation(dataset["project"]).fetch(tda.id)

    def test_tag_domain_association_by_projects(self, connect, dataset):
        tags = TagDomainAssociationCollection(dataset["project"]).fetch()
        assert isinstance(tags, TagDomainAssociationCollection)
