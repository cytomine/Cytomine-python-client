# -*- coding: utf-8 -*-


#
# * Copyright (c) 2009-2015. Authors: see NOTICE file.
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
# */

__author__          = "Stévens Benjamin <b.stevens@ulg.ac.be>" 
__contributors__    = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]                
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"



from model import Model
from collection import Collection


class Software(Model):
    def __init__(self, params = None):
        super(Software, self).__init__(params)
        self._callback_identifier = "software"

    def to_url(self):
        if hasattr(self, "id"):
            return "software/%d.json" % self.id
        else:
            return "software.json"

    def __str__( self ):
        return "software : " + str(self.id)

class SoftwareProject(Model):
    def __init__(self, params = None):
        super(SoftwareProject, self).__init__(params)
        self._callback_identifier = "softwareproject"

    def to_url(self):
        if hasattr(self, "id"):
            return "softwareproject/%d.json" % self.id
        else:
            return "softwareproject.json"

    def __str__( self ):
        return "softwareproject : " + str(self.id)

class SoftwareParameter(Model):
    def __init__(self, params = None):
        super(SoftwareParameter, self).__init__(params)
        self._callback_identifier = "softwareparameter"

    def to_url(self):
        if hasattr(self, "id"):
            return "softwareparameter/%d.json" % self.id
        else:
            return "softwareparameter.json"

    def __str__( self ):
        return "softwareparameter : " + str(self.id)

class Job(Model):
    
    (RUNNING,TERMINATED,PREVIEW_DONE) = (2,3,7)
	
    def __init__(self, params = None):
        super(Job, self).__init__(params)
        self._callback_identifier = "job"

    def to_url(self):
        if hasattr(self, "id"):
            return "job/%d.json" % self.id        
        else:
            return "job.json"

    def set_running(self):
        self.status = Job.RUNNING
	
    def set_terminated(self):
        self.status = Job.TERMINATED

    def __str__( self ):
        return "Job : " + str(self.id)

class JobParameter(Model):

    def __init__(self, params = None):
        super(JobParameter, self).__init__(params)
        self._callback_identifier = "jobparameter"

    def to_url(self):
        if hasattr(self, "id"):
            return "jobparameter/%d.json" % self.id
        else:
            return "jobparameter.json"

    def __str__( self ):
        return "Jobparameter : " + str(self.id)

class JobData(Model):

    def __init__(self, params = None):
        super(JobData, self).__init__(params)
        self._callback_identifier = "jobdata"

    def to_url(self):
        if hasattr(self, "id"):
            return "jobdata/%d.json" % self.id
        else:
            return "jobdata.json"

    def __str__( self ):
        return "JobData : " + str(self.id)  
