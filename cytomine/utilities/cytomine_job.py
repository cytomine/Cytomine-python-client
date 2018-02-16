# -*- coding: utf-8 -*-
"""
Copyright 2010-2013 University of LiÃ¨ge, Belgium.

This software is provided 'as-is', without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the
use of this software.

Permission is only granted to use this software for non-commercial purposes.
"""

__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__contributors = ["Mormont Romain <romainmormont@gmail.com"]
__copyright__ = "Copyright 2010-2013 University of Liège, Belgium"
__version__ = '0.1'


class CytomineJob(object):
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
    cytomine_client : :class:`Cytomine`
        The Cytomine client through which to communicate with the server
    software_id : int
        The identifier of the software on the Cytomine server
    project_id : int
        The identifier of the project to process on the Cytomine server
    parameters: dict
        A dictionary mapping job parameters with their values (the dictionary must not contain any other key than
        the parameters names)
    """
    def __init__(self, cytomine_client, software_id, project_id, parameters=None):
        self.__cytomine = cytomine_client
        self.__software_id = software_id
        self.__project_id = project_id
        self.__job_done = False
        self.__job = None
        self.__parameters = parameters

    @property
    def job(self):
        """Return the job model

        Return
        ------
        job: cytomine.Job
            The job model
        """
        return self.__job

    @property
    def cytomine_client(self):
        """
        Protected method

        Return
        ------
        cytomine : :class:`Cytomine`
            The Cytomine client
        """
        return self.__cytomine

    @property
    def project_id(self):
        """
        Protected method

        Return
        ------
        project_id : int
            The id of the project
        """
        return self.__project_id

    @property
    def software_id(self):
        """
        Protected method

        Return
        ------
        software_id : int
            The id of the software
        """
        return self.__software_id

    def done(self, status=True):
        """
        Indicates whether the job is finished or not

        Parameters
        ----------
        status : bool
            Whether the process is finished
        """
        self.__job_done = status

    def is_done(self):
        """
        Return
        ------
        job_status : bool
            Whether the process is finished
        """
        return self.__job_done

    def start(self):
        """
        Connect to the Cytomine server and switch to job connection
        Incurs dataflows
        """
        current_user = self.__cytomine.get_current_user()
        if not current_user.algo:  # If user connects as a human (CLI execution)
            user_job = self.__cytomine.add_user_job(
                self.__software_id,
                self.__project_id
            )
            self.__cytomine.set_credentials(
                str(user_job.publicKey),
                str(user_job.privateKey)
            )
        else:  # If the user executes the job through the Cytomine interface
            user_job = current_user

        # set job state to RUNNING
        job = self.__cytomine.get_job(user_job.job)
        self.__job = self.__cytomine.update_job_status(job, status=job.RUNNING)

        # add software parameters
        if self.__parameters is not None:
            software = self.__cytomine.get_software(self.__software_id)
            self.__cytomine.add_job_parameters(self.__job.id, software, self.__parameters)

    def close(self):
        """
        Notify the Cytomine server of the job's end
        Incurs a dataflows
        """
        status = 4  # status code for FAILED
        if self.is_done():
            status = self.__job.TERMINATED

        self.__cytomine.update_job_status(self.__job, status=status)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        if value is None:
            # No exception, job is done
            self.done()
        self.close()
        return False
