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

# pylint: disable=invalid-name

import re
from typing import Any, Dict, Optional, Union

from cytomine.cytomine import Cytomine
from cytomine.models.annotation import Annotation
from cytomine.models.collection import Collection, DomainCollection
from cytomine.models.model import DomainModel, Model


class Property(DomainModel):
    def __init__(
        self,
        object: Model,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        **attributes: Any,
    ) -> None:
        super().__init__(object)
        self.key = key
        self.value = value
        self.populate(attributes)
        self._by_key = False

    @property
    def obj(self) -> Model:
        return self._object

    @obj.setter
    def obj(self, value: Model) -> None:
        self._object = value
        self.domainClassName = getattr(value, "class_", None)
        self.domainIdent = value.id

    def uri(self) -> str:
        if self._by_key and self.domainClassName and self.domainIdent and self.key:
            uri = f"domain/{self.domainClassName}/{self.domainIdent}/key/{self.key}/property.json"
        else:
            uri = super().uri()

        if self.domainClassName == "annotation":
            uri = uri.replace("domain/", "")

        return uri

    def fetch(
        self,
        id: Optional[int] = None,
        key: Optional[str] = None,
    ) -> Union[bool, Model]:
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

    def __str__(self) -> str:
        return (
            f"[{self.callback_identifier}] {self.id} : {self.domainClassName} ({self.domainIdent}) "
            f"- Key: {self.key} - Value {self.value}"
        )


class PropertyCollection(DomainCollection):
    def __init__(
        self,
        object: Model,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(Property, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)

    def uri(self, without_filters: bool = False) -> str:
        uri = super().uri(without_filters)
        if self._domainClassName == "annotation":
            uri = uri.replace("domain/", "")
        return uri

    def as_dict(self) -> Dict[str, "Property"]:
        """Transform the property collection into a python dictionary mapping keys
        with their respective Property objects.
        """
        return {p.key: p for p in self}

    @property
    def _obj(self) -> Model:
        return self._object

    @_obj.setter
    def _obj(self, value: Model) -> None:
        self._object = value
        if isinstance(value, Annotation):
            self._domainClassName = "annotation"
        else:
            self._domainClassName = getattr(value, "class_", None)
        self._domainIdent = value.id


class AttachedFile(DomainModel):
    def __init__(
        self,
        object: Model,
        filename: Optional[str] = None,
        file: Optional[str] = None,
        **attributes: Any,
    ) -> None:
        super().__init__(object)
        self.filename = filename
        self.file = file
        self.url = None
        self.populate(attributes)

    def uri(self) -> str:
        if self.is_new():
            return f"{self.callback_identifier}.json"

        return f"{self.callback_identifier}/{self.id}.json"

    def save(self) -> Union[bool, Model]:
        return self.upload()

    def update(self, id: Optional[int] = None, **attributes: Any) -> Union[bool, Model]:
        return self.upload()

    def upload(self) -> Union[bool, Model]:
        if self.file:
            return Cytomine.get_instance().upload_file(
                self,
                self.file,
                uri="attachedfile.json",
                query_parameters={
                    "domainClassName": self.domainClassName,
                    "domainIdent": self.domainIdent,
                    "filename": self.filename,
                },
            )

        if not self.filename:
            return False

        return Cytomine.get_instance().upload_file(
            self,
            self.filename,
            query_parameters={
                "domainClassName": self.domainClassName,
                "domainIdent": self.domainIdent,
            },
        )

    def download(self, destination: str = "{filename}", override: bool = False) -> bool:
        if self.is_new():
            raise ValueError("Cannot download file if not existing ID.")

        pattern = re.compile("{(.*?)}")
        destination = re.sub(
            pattern,
            lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")),
            destination,
        )

        return Cytomine.get_instance().download_file(
            f"{self.callback_identifier}/{self.id}/download",
            destination,
            override,
        )


class AttachedFileCollection(DomainCollection):
    def __init__(
        self,
        object: Model,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(AttachedFile, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class Description(DomainModel):
    def __init__(
        self,
        object: Model,
        data: Optional[Any] = None,
        **attributes: Any,
    ) -> None:
        super().__init__(object)
        self.data = data
        self.populate(attributes)

    def uri(self) -> str:
        class_value = getattr(self._object, "class_", None)
        return f"domain/{class_value}/{self._object.id}/{self.callback_identifier}.json"

    def fetch(self, id: Optional[int] = None) -> Union[bool, Model]:
        if id is not None:
            self.id = id

        return Cytomine.get_instance().get_model(self, self.query_parameters)


class Tag(Model):
    def __init__(self, name: Optional[str] = None, **attributes: Any) -> None:
        super().__init__()
        self.name: Optional[str] = name
        self.populate(attributes)


class TagCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(Tag, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class TagDomainAssociation(DomainModel):
    def __init__(
        self, object: Model, tag: Optional[int] = None, **attributes: Any
    ) -> None:
        super().__init__(object)
        self.tag = tag
        self.populate(attributes)

    def uri(self) -> str:
        if self.id:
            return f"tag_domain_association/{self.id}.json"

        if self.domainClassName and self.domainIdent:
            return super().uri()

        return ""

    @property
    def callback_identifier(self) -> str:
        return "tag_domain_association"


class TagDomainAssociationCollection(DomainCollection):
    def __init__(
        self,
        object: Any,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(TagDomainAssociation, object, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)

    @property
    def callback_identifier(self) -> str:
        return "tag_domain_association"
