# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2017. Authors: see NOTICE file.
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

from client.cytomine.cytomine import Cytomine
from client.cytomine.models.annotation import Annotation
from client.cytomine.models.collection import DomainCollection
from client.cytomine.models.model import DomainModel

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__copyright__ = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"


class Property(DomainModel):
    def __init__(self, object, key=None, value=None, **attributes):
        super(Property, self).__init__(object)

        if isinstance(object, Annotation):
            self.domainClassName = "annotation"
        else:
            self.domainClassName = object.class_
        self.domainIdent = object.id
        self.key = key
        self.value = value
        self.populate(attributes)

    def uri(self):
        if self.is_new() and self.domainClassName and self.domainIdent and self.key:
            uri = "domain/{}/{}/key/{}/property.json".format(self.domainClassName, self.domainIdent, self.key)
        else:
            uri = super(Property, self).uri()

        if self.domainClassName == "annotation":
            uri = uri.replace("domain/", "")

        return uri

    def fetch(self, id=None, key=None):
        if self.id is None and id is None and self.key is None and key is None:
            raise ValueError("Cannot fetch a model with no ID and no key.")
        if id is not None:
            self.id = id
        if key is not None:
            self.key = key

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def __str__(self):
        return "[{}] {} : {} ({}) - Key: {} - Value {}".format(self.callback_identifier, self.id, self.domainClassName,
                                                               self.domainIdent, self.key, self.value)


class PropertyCollection(DomainCollection):
    def __init__(self, object, filters=None, max=0, offset=0, **parameters):
        super(PropertyCollection, self).__init__(Property, object, filters, max, offset)
        if object.is_new():
            raise ValueError("The object must be fetched or saved before.")

        if isinstance(object, Annotation):
            self._domainClassName = "annotation"
        else:
            self._domainClassName = object.class_
        self._domainIdent = object.id
        self.set_parameters(parameters)

    def uri(self):
        uri = super(PropertyCollection, self).uri()
        if self._domainClassName == "annotation":
            uri = uri.replace("domain/", "")
        return uri
