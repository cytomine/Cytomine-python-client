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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import MutableSequence

import six

from ..cytomine import Cytomine

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"


class Collection(MutableSequence):
    def __init__(self, model, filters=None, max=0, offset=0):
        self._model = model
        self._data = []

        self._allowed_filters = []
        self._filters = filters if filters is not None else {}

        self._total = None  # total number of resources
        self._total_pages = None  # total number of pages

        self.max = max
        self.offset = offset

    def fetch(self):
        return Cytomine.get_instance().get(self, self.parameters)

    def fetch_with_filter(self, key, value):
        self._filters[key] = value
        self.fetch()

    def fetch_next_page(self):
        pass

    def fetch_previous_page(self):
        pass

    def populate(self, attributes):
        self._data = [self._model().populate(instance) for instance in attributes["collection"]]
        return self

    @property
    def filters(self):
        return self._filters

    def is_filtered_by(self, key):
        return key in self._filters

    def set_parameters(self, parameters):
        if parameters:
            for key, value in six.iteritems(parameters):
                if not key.startswith("_"):
                    setattr(self, key, value)
        return self

    @property
    def parameters(self):
        return dict((k, v) for k, v in six.iteritems(self.__dict__) if v is not None and not k.startswith("_"))

    @property
    def callback_identifier(self):
        return self._model.__name__.lower()

    def uri(self):
        if len(self.filters) > 1:
            raise ValueError("More than 1 filter not allowed by default.")

        uri = "/".join(["{}/{}".format(key, value) for key, value in six.iteritems(self.filters)
                        if key in self._allowed_filters])
        if len(uri) > 0:
            uri += "/"

        return "{}{}.json".format(uri, self.callback_identifier)

    def __str__(self):
        return "[{} collection] {} objects".format(self.callback_identifier, len(self))

    # Collection
    def __len__(self):
        return len(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, index, value):
        if not isinstance(value, self._model):
            raise TypeError("Value of type {} not allowed in {}.".format(value.__class__.__name__,
                                                                         self.__class__.__name__))
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def insert(self, index, value):
        if not isinstance(value, self._model):
            raise TypeError("Value of type {} not allowed in {}.".format(value.__class__.__name__,
                                                                         self.__class__.__name__))
        self._data.insert(index, value)

    def __iadd__(self, other):
        if type(self) is not type(other):
            raise TypeError("Only two same Collection objects can be added together.")
        self._data.extend(other.data())
        return self

    def __add__(self, other):
        if type(self) is not type(other):
            raise TypeError("Only two same Collection objects can be added together.")
        collection = Collection(self._model)
        collection += self.data()
        collection += other.data()
        return collection

    @DeprecationWarning
    def data(self):
        return self._data

        # def parse(self, params = None):
        #     response = json.loads(params)
        #     if hasattr(self, "collection_identifier"):
        #         data = response[self.collection_identifier]
        #         self._total = int(response["size"])
        #         self._offset = int(response["offset"])
        #         self._total_pages = int(response["totalPages"])
        #         self._per_page = int(response["perPage"])
        #         if self._per_page != 0:
        #             self._page_index = self._offset / self._per_page
        #         else:
        #            self._page_index = 0
        #     for model in data:
        #         self._data.append(self._model().__class__(json.dumps(model)))
        #
        # def next_page(self):
        #     if self._total_pages:
        #         if self._page_index == self._total_pages - 1:
        #             return None
        #         else :
        #             self._page_index = self._page_index + 1
        #             return self._page_index
        #     else :
        #         return None #to do : should we thrown something here, like first page not fetch ?
        #
        # def previous_page(self):
        #     self._per_page = max(1, self._per_page - 1)
        #     return self._per_page
        #
        # def init_paginator(self, per_page, page_index = 0):
        #     self._per_page = per_page
        #     self._page_index = page_index
        #
