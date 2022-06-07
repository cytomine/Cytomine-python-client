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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

# Importing collections.abc objects from collections is deprecated
# since python 3.3. 
from sys import version_info
if version_info.major < 3 or \
        (version_info.major == 3 and version_info.minor < 3):
    from collections import MutableSequence
else:
    from collections.abc import MutableSequence

import six
import copy

from cytomine.cytomine import Cytomine
from ._utilities.parallel import generic_chunk_parallel


class CollectionPartialUploadException(Exception):
    """To be thrown when a collection is saved but only a part of it was successfully done so."""
    def __init__(self, desc, created=None, failed=None):
        """
        Parameters
        ----------
        desc: str
            Description of the exception
        created: Collection
            A Cytomine collection (same type as the one saved) containing the successfully saved objects (with their
            created ids).
        failed: Collection
            A Cytomine collection (same type as the one saved) containing the objects that couldn't be saved.
        """
        super(CollectionPartialUploadException, self).__init__(desc)
        self._created = created
        self._failed = failed

    @property
    def created(self):
        return self._created

    @property
    def failed(self):
        return self._failed


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

    def _upload_fn(self, collection):
        if not isinstance(collection, Collection):
            _tmp = self.__class__(model=self._model)
            _tmp.extend(collection)
            collection = _tmp
        return Cytomine.get_instance().post_collection(collection)

    def save(self, chunk=15, n_workers=0):
        """
        chunk: int|None
             Maximum number of object to send at once in a single HTTP request. None for sending them all at once.
        n_workers: int
            Number of threads to use for sending chunked requests (ignored if chunk is None). Value 0 for using as many threads as cpus on the machine.
        """
        if chunk is None:
            return Cytomine.get_instance().post_collection(self)
        elif isinstance(chunk, int):
            upload_fn = self._upload_fn
            results = generic_chunk_parallel(self, worker_fn=upload_fn, chunk_size=chunk, n_workers=n_workers)
            added, failed = list(), list()
            for (start, end), success in results:
                (added if success else failed).extend(self[start:end])
            if len(added) != len(self):
                raise CollectionPartialUploadException("Some items could not be uploaded", created=added, failed=failed)
            return True
        else:
            raise ValueError("Invalid value '{}' for chunk parameter.".format(chunk))

    def to_json(self, **dump_parameters):
        return "[{}]".format(",".join([d.to_json(**dump_parameters) for d in self._data]))

    def populate(self, attributes, append_mode=False):
        data = [self._model().populate(instance) for instance in attributes["collection"]]
        if append_mode:
            self._data += data
        else:
            self._data = data
        self._total = attributes["size"]
        if self.max is None or self.max == 0:
            self._total_pages = 1
        else:
            self._total_pages = self._total // self.max
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

    def find_by_attribute(self, attr, value):
        """Retrieve the first item of which the item.attr matches 'value'
        Parameters
        ----------
        attr: str
            Name of the attribute
        value: str
            The value to find

        Returns
        -------
        item: object|None
            The object retrieved from the list, or None if not found.
        """
        return next(iter([i for i in self if hasattr(i, attr) and getattr(i, attr) == value]), None)

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
        collection = copy.copy(self)
        collection._data = list()
        collection += self
        collection += other
        return collection

    def data(self):
        return self._data

    def filter(self, fn):
        """Return another Collection instance containing only element of the current collection that the function
        evaluates to true."""
        collection = copy.copy(self)
        collection._data = list(filter(fn, self))
        return collection


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

    def _upload_fn(self, collection):
        if not isinstance(collection, Collection):
            _tmp = self.__class__(model=self._model, object=self._obj)
            _tmp.extend(collection)
            collection = _tmp
        return Cytomine.get_instance().post_collection(collection)
