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

from argparse import ArgumentParser
import logging

from cytomine.cytomine import Cytomine, _cytomine_parameter_name_synonyms
from cytomine.models.project import Project
from cytomine.models.software import Software, Job, JobParameter, SoftwareParameterCollection
from cytomine.models.user import User

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__contributors = ["Mormont Romain <romainmormont@gmail.com", "Rubens Ulysse <urubens@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"


def _inferred_number_type(v):
    """Return the inferred type for the given string. The string must contain either an interger or a float.
    """
    try:
        return int(v)
    except ValueError:
        return float(v)


def _convert_type(_type):
    # Not trying too hard for the finding types (list considered as string and number as floats)
    # Just want a first validation (when possible) with argparse.
    # Advanced checking is advised in actual job implementation.
    return {
        "Number": _inferred_number_type,
        "String": str,
        "Boolean": _to_bool,
        "Domain": int,
        "List": str,
        "ListDomain": str,
        "Date": str
    }[_type]


def _to_bool(v):
    """
    Convert the value to boolean. Treat the following strings
    as False (case insensitive): {"0", "false", "no"}
    and True (case insensitive): {"1", "true", "yes"}

    Parameters
    ----------
    v: object
        A object to convert to a boolean value.

    Returns
    -------
    b: bool
        The boolean value
    """
    if isinstance(v, str):
        lv = v.lower()
        if lv in {"0", "false", "no"}:
            return False
        elif lv in {"1", "true", "yes"}:
            return True
        else:
            raise ValueError("unexpected value '{}' for a boolean".format(v))
    else:
        return bool(v)


def _software_params_to_argparse(parameters):
    """
    Converts a SoftwareParameterCollection into an ArgumentParser object.

    Parameters
    ----------
    parameters: SoftwareParameterCollection
        The software parameters
    Returns
    -------
    argparse: ArgumentParser
        An initialized argument parser
    """
    # Check software parameters
    argparse = ArgumentParser()
    for parameter in parameters:
        python_type = _convert_type(parameter.type)
        arg_desc = {
            "type": python_type,
            "default": None if parameter.defaultParamValue is None else python_type(parameter.defaultParamValue),
            "dest": parameter.name,
            "required": parameter.required,
            "help": ""  # TODO help
        }
        argparse.add_argument(*_cytomine_parameter_name_synonyms(parameter.name), **arg_desc)
    return argparse


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
    parameters: Namespace
        A namespace mapping job parameters with their values (must not contain any other key than
        the parameters names)
    """
    def __init__(self, host, public_key, private_key, software_id, project_id, parameters=None, **kwargs):
        super(CytomineJob, self).__init__(host, public_key, private_key, **kwargs)
        self._job = None
        self._project = Project().fetch(project_id)
        self._software = Software().fetch(software_id)
        self._job_done = False
        self._parameters = parameters

    @classmethod
    def from_cli(cls, argv, **kwargs):
        # Parse CytomineJob constructor parameters
        argparse = cls._add_cytomine_cli_args(ArgumentParser())
        argparse.add_argument(*_cytomine_parameter_name_synonyms("software_id"),
                              dest="software_id", type=int, help="The Cytomine software id.", required=True)
        argparse.add_argument(*_cytomine_parameter_name_synonyms("project_id"),
                              dest="project_id", type=int, help="The Cytomine project id.", required=True)
        base_params, _ = argparse.parse_known_args(args=argv)

        log_level = base_params.verbose
        if base_params.log_level is not None:
            log_level = logging.getLevelName(base_params.log_level)

        cytomine_job = CytomineJob(
            host=base_params.host,
            public_key=base_params.public_key,
            private_key=base_params.private_key,
            software_id=base_params.software_id,
            project_id=base_params.project_id,
            parameters=None,
            verbose=log_level,
            **kwargs
        )

        # Parse and set job parameters
        params_collection = SoftwareParameterCollection(
            filters={"software": cytomine_job.software.id},
            withSetByServer=True
        ).fetch()
        cytomine_job.parameters, _ = _software_params_to_argparse(params_collection).parse_known_args(argv)
        return cytomine_job

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

    @property
    def parameters(self):
        """
        Return
        ------
        parameters : dict
            The id of the software
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        Protected method.

        Parameters
        ----------
        parameters: dict
            Dictionnary mapping parameters name with their values.
        """
        self._parameters = parameters

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

        run_by_ui = False
        if not self.current_user.algo:
            # If user connects as a human (CLI execution)
            self._job = Job(self._project.id, self._software.id).save()
            user_job = User().fetch(self._job.userJob)
            self.set_credentials(user_job.publicKey, user_job.privateKey)
        else:
            # If the user executes the job through the Cytomine interface
            self._job = Job().fetch(self.current_user.job)
            run_by_ui = True

        # set job state to RUNNING
        self._job.status = Job.RUNNING
        self._job.update()

        # add software parameters
        if not run_by_ui and self._parameters is not None:
            parameters = vars(self._parameters)
            for software_param in self._software.parameters:
                name = software_param["name"]
                if name in parameters:
                    value = parameters[name]
                else:
                    value = software_param["defaultParamValue"]

                JobParameter(self._job.id, software_param["id"], value).save()

    def close(self, value):
        """
        Notify the Cytomine server of the job's end
        Incurs a dataflows
        """
        if value is None:
            status = Job.TERMINATED
            status_comment = "Job successfully terminated"
        else:
            status = Job.FAILED
            status_comment = str(value)[:255]

        self._job.status = status
        self._job.statusComment = status_comment 
        self._job.update()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.close(value)
        return False

    def job_logger(self, start=0, end=100, period=None):
        """Return a logger for the current job."""
        return CytomineJobLogger(self, start=start, end=end, period=period)

    def monitor(self, iterable, start=0, end=100, period=None, prefix=""):
        """Return a monitor for the current job"""
        return self.job_logger(start=start, end=end, period=period).monitor(iterable, prefix=prefix)


class CytomineJobLogger(object):
    def __init__(self, cytomine_job, start=0, end=100, period=None):
        """A logger serves as intermediary between the job implementation and the job status update requests.

        Parameters
        ----------
        cytomine_job: CytomineJob
            The job
        start: float (range: [0.0, 100.0[)
            Progress at which the logger should start
        end: float (range: ]0.0, 100.0])
            Progress at which the logger should stop
        period: int, float
            The number of iteration to wait before actually updating the status. Also supports
            frequencies (float values).
        """
        self._cytomine_job = cytomine_job
        self._start = start
        self._end = end
        self._update_period = period

    def abs_update(self, statusComment="", status=Job.RUNNING, progress=None):
        """Update the status with an absolute progress (i.e. integer percentage)

        Parameters
        ----------
        statusComment: str
            Status comment
        status: int
            Job status.
        progress: int
            An integer percentage of progress
        """
        self.update(statusComment=statusComment, status=status, current=int(progress), total=100)

    def update(self, statusComment, current, total, status=Job.RUNNING):
        """
        Parameters
        ----------
        statusComment: str
            Job status update message
        current: int (range: [0, total[)
            Current iteration
        total: int
            Total number of iteration
        status: int
            Status of the job to send with the update
        """
        period = self._get_period(total)
        if period is not None and current % period != 0:
            return
        relative_progress = self._relative_progress(current / float(total))
        self._cytomine_job.job.update(progress=relative_progress, statusComment=statusComment, status=status)

    def _get_period(self, n_iter):
        """Return integer period given a maximum number of iteration """
        if self._update_period is None:
            return None
        if isinstance(self._update_period, float):
            return max(int(self._update_period * n_iter), 1)
        return self._update_period

    def _relative_progress(self, ratio):
        return int(self._start + (self._end - self._start) * ratio)

    def logger(self, progress_start, progress_end, update_period=None):
        """Return a logger that updates progress in a subrange of the current logger's range."""
        return CytomineJobLogger(
            self._cytomine_job,
            start=self._relative_progress(progress_start / 100.),
            end=self._relative_progress(progress_end / 100.),
            period=update_period
        )

    def monitor(self, iterable, prefix=""):
        """Return a monitor for the given iterable using this logger"""
        return CytomineJobProgressMonitor(self, iterable, comment_prefix=prefix)


class CytomineJobProgressMonitor(object):
    def __init__(self, cytomine_logger, iterable, comment_prefix=None):
        """
        cytomine_logger: CytomineJobLogger
            A logger
        iterable: iterable
            The iterable to iterate on
        comment_prefix: str
            A prefix for the status comment
        """
        self._cytomine_logger = cytomine_logger
        self._iterable = list(iterable)
        self._comment_prefix = comment_prefix

    def __iter__(self):
        for i, v in enumerate(self._iterable):
            self._cytomine_logger.update(
                "{} ({}/{}).".format(self._comment_prefix, i + 1, len(self)),
                current=i, total=len(self)
            )
            yield v

    def __len__(self):
        return len(list(self._iterable))

