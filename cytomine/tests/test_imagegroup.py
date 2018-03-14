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

from cytomine.models.imagegroup import *
from cytomine.tests.conftest import random_string

__author__ = "Rubens Ulysse <urubens@uliege.be>"


class TestImageGroup:
    def test_imagegroup(self, connect, dataset):
        name = random_string()
        imagegroup = ImageGroup(name, dataset["project"].id).save()
        assert (isinstance(imagegroup, ImageGroup))
        assert (imagegroup.name == name)

        imagegroup = ImageGroup().fetch(imagegroup.id)
        assert (isinstance(imagegroup, ImageGroup))
        assert (imagegroup.name == name)

        name = random_string()
        imagegroup.name = name
        imagegroup.update()
        assert (isinstance(imagegroup, ImageGroup))
        assert (imagegroup.name == name)

        imagegroup.delete()
        assert (not ImageGroup().fetch(imagegroup.id))

    def test_imagegroup_characteristics(self, connect, dataset):
        characteristics = ImageGroup().fetch(dataset["image_group"].id).characteristics()
        assert (isinstance(characteristics, dict))
        assert ("channel" in characteristics)

    def test_imagegroups_by_project(self, connect, dataset):
        imagegroups = ImageGroupCollection().fetch_with_filter("project", dataset["project"].id)
        assert (isinstance(imagegroups, ImageGroupCollection))


class TestImageGroupHDF5:
    # TODO: requires an image group with image sequence inside.
    # def test_imagegroupHDF5(self, connect, dataset):
    #     filename = random_string()
    #     imagegroupHDF5 = ImageGroupHDF5(dataset["image_group"].id, filename).save()
    #     assert (isinstance(imagegroupHDF5, ImageGroupHDF5))
    #     assert (imagegroupHDF5.filename == filename)
    #
    #     imagegroupHDF5 = ImageGroupHDF5().fetch(imagegroupHDF5.id)
    #     assert (isinstance(imagegroupHDF5, ImageGroupHDF5))
    #     assert (imagegroupHDF5.filename == filename)
    #
    #     filename = random_string()
    #     imagegroupHDF5.filename = filename
    #     imagegroupHDF5.update()
    #     assert (isinstance(imagegroupHDF5, ImageGroupHDF5))
    #     assert (imagegroupHDF5.filename == filename)
    #
    #     imagegroupHDF5.delete()
    #     assert (not ImageGroupHDF5().fetch(imagegroupHDF5.id))

    def test_imagegroupHDF5_pixel(self, connect, dataset):
        pass

    def test_imagegroupHDF5_rectangle(self, connect, dataset):
        pass

    # def test_imagegroupHDF5s_by_project(self, connect, dataset):
    #     imagegroupHDF5s = ImageGroupHDF5Collection().fetch_with_filter("project", dataset["project"].id)
    #     assert (isinstance(imagegroupHDF5s, ImageGroupHDF5Collection))


class TestImageSequence:
    def test_image_sequence(self, connect, dataset):
        channel = 10
        image_sequence = ImageSequence(dataset["image_group"].id, dataset["image_instance"].id, 0, 0, 0, channel).save()
        assert (isinstance(image_sequence, ImageSequence))
        assert (image_sequence.channel == channel)

        image_sequence = ImageSequence().fetch(image_sequence.id)
        assert (isinstance(image_sequence, ImageSequence))
        assert (image_sequence.channel == channel)

        channel += 3
        image_sequence.channel = channel
        image_sequence.update()
        assert (isinstance(image_sequence, ImageSequence))
        assert (image_sequence.channel == channel)

        # TODO: Cytomine-core delete image instance and abstract image in cascade !!
        # image_sequence.delete()
        # assert (not ImageSequence().fetch(image_sequence.id))

    def test_image_sequences_by_imagegroup(self, connect, dataset):
        image_sequences = ImageSequenceCollection().fetch_with_filter("imagegroup", dataset["image_group"].id)
        assert (isinstance(image_sequences, ImageSequenceCollection))

    def test_image_sequences_by_imageinstance(self, connect, dataset):
        image_sequences = ImageSequenceCollection().fetch_with_filter("imageinstance", dataset["image_instance"].id)
        assert (isinstance(image_sequences, ImageSequenceCollection))