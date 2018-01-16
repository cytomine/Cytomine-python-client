# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2015. Authors: see NOTICE file.
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

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"

from collection import Collection
from model import Model


class Storage(Model):
    def __init__(self, name=None, **attributes):
        super(Storage, self).__init__(**attributes)
        self.name = name
        self.basePath = None
        self.user = None


class StorageCollection(Collection):
    def __init__(self, filters=None, query_parameters=None, max=0, offset=0):
        super(StorageCollection, self).__init__(Storage, filters, query_parameters, max, offset)


class UploadedFile(Model):
    def __init__(self, **attributes):
        super(UploadedFile, self).__init__(**attributes)
        self.user = None
        self.projects = None
        self.storages = None
        self.filename = None
        self.originalFilename = None
        self.ext = None
        self.size = None
        self.path = None
        self.status = None

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.filename)


class UploadedFileCollection(Collection):
    def __init__(self, filters=None, query_parameters=None, max=0, offset=0):
        super(UploadedFileCollection, self).__init__(UploadedFile, filters, query_parameters, max, offset)
