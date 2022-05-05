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

import re

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.cytomine import Cytomine
from cytomine.models.annotation import Annotation
from cytomine.models.collection import Collection, DomainCollection
from cytomine.models.model import Model, DomainModel


class Property(DomainModel):
    def __init__(self, object, key=None, value=None, **attributes):
        super(Property, self).__init__(object)
        self.key = key
        self.value = value
        self.populate(attributes)
        self._by_key = False

    @property
    def obj(self):
        return self._object

    @obj.setter
    def obj(self, value):
        self._object = value
        if isinstance(value, Annotation):
            self.domainClassName = "annotation"
        else:
            self.domainClassName = value.class_
        self.domainIdent = value.id

    def uri(self):
        if self._by_key and self.domainClassName and self.domainIdent and self.key:
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
            self._by_key = True

        model = Cytomine.get_instance().get_model(self, self.query_parameters)
        self._by_key = False
        return model

    def __str__(self):
        return "[{}] {} : {} ({}) - Key: {} - Value {}".format(self.callback_identifier, self.id, self.domainClassName,
                                                               self.domainIdent, self.key, self.value)


class PropertyCollection(DomainCollection):
    def __init__(self, object, filters=None, max=0, offset=0, **parameters):
        super(PropertyCollection, self).__init__(Property, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)

    def uri(self, without_filters=False):
        uri = super(PropertyCollection, self).uri(without_filters)
        if self._domainClassName == "annotation":
            uri = uri.replace("domain/", "")
        return uri

    def as_dict(self):
        """Transform the property collection into a python dictionary mapping keys
            with their respective Property objects.
        """
        return {p.key: p for p in self}

    @property
    def _obj(self):
        return self._object

    @_obj.setter
    def _obj(self, value):
        self._object = value
        if isinstance(value, Annotation):
            self._domainClassName = "annotation"
        else:
            self._domainClassName = value.class_
        self._domainIdent = value.id


class AttachedFile(DomainModel):
    def __init__(self, object, filename=None, file=None, **attributes):
        super(AttachedFile, self).__init__(object)
        self.filename = filename
        self.file = file
        self.url = None
        self.populate(attributes)

    def uri(self):
        if self.is_new():
            return "{}.json".format(self.callback_identifier)
        else:
            return "{}/{}.json".format(self.callback_identifier, self.id)

    def save(self):
        return self.upload()

    def update(self, id=None, **attributes):
        return self.upload()

    def upload(self):
        if self.file:
            return Cytomine.get_instance().upload_file(
                self, self.file, uri='attachedfile.json',
                query_parameters={
                    "domainClassName": self.domainClassName,
                    "domainIdent": self.domainIdent,
                    "filename": self.filename
                }
            )
        else:
            return Cytomine.get_instance().upload_file(
                self, self.filename,
                query_parameters={
                    "domainClassName": self.domainClassName,
                    "domainIdent": self.domainIdent
                }
            )

    def download(self, destination="{filename}", override=False):
        if self.is_new():
            raise ValueError("Cannot download file if not existing ID.")

        pattern = re.compile("{(.*?)}")
        destination = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), destination)

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     destination, override)


class AttachedFileCollection(DomainCollection):
    def __init__(self, object, filters=None, max=0, offset=0, **parameters):
        super(AttachedFileCollection, self).__init__(AttachedFile, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class Description(DomainModel):
    def __init__(self, object, data=None, **attributes):
        super(Description, self).__init__(object)
        self.data = data
        self.populate(attributes)

    def uri(self):
        return "domain/{}/{}/{}.json".format(self._object.class_, self._object.id, self.callback_identifier)

    def fetch(self, id=None):
        if id is not None:
            self.id = id

        return Cytomine.get_instance().get_model(self, self.query_parameters)


class Tag(Model):
    def __init__(self, name=None, **attributes):
        super(Tag, self).__init__()
        self.name = name
        self.populate(attributes)


class TagCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(TagCollection, self).__init__(Tag, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class TagDomainAssociation(DomainModel):
    def __init__(self, object, tag=None, **attributes):
        super(TagDomainAssociation, self).__init__(object)
        self.tag = tag
        self.populate(attributes)

    def uri(self):
        if self.id:
            uri = "tag_domain_association/{}.json".format(self.id)
        elif self.domainClassName and self.domainIdent:
            uri = super(TagDomainAssociation, self).uri()

        return uri

    @property
    def callback_identifier(self):
        return "tag_domain_association"


class TagDomainAssociationCollection(DomainCollection):
    def __init__(self, object, filters=None, max=0, offset=0, **parameters):
        super(TagDomainAssociationCollection, self).__init__(TagDomainAssociation, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        return "tag_domain_association"
