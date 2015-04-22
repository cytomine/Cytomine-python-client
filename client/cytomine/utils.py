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


import threading, Queue
import copy
import progressbar

def parameters_values_to_argv(parameters, parameters_values):
        argv = []
        for key in parameters_values:           
                name, value = parameters_values[key]
                if name in parameters.keys():                   
                        if type(value) is bool or value == 'True':
                                if bool(value):                         
                                        argv.append("--%s" % name)                              
                        elif not value == 'False':
                                argv.append("--%s" % name)
                                argv.append("%s" % value)
                                
        return argv

class ImageFetcher(threading.Thread):
    
    def __init__(self, queue, cytomine,  override, pbar = None, verbose = True):
        threading.Thread.__init__(self)
        self.cytomine = copy.deepcopy(cytomine)
        self.verbose = verbose
        self.override = override
        self.queue = queue
        self.pbar = pbar

    def run(self):
    	while True:
            #grabs host from queue
            url, filename, annotation = self.queue.get()
            download_successful = self.cytomine.fetch_url_into_file(url, filename, self.override)
            if not download_successful:
            	import warnings
            	warnings.warn("Crop Error for annotation %d" % annotation.id)
                if os.path.exists(filename): 
                	os.remove(filename)

            #signals to queue job is done
            #if self.pbar:
             #   self.pbar.update(self.pbar.currval+1)
            self.queue.task_done()
