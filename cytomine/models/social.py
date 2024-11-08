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

# pylint: disable=arguments-differ,invalid-name

from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Position(Model):
    def __init__(self):
        super().__init__()
        self.user = None
        self.image = None
        self.slice = None
        self.project = None
        self.broadcast = None
        self.location = None
        self.zoom = None
        self.rotation = None
        self.x = None
        self.y = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a new position by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete a position.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a position.")


class PositionCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(Position, filters, max, offset)
        self._allowed_filters = ["imageinstance", "sliceinstance"]

        self.user = None
        self.afterThan = None
        self.beforeThan = None
        self.showDetails = True
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        return "positions"


class AnnotationAction(Model):
    def __init__(self):
        super().__init__()
        self.user = None
        self.image = None
        self.slice = None
        self.project = None
        self.annotationClassName = None
        self.annotationIdent = None
        self.annotationCreator = None
        self.action = None

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a new annotation action by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete an annotation action.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update an annotation action.")

    @property
    def callback_identifier(self):
        return "annotation_action"


class AnnotationActionCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(AnnotationAction, filters, max, offset)
        self._allowed_filters = ["imageinstance"]

        self.user = None
        self.afterThan = None
        self.beforeThan = None
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        return "annotation_action"


class ProjectConnection(Model):
    def __init__(self, project=None, user=None, **attributes):
        super().__init__()
        self.project = project
        self.user = user
        self.countViewedImages = None
        self.countCreatedAnnotations = None
        self.os = None
        self.created = None
        self.browser = None
        self.browserVersion = None
        self.time = None
        self.updated = None
        self.deleted = None
        self.name = None

        self.populate(attributes)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a ProjectConnection by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete a ProjectConnection by client.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a ProjectConnection by client.")

    def fetch(self, *args, **kwargs):
        raise NotImplementedError("Cannot fetch a ProjectConnection by client.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] {self.id}: "
            f"[user] {self.user}, [project] {self.project}"
        )


class ProjectConnectionCollection(Collection):
    def __init__(self, project, user, filters=None, max=0, offset=0, **parameters):
        super().__init__(ProjectConnection, filters, max, offset)
        self._allowed_filters = [None]
        self.project = project
        self.user = user
        self.set_parameters(parameters)

    def uri(self):
        return f"project/{self.project}/userconnection/{self.user}.json"

    def save(self, *args, **kwargs):
        raise NotImplementedError(
            "Cannot save a ProjectConnection collection by client."
        )


class ImageConsultation(Model):
    def __init__(self, image=None, user=None, **attributes):
        super().__init__()
        self.project = None
        self.user = user
        self.image = image
        self.imageName = None
        self.imageThumb = None
        self.mode = None
        self.projectConnection = None
        self.time = None
        self.updated = None
        self.countCreatedAnnotations = None
        self.created = None
        self.deleted = None
        self.name = None

        self.populate(attributes)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a ImageConsultation by client.")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("Cannot delete a ImageConsultation by client.")

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a ImageConsultation by client.")

    def fetch(self, *args, **kwargs):
        raise NotImplementedError("Cannot fetch a ImageConsultation by client.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] {self.id}: "
            f"[user] {self.user}, [image] {self.image}"
        )


class ImageConsultationCollection(Collection):
    def __init__(self, project, user, filters=None, max=0, offset=0, **parameters):
        super().__init__(ImageConsultation, filters, max, offset)
        self._allowed_filters = [None]
        self.project = project
        self.user = user
        self.set_parameters(parameters)

    def uri(self):
        return f"project/{self.project}/user/{self.user}/imageconsultation.json"

    def save(self, *args, **kwargs):
        raise NotImplementedError(
            "Cannot save a ImageConsultation collection by client."
        )
