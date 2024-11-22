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

from typing import Any, Dict, Optional, Union

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Ontology(Model):
    def __init__(self, name: Optional[str] = None, **attributes: Any) -> None:
        super().__init__()
        self.name = name
        self.user = None
        self.title = None
        self.attr = None
        self.data = None
        self.isFolder = None
        self.key = None
        self.children = None
        self.populate(attributes)


class OntologyCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(Ontology, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class Term(Model):
    def __init__(
        self,
        name: Optional[str] = None,
        id_ontology: Optional[int] = None,
        color: Optional[str] = None,
        id_parent: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.name = name
        self.ontology = id_ontology
        self.parent = id_parent
        self.color = color
        self.populate(attributes)


class TermCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(Term, filters, max, offset)
        self._allowed_filters = [None, "project", "ontology", "annotation"]
        self.set_parameters(parameters)


class RelationTerm(Model):
    def __init__(
        self,
        id_term1: Optional[int] = None,
        id_term2: Optional[int] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.term1 = id_term1
        self.term2 = id_term2
        self.populate(attributes)

    def uri(self) -> str:
        if not self.id:
            return "relation/parent/term.json"

        return f"relation/parent/term1/{self.term1}/term2/{self.term2}.json"

    def fetch(
        self,
        id_term1: Optional[int] = None,
        id_term2: Optional[int] = None,
    ) -> Union[bool, Model]:
        self.id = -1

        if self.term1 is None and id_term1 is None:
            raise ValueError("Cannot fetch a model with no term 1 ID.")

        if self.term2 is None and id_term2 is None:
            raise ValueError("Cannot fetch a model with no term 2 ID.")

        if id_term1 is not None:
            self.term1 = id_term1

        if id_term2 is not None:
            self.term2 = id_term2

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args: Any, **kwargs: Any) -> Union[bool, Model]:
        raise NotImplementedError("Cannot update a relation-term.")

    def __str__(self) -> str:
        return (
            f"[{self.callback_identifier}] {self.id} : "
            f"parent {self.term1} - child {self.term2}"
        )
