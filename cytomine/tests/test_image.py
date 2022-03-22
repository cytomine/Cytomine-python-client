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

from cytomine.models.image import *
from cytomine.tests.conftest import random_string

__author__ = "Rubens Ulysse <urubens@uliege.be>"


class TestAbstractImage:
    def test_abstract_image(self, connect, dataset):
        filename = random_string()
        abstract_image = AbstractImage(filename, dataset["uploaded_file"].id).save()
        assert (isinstance(abstract_image, AbstractImage))
        assert (abstract_image.filename == filename)

        abstract_image = AbstractImage().fetch(abstract_image.id)
        assert (isinstance(abstract_image, AbstractImage))
        assert (abstract_image.filename == filename)

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
        assert (isinstance(abstract_images, AbstractImageCollection))
    
    
class TestImageInstance:
    def test_image_instance(self, connect, dataset):
        image_instance = ImageInstance(dataset["abstract_image"].id, dataset["project"].id).save()
        assert (isinstance(image_instance, ImageInstance))

        image_instance = ImageInstance().fetch(image_instance.id)
        assert (isinstance(image_instance, ImageInstance))

        image_instance.instanceFilename = "filename"
        image_instance.update()
        assert (isinstance(image_instance, ImageInstance))
        assert (image_instance.instanceFilename == "filename")

        image_instance.delete()
        assert (not ImageInstance().fetch(image_instance.id))

    def test_image_instance_server(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_download(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_dump(self, connect, dataset):
        # TODO
        pass

    def test_image_instance_by_project(self, connect, dataset):
        image_instances = ImageInstanceCollection().fetch_with_filter("project", dataset["project"].id)
        assert (isinstance(image_instances, ImageInstanceCollection))
