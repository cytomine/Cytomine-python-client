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


class Track(Model):
    def __init__(
        self,
        name: Optional[str] = None,
        id_image: Optional[int] = None,
        color: Optional[str] = None,
        **attributes: Any,
    ) -> None:
        super().__init__()
        self.name = name
        self.image = id_image
        self.color = color
        self.populate(attributes)


class TrackCollection(Collection):
    def __init__(
        self,
        filters: Optional[Dict[str, Any]] = None,
        max: int = 0,
        offset: int = 0,
        **parameters: Any,
    ) -> None:
        super().__init__(Track, filters, max, offset)
        self._allowed_filters = ["project", "imageinstance"]
        self.set_parameters(parameters)


class AnnotationTrack(Model):
    def __init__(
        self,
        annotation_class_name: Optional[str] = None,
        id_annotation: Optional[int] = None,
        id_track: Optional[int] = None,
        **attributes: Any,
    ):
        super().__init__()
        self.annotationClassName = annotation_class_name
        self.annotationIdent = id_annotation
        self.track = id_track
        self.populate(attributes)

    def uri(self) -> str:
        return f"annotationtrack/{self.annotationIdent}/{self.track}.json"

    def fetch(
        self,
        id_annotation: Optional[int] = None,
        id_track: Optional[int] = None,
    ) -> Union[bool, Model]:
        self.id = -1

        if self.annotationIdent is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")

        if self.track is None and id_track is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.annotationIdent = id_annotation

        if id_track is not None:
            self.track = id_track

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args: Any, **kwargs: Any) -> Union[bool, Model]:
        raise NotImplementedError("Cannot update a annotation-track.")

    def __str__(self) -> str:
        return (
            f"[{self.callback_identifier}] Annotation {self.annotationIdent} "
            f"- Track {self.track}"
        )
