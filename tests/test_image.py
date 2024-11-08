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

import pytest

from cytomine.models import (
    AbstractImage,
    AbstractImageCollection,
    AbstractSlice,
    AbstractSliceCollection,
    ImageInstance,
    ImageInstanceCollection,
    SliceInstance,
    SliceInstanceCollection,
)
from tests.conftest import random_string


class TestAbstractImage:
    def test_abstract_image(self, connect, dataset):
        filename = random_string()
        abstract_image = AbstractImage(filename, dataset["uploaded_file"].id).save()
        assert isinstance(abstract_image, AbstractImage)
        assert abstract_image.filename == filename

        abstract_image = AbstractImage().fetch(abstract_image.id)
        assert isinstance(abstract_image, AbstractImage)
        assert abstract_image.filename == filename

        abstract_image = AbstractImage().fetch(abstract_image.id)
        assert isinstance(abstract_image, AbstractImage)
        assert abstract_image.filename == filename

        # TODO: problem of access rights in core prevent the successful execution of following tests
        # filename = random_string()
        # abstract_image.filename = filename
        # abstract_image.update()
        # assert (isinstance(abstract_image, AbstractImage))
        # assert (abstract_image.filename == filename)
        #
        # abstract_image.delete()
        # assert (not AbstractImage().fetch(abstract_image.id))

    def test_abstract_image_server(self, connect, dataset):
        # TODO
        pass

    def test_abstract_image_download(self, connect, dataset):
        # TODO
        pass

    def test_abstract_images(self, connect, dataset):
        abstract_images = AbstractImageCollection().fetch()
        assert isinstance(abstract_images, AbstractImageCollection)


class TestImageInstance:
    def test_image_instance(self, connect, dataset):
        image_instance = ImageInstance(
            dataset["abstract_image3"].id,
            dataset["project"].id,
        ).save()
        assert isinstance(image_instance, ImageInstance)

        image_instance = ImageInstance().fetch(image_instance.id)
        assert isinstance(image_instance, ImageInstance)

        image_instance.instanceFilename = "filename"
        image_instance.update()
        assert isinstance(image_instance, ImageInstance)
        assert image_instance.instanceFilename == "filename"

        image_instance.delete()
        assert not ImageInstance().fetch(image_instance.id)

    def test_image_instance_server(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_download(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_dump(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_by_project(
        self,
        connect,
        dataset,
    ):
        image_instances = ImageInstanceCollection().fetch_with_filter(
            "project",
            dataset["project"].id,
        )
        assert isinstance(image_instances, ImageInstanceCollection)


class TestAbstractSlice:
    def test_abstract_slice(self, connect, dataset):
        abstract_slice = AbstractSlice(
            dataset["abstract_image2"].id,
            dataset["uploaded_file2"].id,
            "image/pyrtiff",
            0,
            0,
            0,
        ).save()
        assert isinstance(abstract_slice, AbstractSlice)

        abstract_slice = AbstractSlice().fetch(abstract_slice.id)
        assert isinstance(abstract_slice, AbstractSlice)

    def test_abstract_slices_by_abstract_image(
        self,
        connect,
        dataset,
    ):
        abstract_slices = AbstractSliceCollection().fetch_with_filter(
            "abstractimage",
            dataset["abstract_image"].id,
        )
        assert isinstance(abstract_slices, AbstractSliceCollection)

    def test_abstract_slices_by_uploadedfile(
        self,
        connect,
        dataset,
    ):
        abstract_slices = AbstractSliceCollection().fetch_with_filter(
            "uploadedfile",
            dataset["uploaded_file"].id,
        )
        assert isinstance(abstract_slices, AbstractSliceCollection)


class TestSliceInstance:
    @pytest.mark.skip(
        reason=(
            "SliceInstance object automatically created when creating ImageInstance object, "
            "so trying to create a slice instance based on the image instance returns a 409 code"
        )
    )
    def test_slice_instance(self, connect, dataset):
        slice_instance = SliceInstance(
            dataset["project"].id,
            dataset["image_instance2"].id,
            dataset["abstract_slice2"].id,
        ).save()
        assert isinstance(slice_instance, SliceInstance)

        slice_instance = SliceInstance().fetch(slice_instance.id)
        assert isinstance(slice_instance, SliceInstance)

        slice_instance.filename = "filename"
        slice_instance.update()
        assert isinstance(slice_instance, SliceInstance)
        assert slice_instance.filename == "filename"

        slice_instance.delete()
        assert not SliceInstance.fetch(slice_instance.id)

    def test_slices_by_image(self, connect, dataset):
        slices = SliceInstanceCollection().fetch_with_filter(
            "imageinstance",
            dataset["image_instance"].id,
        )
        assert isinstance(slices, SliceInstanceCollection)
