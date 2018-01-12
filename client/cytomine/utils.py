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
from future.builtins import bytes

import base64
import hashlib
import hmac

import requests.auth

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__copyright__ = "Copyright 2010-2018 University of Liège, Belgium, http://www.cytomine.be/"


class CytomineAuth(requests.auth.AuthBase):
    def __init__(self, public_key, private_key, base_url, base_path, sign_with_base_path=True):
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = base_url
        self.base_path = base_path if sign_with_base_path else ""

    def __call__(self, r):
        content_type = r.headers.get("content-type", "")
        token = "{}\n\n{}\n{}\n{}{}".format(r.method, content_type, r.headers['date'],
                                            self.base_path, r.url.replace(self.base_url, ""))

        signature = base64.b64encode(hmac.new(bytes(self.private_key, 'utf-8'),
                                              token.encode('utf-8'), hashlib.sha1).digest())

        authorization = "CYTOMINE {}:{}".format(self.public_key, signature.decode('utf-8'))
        r.headers['authorization'] = authorization
        return r


# def parameters_values_to_argv(parameters, parameters_values):
#         argv = []
#         for key in parameters_values:
#                 name, value = parameters_values[key]
#                 if name in parameters.keys():
#                         if type(value) is bool or value == 'True':
#                                 if bool(value):
#                                         argv.append("--%s" % name)
#                         elif not value == 'False':
#                                 argv.append("--%s" % name)
#                                 argv.append("%s" % value)
#
#         return argv
#
# class ImageFetcher(threading.Thread):
#
#     def __init__(self, queue, cytomine,  override, pbar = None, verbose = True):
#         threading.Thread.__init__(self)
#         self.cytomine = copy.deepcopy(cytomine)
#         self.verbose = verbose
#         self.override = override
#         self.queue = queue
#         self.pbar = pbar
#
#     def run(self):
#     	while True:
#             #grabs host from queue
#             url, filename, annotation = self.queue.get()
#             download_successful = self.cytomine.fetch_url_into_file(url, filename, self.override)
#             if not download_successful:
#             	import warnings
#             	warnings.warn("Crop Error for annotation %d" % annotation.id)
#                 if os.path.exists(filename):
#                 	os.remove(filename)
#
#             #signals to queue job is done
#             #if self.pbar:
#              #   self.pbar.update(self.pbar.currval+1)
#             self.queue.task_done()
