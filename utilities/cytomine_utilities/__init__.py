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


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__contributors__ = ["Mormont Romain <romainmormont@gmail.com"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"
__version__ = '0.1'


from .logger import Logger
from .logger import StandardLogger
from .logger import FileLogger
from .logger import VoidLogger
from .logger import ProgressLogger
from .logger import Progressable
from .logger import format_duration
from .logger import format_size

from .taskmanager import TaskSplitter
from .taskmanager import TaskExecutor
from .taskmanager import SerialExecutor
from .taskmanager import ParallelExecutor

from .cytomine_job import CytomineJob

__all__ = [
    "Logger",
    "StandardLogger",
    "FileLogger",
    "VoidLogger",
    "ProgressLogger",
    "Progressable",
    "format_duration",
    "format_size",
    "TaskSplitter",
    "TaskExecutor",
    "SerialExecutor",
    "ParallelExecutor",
    "CytomineJob"
]
