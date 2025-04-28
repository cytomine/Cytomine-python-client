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

import copy
from collections.abc import MutableSequence
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar, Union

from cytomine.cytomine import Cytomine
from cytomine.models.model import Model

from ._utilities.parallel import generic_chunk_parallel

T = TypeVar("T")


class CollectionPartialUploadException(Exception):
    """To be thrown when a collection is saved but
    only a part of it was successfully done so.
    """

    def __init__(
        self,
        desc: str,
        created: Optional["Collection"] = None,
        failed: Optional["Collection"] = None,
    ) -> None:
        """
        Parameters
        ----------
        desc: str
            Description of the exception
        created: Collection
            A Cytomine collection (same type as the one saved) containing
            the successfully saved objects (with their created ids).
        failed: Collection
            A Cytomine collection (same type as the one saved) containing
            the objects that couldn't be saved.
        """
        super().__init__(desc)
        self._created = created
        self._failed = failed

    @property
    def created(self) -> Optional["Collection"]:
        return self._created

    @property
    def failed(self) -> Optional["Collection"]:
        return self._failed


class Collection(MutableSequence):
    def __init__(
        self,
        model: Any,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
    ) -> None:
        self._model: Any = model
        self._data: List[Any] = []

        self._allowed_filters: List[Optional[str]] = []
        self._filters = filters if filters is not None else {}

        self._total: int = 0  # total number of resources
        self._total_pages: Optional[int] = None  # total number of pages

        self.max: int = max
        self.offset: int = offset

    def _fetch(self, append_mode: bool = False) -> Union[bool, "Collection"]:
        if len(self._filters) == 0 and None not in self._allowed_filters:
            raise ValueError("This collection cannot be fetched without a filter.")

        return Cytomine.get_instance().get_collection(
            self,
            self.parameters,
            append_mode,
        )

    def fetch(self, max: Optional[int] = None) -> Union[bool, "Collection"]:
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

        return self._fetch()

    def fetch_with_filter(
        self,
        key: str,
        value: Any,
        max: Optional[int] = None,
    ) -> Union[bool, "Collection"]:
        self._filters[key] = value
        return self.fetch(max)

    def fetch_next_page(self, append_mode: bool = False) -> Union[bool, "Collection"]:
        self.offset = min(self._total, self.offset + self.max)
        return self._fetch(append_mode)

    def fetch_previous_page(self) -> Union[bool, "Collection"]:
        self.offset = max(0, self.offset - self.max)
        return self._fetch()

    def _upload_fn(self, collection: "Collection") -> Union[bool, "Collection"]:
        if not isinstance(collection, Collection):
            _tmp = self.__class__(model=self._model)
            _tmp.extend(collection)
            collection = _tmp
        return Cytomine.get_instance().post_collection(collection)

    def save(self, chunk: int = 15, n_workers: int = 0) -> Union[bool, "Collection"]:
        """
        chunk: int|None
            Maximum number of object to send at once in a single HTTP request.
            None for sending them all at once.
        n_workers: int
            Number of threads to use for sending chunked requests (ignored if chunk is None).
            Value 0 for using as many threads as cpus on the machine.
        """
        if chunk is None:
            return Cytomine.get_instance().post_collection(self)

        if isinstance(chunk, int):
            upload_fn = self._upload_fn
            results = generic_chunk_parallel(
                self,  # type: ignore
                worker_fn=upload_fn,  # type: ignore
                chunk_size=chunk,
                n_workers=n_workers,
            )

            added: List[Any] = []
            failed: List[Any] = []
            for (start, end), success in results:
                (added if success else failed).extend(self[start:end])

            if len(added) != len(self):
                raise CollectionPartialUploadException(
                    "Some items could not be uploaded",
                    created=added,  # type: ignore
                    failed=failed,  # type: ignore
                )

            return True

        raise ValueError(f"Invalid value '{chunk}' for chunk parameter.")

    def to_json(self, **dump_parameters: Dict[str, Any]) -> str:
        return f"[{','.join([d.to_json(**dump_parameters) for d in self._data])}]"

    def populate(
        self,
        attributes: Dict[str, Any],
        append_mode: bool = False,
    ) -> "Collection":
        data = [
            self._model().populate(instance) for instance in attributes["collection"]
        ]
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
    def filters(self) -> Dict[str, Any]:
        return self._filters

    def is_filtered_by(self, key: str) -> bool:
        return key in self._filters

    def add_filter(self, key: str, value: Any) -> None:
        self._filters[key] = value

    def set_parameters(self, parameters: Dict[str, Any]) -> "Collection":
        if parameters:
            for key, value in parameters.items():
                if not key.startswith("_"):
                    setattr(self, key, value)
        return self

    @property
    def parameters(self) -> Dict[str, Any]:
        params = {}
        for k, v in self.__dict__.items():
            if v is not None and not k.startswith("_"):
                if isinstance(v, list):
                    v = ",".join(str(item) for item in v)
                params[k] = v
        return params

    @property
    def callback_identifier(self) -> str:
        return self._model.__name__.lower()

    def uri(self, without_filters: bool = False) -> str:
        uri = ""
        if not without_filters:
            if len(self.filters) > 1:
                raise ValueError("More than 1 filter not allowed by default.")

            uri = "/".join(
                [
                    f"{key}/{value}"
                    for key, value in self.filters.items()
                    if key in self._allowed_filters
                ]
            )
            if len(uri) > 0:
                uri += "/"

        return f"{uri}{self.callback_identifier}.json"

    def find_by_attribute(self, attr: str, value: Any) -> Optional[Model]:
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
        return next(
            iter([i for i in self if hasattr(i, attr) and getattr(i, attr) == value]),
            None,
        )

    def __str__(self) -> str:
        return f"[{self.callback_identifier} collection] {len(self)} objects"

    # Collection
    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, item: Union[int, slice]) -> Any:
        return self._data[item]

    def __setitem__(
        self,
        index: Union[int, slice],
        value: Union[Any, Iterable[Any]],
    ) -> None:
        if not isinstance(value, self._model):
            raise TypeError(
                f"Value of type {value.__class__.__name__} "
                f"not allowed in {self.__class__.__name__}."
            )
        self._data[index] = value

    def __delitem__(self, index: Union[int, slice]) -> None:
        del self._data[index]

    def insert(self, index: int, value: Any) -> None:
        if not isinstance(value, self._model):
            raise TypeError(
                f"Value of type {value.__class__.__name__} "
                f"not allowed in {self.__class__.__name__}."
            )
        self._data.insert(index, value)

    def __iadd__(self, other: "Collection") -> "Collection":  # type: ignore
        if type(self) is not type(other):
            raise TypeError("Only two same Collection objects can be added together.")
        self._data.extend(other.data())
        return self

    def __add__(self, other: "Collection") -> "Collection":
        if type(self) is not type(other):
            raise TypeError("Only two same Collection objects can be added together.")
        collection = copy.copy(self)
        collection._data = []
        collection += self
        collection += other
        return collection

    def data(self) -> List[Any]:
        return self._data

    def filter(self, fn: Callable[[T], bool]) -> "Collection":
        """Return another Collection instance containing only element of
        the current collection that the function evaluates to true.
        """
        collection = copy.copy(self)
        collection._data = list(filter(fn, self))  # pylint: disable=protected-access
        return collection


class DomainCollection(Collection):
    def __init__(
        self,
        model: Any,
        object: Model,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
    ) -> None:
        super().__init__(model, filters, max, offset)

        if object.is_new():
            raise ValueError("The object must be fetched or saved before.")

        self._domainClassName: Optional[str] = None
        self._domainIdent: Optional[int] = None
        self._obj = object

    def uri(self, without_filters: bool = False) -> str:
        return (
            f"domain/{self._domainClassName}/{self._domainIdent}/"
            f"{super().uri(without_filters)}"
        )

    def populate(
        self,
        attributes: Any,
        append_mode: bool = False,
    ) -> "DomainCollection":
        data = [
            self._model(self._object).populate(instance)
            for instance in attributes["collection"]
        ]
        if append_mode:
            self._data += data
        else:
            self._data = data
        return self

    @property
    def _obj(self) -> Model:
        return self._object

    @_obj.setter
    def _obj(self, value: Any) -> None:
        self._object = value
        self._domainClassName = value.class_
        self._domainIdent = value.id

    def _upload_fn(self, collection: "Collection") -> bool:
        if not isinstance(collection, Collection):
            _tmp = self.__class__(model=self._model, object=self._obj)
            _tmp.extend(collection)
            collection = _tmp
        return Cytomine.get_instance().post_collection(collection)
