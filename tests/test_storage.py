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
    Storage,
    StorageCollection,
    UploadedFile,
    UploadedFileCollection,
)
from tests.conftest import random_string


class TestStorage:
    def test_storage(self, connect, dataset):
        name = random_string()
        storage = Storage(name, dataset["user"].id).save()
        assert isinstance(storage, Storage)
        assert storage.name == name

        storage = Storage().fetch(storage.id)
        assert isinstance(storage, Storage)
        assert storage.name == name

        name = random_string()
        storage.name = name
        storage.update()
        assert isinstance(storage, Storage)
        assert storage.name == name

        # TODO: Storage delete does not work on Cytomine-Core
        # storage.delete()
        # assert(not Storage().fetch(storage.id))

    def test_storages(self, connect, dataset):
        storages = StorageCollection().fetch()
        assert isinstance(storages, StorageCollection)


class TestUploadedFile:
    def test_uploaded_file(self, connect, dataset):
        storages = StorageCollection().fetch()
        filename = "filename"
        uf = UploadedFile(
            "original",
            filename,
            id_user=connect.current_user.id,
            size=1,
            ext="ext",
            contentType="contentType",
            id_storage=storages[0].id,
            id_image_server=dataset["image_servers"][0].id,
        ).save()
        assert isinstance(uf, UploadedFile)
        assert uf.filename == filename

        filename = filename + "bis"
        uf.filename = filename
        uf.update()
        assert isinstance(uf, UploadedFile)
        assert uf.filename == filename

        uf.delete()
        assert not UploadedFile().fetch(uf.id)

    def test_uploaded_files(self, connect, dataset):
        uploaded_files = UploadedFileCollection().fetch()
        assert isinstance(uploaded_files, UploadedFileCollection)
