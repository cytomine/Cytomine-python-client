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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

from collections import MutableSequence

import six

from cytomine.cytomine import Cytomine


class Collection(MutableSequence):
    def __init__(self, model, filters=None, max=0, offset=0):
        self._model = model
        self._data = []

        self._allowed_filters = []
        self._filters = filters if filters is not None else {}

        self._total = 0  # total number of resources
        self._total_pages = None  # total number of pages

        self.max = max
        self.offset = offset

    def _fetch(self, append_mode=False):
        if len(self._filters) == 0 and None not in self._allowed_filters:
            raise ValueError("This collection cannot be fetched without a filter.")

        return Cytomine.get_instance().get_collection(self, self.parameters, append_mode)

    def fetch(self, max=None):
        """
        Fetch all collection by pages of `max` items.
        Parameters
        ----------
        max : int, None (optional)
            The number of item per page. If None, retrieve all collection.

        Returns
        -------
        self    Collection, the fetched collection
        """
        if max:
            self.max = max
            n_pages = 0
            while not self._total_pages or n_pages < self._total_pages:
                self.fetch_next_page(True)
                n_pages += 1

            return self
        else:
            return self._fetch()

    def fetch_with_filter(self, key, value, max=None):
        self._filters[key] = value
        return self.fetch(max)

    def fetch_next_page(self, append_mode=False):
        self.offset = min(self._total, self.offset + self.max)
        return self._fetch(append_mode)

    def fetch_previous_page(self):
        self.offset = max(0, self.offset - self.max)
        return self._fetch()

    def save(self):
        return Cytomine.get_instance().post_collection(self)

    def to_json(self, **dump_parameters):
        return "[{}]".format(",".join([d.to_json(**dump_parameters) for d in self._data]))

    def populate(self, attributes, append_mode=False):
        data = [self._model().populate(instance) for instance in attributes["collection"]]
        if append_mode:
            self._data += data
        else:
            self._data = data
        self._total = attributes["size"]
        self._total_pages = attributes["totalPages"]
        return self

    @property
    def filters(self):
        return self._filters

    def is_filtered_by(self, key):
        return key in self._filters

    def add_filter(self, key, value):
        self._filters[key] = value

    def set_parameters(self, parameters):
        if parameters:
            for key, value in six.iteritems(parameters):
                if not key.startswith("_"):
                    setattr(self, key, value)
        return self

    @property
    def parameters(self):
        params = dict()
        for k, v in six.iteritems(self.__dict__):
            if v is not None and not k.startswith("_"):
                if isinstance(v, list):
                    v = ",".join(str(item) for item in v)
                params[k] = v
        return params

    @property
    def callback_identifier(self):
        return self._model.__name__.lower()

    def uri(self, without_filters=False):
        uri = ""
        if not without_filters:
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
        collection = self.__class__(self._model)
        collection += self
        collection += other
        return collection

    def data(self):
        return self._data


class DomainCollection(Collection):
    def __init__(self, model, object, filters=None, max=0, offset=0):
        super(DomainCollection, self).__init__(model, filters, max, offset)

        if object.is_new():
            raise ValueError("The object must be fetched or saved before.")

        self._domainClassName = None
        self._domainIdent = None
        self._obj = object

    def uri(self, without_filters=False):
        return "domain/{}/{}/{}".format(self._domainClassName, self._domainIdent,
                                        super(DomainCollection, self).uri(without_filters))

    def populate(self, attributes, append_mode=False):
        data = [self._model(self._object).populate(instance) for instance in attributes["collection"]]
        if append_mode:
            self._data += data
        else:
            self._data = data
        return self

    @property
    def _obj(self):
        return self._object

    @_obj.setter
    def _obj(self, value):
        self._object = value
        self._domainClassName = value.class_
        self._domainIdent = value.id
