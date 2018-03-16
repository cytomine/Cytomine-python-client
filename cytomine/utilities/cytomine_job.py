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

from cytomine.cytomine import Cytomine
from cytomine.models.project import Project
from cytomine.models.software import Software, Job, JobParameter
from cytomine.models.user import User

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__contributors = ["Mormont Romain <romainmormont@gmail.com", "Rubens Ulysse <urubens@uliege.be>"]
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"


class CytomineJob(Cytomine):
    """
    ===========
    CytomineJob
    ===========
    A :class:`CytomineJob` represents a job in the cytomine context.
    This class does nothing by itself. It is just supposed to be
    inherited from or incorporated in any class representing
    a software/job registered in the Cytomine server

    Usage
    -----
    Either use the :meth:`connect`/meth:`close`methods or use it with a
    with statement:

    with CytomineJob(...) as job:
         do_your_stuff()

    Constructor parameters
    ----------------------
    software_id : int
        The identifier of the software on the Cytomine server
    project_id : int
        The identifier of the project to process on the Cytomine server
    parameters: dict
        A dictionary mapping job parameters with their values (the dictionary must not contain any other key than
        the parameters names)
    """
    def __init__(self, host, public_key, private_key, software_id, project_id, parameters=None, **kwargs):
        super(CytomineJob, self).__init__(host, public_key, private_key, **kwargs)
        self._job = None
        self._project = Project().fetch(project_id)
        self._software = Software().fetch(software_id)
        self._job_done = False
        self._parameters = parameters

    @property
    def job(self):
        """Return the job model

        Return
        ------
        job: cytomine.Job
            The job model
        """
        return self._job

    @property
    def project(self):
        """
        Protected method

        Return
        ------
        project_id : int
            The id of the project
        """
        return self._project

    @property
    def software(self):
        """
        Protected method

        Return
        ------
        software_id : int
            The id of the software
        """
        return self._software

    def done(self, status=True):
        """
        Indicates whether the job is finished or not

        Parameters
        ----------
        status : bool
            Whether the process is finished
        """
        self._job_done = status

    def is_done(self):
        """
        Return
        ------
        job_status : bool
            Whether the process is finished
        """
        return self._job_done

    def start(self):
        """
        Connect to the Cytomine server and switch to job connection
        Incurs dataflows
        """

        if not self.current_user.algo:
            # If user connects as a human (CLI execution)
            self._job = Job(self._project.id, self._software.id).save()
            user_job = User().fetch(self._job.userJob)
            self.set_credentials(user_job.publicKey, user_job.privateKey)
        else:
            # If the user executes the job through the Cytomine interface
            self._job = Job().fetch(self.current_user.job)

        # set job state to RUNNING
        self._job.status = Job.RUNNING
        self._job.update()

        # add software parameters
        if self._parameters is not None:
            for software_param in self._software.parameters:
                name = software_param["name"]
                if name in self._parameters:
                    value = self._parameters[name]
                else:
                    value = software_param["defaultParamValue"]

                JobParameter(self._job.id, software_param["id"], value).save()

    def close(self):
        """
        Notify the Cytomine server of the job's end
        Incurs a dataflows
        """
        status = Job.FAILED  # status code for FAILED
        if self.is_done():
            status = Job.TERMINATED

        self._job.status = status
        self._job.update()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value is None:
            # No exception, job is done
            self.done()
        self.close()
        return False
