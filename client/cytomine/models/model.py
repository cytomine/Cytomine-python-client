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

import six
import json

from ..cytomine import Cytomine

__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"


class Model(object):

    def __init__(self, **attributes):
        self._filters = {}
        self._query_parameters = {}

        # Attributes common to all models
        self.id = None
        self.created = None
        self.updated = None
        self.deleted = None
        self.name = None

    def fetch(self, id=None):
        if self.id is None and id is None:
            raise ValueError("Cannot fetch a model with no ID.")
        if id is not None:
            self.id = id

        return Cytomine.get_instance().get(self, self.query_parameters)

    def save(self):
        self.id = None
        return Cytomine.get_instance().post(self)

    def delete(self, id=None):
        if self.id is None and id is None:
            raise ValueError("Cannot delete a model with no ID.")
        if id is not None:
            self.id = id

        return Cytomine.get_instance().delete(self)

    def update(self, id=None, **attributes):
        if self.id is None and id is None:
            raise ValueError("Cannot update a model with no ID.")
        if id is not None:
            self.id = id

        if attributes:
            self.populate(attributes)
        return Cytomine.get_instance().put(self)

    def is_new(self):
        return self.id is None

    def populate(self, attributes):
        if attributes:
            for key, value in six.iteritems(attributes):
                if key.startswith("id_"):
                    key = key[3:]
                if not key.startswith("_"):
                    setattr(self, key, value)
        return self

    def to_json(self, **dump_parameters):
        d = dict((k, v) for k, v in six.iteritems(self.__dict__) if v is not None and not k.startswith("_"))
        return json.dumps(d, **dump_parameters)

    def uri(self):
        if self.is_new():
            return "{}.json".format(self.callback_identifier)
        else:
            return "{}/{}.json".format(self.callback_identifier, self.id)

    @property
    def filters(self):
        return self._filters

    def is_filtered_by(self, key):
        return key in self._filters

    @property
    def query_parameters(self):
        return self._query_parameters

    @property
    def callback_identifier(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return "[{}] {} : {}".format(self.callback_identifier, self.id, self.name)
