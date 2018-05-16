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

import re

import os

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Software(Model):
    def __init__(self, name=None, service_name=None, result_name=None, execute_command=None, **attributes):
        super(Software, self).__init__()
        self.name = name
        self.serviceName = service_name
        self.resultName = result_name
        self.executeCommand = execute_command
        self.description = None
        self.parameters = None
        self.numberOfJob = None
        self.numberOfNotLaunch = None
        self.numberOfInQueue = None
        self.numberOfRunning = None
        self.numberOfSuccess = None
        self.numberOfFailed = None
        self.numberOfIndeterminate = None
        self.numberOfWait = None
        self.populate(attributes)


class SoftwareCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(SoftwareCollection, self).__init__(Software, filters, max, offset)
        self._allowed_filters = [None, "project"]
        self.set_parameters(parameters)


class SoftwareProject(Model):
    def __init__(self, id_software=None, id_project=None, **attributes):
        super(SoftwareProject, self).__init__()
        self.software = id_software
        self.project = id_project
        self.name = None
        self.populate(attributes)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a software-project by client.")


class SoftwareProjectCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(SoftwareProjectCollection, self).__init__(SoftwareProject, filters, max, offset)
        self._allowed_filters = [None, "project"]
        self.set_parameters(parameters)


class SoftwareParameter(Model):
    def __init__(self, name=None, type=None, id_software=None, default_value=None,
                 required=None, index=None, set_by_server=None, uri=None, uri_sort_attribut=None,
                 uri_print_attribut=None, **attributes):
        super(SoftwareParameter, self).__init__()
        self.name = name
        self.type = type
        self.software = id_software
        self.defaultValue = default_value
        self.required = required
        self.index = index
        self.uri_ = uri
        self.uriSortAttribut = uri_sort_attribut
        self.uriPrintAttribut = uri_print_attribut
        self.setByServer = set_by_server
        self.populate(attributes)


class SoftwareParameterCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(SoftwareParameterCollection, self).__init__(SoftwareParameter, filters, max, offset)
        self._allowed_filters = ["software"]
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        # HACK to save on collection.
        if len(self._data) > 0:
            return "softwareparameter"
        return "parameter"


class Job(Model):
    NOT_LAUNCH = 0
    INQUEUE = 1
    RUNNING = 2
    SUCCESS = TERMINATED = 3
    FAILED = 4
    INDETERMINATE = 5
    WAIT = 6
    PREVIEW_DONE = 7

    def __init__(self, project_id=None, software_id=None, **attributes):
        super(Job, self).__init__()
        self.algoType = None
        self.progress = None
        self.status = None
        self.number = None
        self.statusComment = None
        self.project = project_id
        self.software = software_id
        self.softwareNone = None
        self.rate = None
        self.dataDeleted = None
        self.username = None
        self.userJob = None
        self.jobParameters = None
        self.populate(attributes)
        
    def execute(self):
        if self.is_new():
            raise ValueError("Cannot execute job if no ID was provided.")
        response = Cytomine.get_instance().post(uri="{}/{}/execute.json"
                                        .format(self.callback_identifier, self.id),
                                        data=self.to_json(),
                                        query_parameters={id: self.id})
        self.populate(response)
        return self

    def set_running(self):
        self.status = Job.RUNNING
        self.update()

    def set_terminated(self):
        self.status = Job.TERMINATED
        self.update()


class JobCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(JobCollection, self).__init__(Job, filters, max, offset)
        self._allowed_filters = [None]

        self.project = None
        self.software = None
        self.light = None

        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save a job collection by client.")


class JobParameter(Model):
    def __init__(self, id_job=None, id_software_parameter=None, value=None, **attributes):
        super(JobParameter, self).__init__()
        self.job = id_job
        self.softwareParameter = id_software_parameter
        self.value = value
        self.populate(attributes)


class JobParameterCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(JobParameterCollection, self).__init__(JobParameter, filters, max, offset)
        self._allowed_filters = ["job"]
        self.set_parameters(parameters)

    @property
    def callback_identifier(self):
        # HACK to save on collection
        if len(self._data) > 0:
            return "jobparameter"
        return "parameter"


class JobTemplate(Model):
    def __init__(self, name=None, id_software=None, id_project=None, **attributes):
        super(JobTemplate, self).__init__()
        self.name = name
        self.software = id_software
        self.project = id_project
        self.populate(attributes)


class JobTemplateCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(JobTemplateCollection, self).__init__(JobTemplate, filters, max, offset)
        self._allowed_filters = ["project"]
        self.set_parameters(parameters)


class JobData(Model):
    def __init__(self, id_job=None, key=None, filename=None, **attributes):
        super(JobData, self).__init__()
        self.job = id_job
        self.key = key
        self.filename = filename
        self.size = None
        self.dir = None
        self.value = None
        self.populate(attributes)

    def upload(self, filename):
        if self.is_new():
            raise ValueError("Cannot upload file if not existing ID.")
        return Cytomine.get_instance().upload_file(self, filename,
                                                   uri="{}/{}/upload".format(self.callback_identifier, self.id))

    def download(self, destination="{filename}", override=False):
        if self.is_new():
            raise ValueError("Cannot download file if not existing ID.")

        self.filename = os.path.basename(self.filename)
        pattern = re.compile("{(.*?)}")
        destination = re.sub(pattern, lambda m: str(getattr(self, str(m.group(0))[1:-1], "_")), destination)

        return Cytomine.get_instance().download_file("{}/{}/download".format(self.callback_identifier, self.id),
                                                     destination, override)


class JobDataCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super(JobDataCollection, self).__init__(JobData, filters, max, offset)
        self._allowed_filters = ["job"]
        self.set_parameters(parameters)
