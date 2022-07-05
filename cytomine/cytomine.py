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

try:
    from json.decoder import JSONDecodeError
except ImportError:
    # Python 2
    JSONDecodeError = ValueError

import logging
import base64
import hashlib
import hmac
import sys
import os
import requests
import shutil
import warnings
import functools
import time
from time import strftime, gmtime
from future.builtins import bytes
from argparse import ArgumentParser
from cachecontrol import CacheControlAdapter
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.utils import dump

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>", "Burtin Elodie <elodie.burtin@cytomine.coop"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"


def _cytomine_parameter_name_synonyms(name, prefix="--"):
    """For a given parameter name, returns all the possible usual synonym (and the parameter itself). Optionally, the
    function can prepend a string to the found names.

    If a parameters has no known synonyms, the function returns only the prefixed $name.

    Parameters
    ----------
    name: str
        Parameter based on which synonyms must searched for
    prefix: str
        The prefix

    Returns
    -------
    names: str
        List of prefixed parameter names containing at least $name (preprended with $prefix).
    """
    synonyms = [
        ["host", "cytomine_host"],
        ["public_key", "publicKey", "cytomine_public_key"],
        ["private_key", "privateKey", "cytomine_private_key"],
        ["base_path", "basePath", "cytomine_base_path"],
        ["id_software", "cytomine_software_id", "cytomine_id_software", "idSoftware", "software_id"],
        ["id_project", "cytomine_project_id", "cytomine_id_project", "idProject", "project_id"]
    ]
    synonyms_dict = {params[i]: params[:i] + params[(i + 1):] for params in synonyms for i in range(len(params))}

    if name not in synonyms_dict:
        return [prefix + name]

    return [prefix + n for n in ([name] + synonyms_dict[name])]


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


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def read_response_message(response, key='message', encoding="utf-8"):
    content = response.content.decode(encoding)
    try:
        return response.json().get(key, content)
    except JSONDecodeError:
        return content

class URLRedirectionException(BaseException):
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.message = f"HTTP return code : {status_code}. URL was redirected to {url}."
        super().__init__(self.message)

class Cytomine(object):
    __instance = None

    def __init__(self, host, public_key, private_key, verbose=None,
                 use_cache=True, protocol=None, working_path="/tmp",
                 configure_logging=True, **kwargs):
        """
        Initialize the Cytomine Python client which is a singleton.

        Parameters
        ----------
        host : str
            The Cytomine host (with or without protocol).
        public_key : str
            The Cytomine public key.
        private_key : str
            The Cytomine private key.
        verbose : int or str (optional)
            The verbosity level of the client as a valid Python logging level.
        use_cache : bool
            True to use HTTP cache, False otherwise.
        protocol : str ("http", "https", "http://", "https://") (optional)
            The default protocol - used only if the host value does not specify one
        working_path : str
            Deprecated. Only for backwards compatibility.
        configure_logging : bool
            Whether the Cytomine Python Client has to configure logging (with
            `basicConfig`) if the root logger has no handler already configured.
            Default value is True to mimic backwards compatibility.
            Starting v3.x, default value should be set to False.
        kwargs : dict
            Deprecated arguments.
        """
        self._host, self._protocol = self._parse_url(host, protocol)
        self._public_key = public_key
        self._private_key = private_key

        self._use_cache = use_cache
        self._base_path = "/api/"

        if configure_logging:
            logging.basicConfig(
                stream=sys.stdout,
                format="[%(asctime)s][%(levelname)s] %(message)s"
            )

        self._logger = logging.getLogger("cytomine.client")

        # Deprecated adding of logging handlers - To be removed in next major release
        logging_handlers = kwargs.get('logging_handlers', None)
        if logging_handlers:
            for handler in logging_handlers:
                self._logger.addHandler(handler)
        # ---

        if not verbose and self._logger.level == logging.NOTSET:
            # Here for backwards compatibility, but the logging level should be
            # set by the application and not this low-level library.
            log_level = logging.INFO
        elif type(verbose) is str:
            log_level = logging.getLevelName(verbose)
        elif verbose is None:
            log_level = self._logger.level
        else:
            log_level = verbose
        self._verbose = log_level
        self._logger.setLevel(log_level)

        if log_level == logging.DEBUG:
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client

            http_client.HTTPConnection.debuglevel = 1
            requests_log = logging.getLogger("urllib3")
            requests_log.setLevel(logging.DEBUG)

        # Deprecated
        self._working_path = working_path

        # Should be only in connect() and __enter__(), but here for backwards compatibility.
        self._start()

    @classmethod
    def connect(cls, host, public_key, private_key, verbose=0, use_cache=True):
        """
        Connect the client with the given host and the provided credentials.

        Parameters
        ----------
        host : str
            The Cytomine host (without protocol).
        public_key : str
            The Cytomine public key.
        private_key : str
            The Cytomine private key.
        verbose : int
            The verbosity level of the client.
        use_cache : bool
            True to use HTTP cache, False otherwise.

        Returns
        -------
        client : Cytomine
            A connected Cytomine client.
        """
        return cls(host, public_key, private_key, verbose, use_cache)

    @classmethod
    def connect_from_cli(cls, argv, use_cache=True):
        """
        Connect with data taken from a command line interface.

        Parameters
        ----------
        argv: list
            Command line parameters (executable name excluded)
        use_cache : bool
            True to use HTTP cache, False otherwise.

        Returns
        -------
        client : Cytomine
            A connected Cytomine client.

        Notes
        -----
        If some parameters are invalid, the function stops the execution and displays an help.
        """
        argparse = cls._add_cytomine_cli_args(ArgumentParser())
        params, _ = argparse.parse_known_args(args=argv)
        log_level = params.verbose
        if params.log_level is not None:
            log_level = logging.getLevelName(params.log_level)
        return cls.connect(params.host, params.public_key, params.private_key, log_level, use_cache=use_cache)

    @staticmethod
    def _add_cytomine_cli_args(argparse):
        """
        Add cytomine CLI args to the ArgumentParser object: cytomine_host, cytomine_public_key, cytomine_private_key and
        cytomine_verbose.

        Parameters
        ----------
        argparse: ArgumentParser
            The argument parser

        Return
        ------
        argparse: ArgumentParser
            The argument parser (same object as parameter)
        """
        argparse.add_argument(*_cytomine_parameter_name_synonyms("host"),
                              dest="host", help="The Cytomine host (without protocol).", required=True)
        argparse.add_argument(*_cytomine_parameter_name_synonyms("public_key"),
                              dest="public_key", help="The Cytomine public key.", required=True)
        argparse.add_argument(*_cytomine_parameter_name_synonyms("private_key"),
                              dest="private_key", help="The Cytomine private key.", required=True)
        argparse.add_argument("--verbose", "--cytomine_verbose",
                              dest="verbose", type=int, default=logging.INFO,
                              help="The verbosity level of the client (as an integer value).")
        argparse.add_argument("-l", "--log_level", "--cytomine_log_level",
                              dest="log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                              help="The logging level of the client (as a string value)")
        return argparse

    @staticmethod
    def _parse_url(host, provided_protocol=None):
        """
        Process the provided host and protocol to return them in a standardized
        way that can be subsequently used by Cytomine methods.
        If the protocol is not specified, HTTP is the default.
        Only HTTP and HTTPS schemes are supported.

        Parameters
        ----------
        host: str
            The host, with or without the protocol
        provided_protocol: str ("http", "http://", "https", "https://")
            The default protocol - used only if the host value does not specify one

        Return
        ------
        (host, protocol): tuple
            The host and protocol in a standardized way (host without protocol,
            and protocol in ("http", "https"))

        Examples
        --------
        >>> Cytomine._parse_url("localhost-core")
        ("localhost-core", "http")
        >>> Cytomine._parse_url("https://demo.cytomine.coop", "http")
        ("demo.cytomine.coop", "https")
        """
        protocol = "http" # default protocol

        if host.startswith("http://"):
            protocol = "http"
        elif host.startswith("https://"):
            protocol = "https"
        elif provided_protocol is not None:
            provided_protocol = provided_protocol.replace("://", "")
            if provided_protocol in ("http", "https"):
                protocol = provided_protocol

        host = host.replace("http://", "").replace("https://", "")
        if host.endswith("/"):
            host = host[:-1]

        return host, protocol

    def _start(self):
        self._session = requests.session()
        if self._use_cache:
            self._session.mount('{}://'.format(self._protocol), CacheControlAdapter())

        Cytomine.__instance = self
        self.wait_to_accept_connection()
        self._current_user = None
        self.set_current_user()

    def __enter__(self):
        # self._start()
        return self

    def __exit__(self, type, value, traceback):
        pass

    @staticmethod
    def get_instance():
        if Cytomine.__instance is None:
            raise ConnectionError("You must be connected to get the Cytomine instance.")
        return Cytomine.__instance

    @property
    def host(self):
        return self._host

    @property
    def current_user(self):
        return self._current_user

    def set_current_user(self):
        from cytomine.models.user import CurrentUser
        self._current_user = CurrentUser().fetch()

    def set_credentials(self, public_key, private_key):
        self._public_key = public_key
        self._private_key = private_key
        self.set_current_user()

    def _base_url(self, with_base_path=True):
        url = "{}://{}".format(self._protocol, self._host)
        if with_base_path:
            url += self._base_path
        return url

    @staticmethod
    def _headers(accept="application/json, */*", content_type=None):
        headers = dict()

        if accept is not None:
            headers['accept'] = accept

        if content_type is not None:
            headers['content-type'] = content_type

        headers['date'] = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime())
        headers['X-Requested-With'] = 'XMLHTTPRequest'

        return headers

    def _log_response(self, response, message):
        try:
            msg = "[{}] {} | {} {}".format(response.request.method, message, response.status_code, response.reason)
            if response.status_code == requests.codes.ok or response.status_code >= requests.codes.server_error:
                self.log(msg)
            elif response.status_code == 301 or response.status_code == 302:
                redirected_url = response.headers['Location']
                raise URLRedirectionException(response.status_code, redirected_url)
            else:
                self.log("{} ({})".format(msg, read_response_message(response, key="errors")), level=logging.ERROR)
            self._logger.debug("DUMP:\n{}".format(dump.dump_all(response).decode("utf-8")))
        except (UnicodeDecodeError, JSONDecodeError) as e:
            self._logger.debug("DUMP:\nImpossible to decode.")
        except URLRedirectionException as e:
            raise

    def log(self, msg, level=logging.INFO):
        self._logger.log(level, msg)

    @property
    def logger(self):
        return self._logger

    def _get(self, uri, query_parameters, with_base_path=True):
        return self._session.get("{}{}".format(self._base_url(with_base_path), uri),
                                 allow_redirects=False,
                                 auth=CytomineAuth(
                                     self._public_key, self._private_key,
                                     self._base_url(), self._base_path),
                                 headers=self._headers(),
                                 params=query_parameters)

    def get(self, uri, query_parameters=None):
        response = self._get(uri, query_parameters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def get_model(self, model, query_parameters=None):
        response = self._get(model.uri(), query_parameters)
        
        if response.status_code == requests.codes.ok:
            response_json = response.json()
            model = model.populate(response_json)
            self._log_response(response, model)
            
        if not response.status_code == requests.codes.ok:
            self._log_response(response, model.uri())
            model = False

        return model

    def get_collection(self, collection, query_parameters=None, append_mode=False):
        response = self._get(collection.uri(), query_parameters)
        if response.status_code == requests.codes.ok:
            collection = collection.populate(response.json(), append_mode)

        self._log_response(response, collection)
        if not response.status_code == requests.codes.ok:
            collection = False

        return collection

    def _put(self, uri, data=None, query_parameters=None):
        return self._session.put("{}{}".format(self._base_url(), uri),
                                 auth=CytomineAuth(
                                     self._public_key, self._private_key,
                                     self._base_url(), self._base_path),
                                 headers=self._headers(content_type='application/json'),
                                 params=query_parameters,
                                 data=data)

    def put(self, uri, data=None, query_paramters=None):
        response = self._put(uri, data=data, query_parameters=query_paramters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def put_model(self, model, query_parameters=None):
        response = self._put(model.uri(), model.to_json(), query_parameters)
        if response.status_code == requests.codes.ok:
            if model.callback_identifier.lower() in response.json() :
                model = model.populate(response.json()[model.callback_identifier.lower()])
            else :
                model = model.populate(response.json()[model.__class__.__name__.lower()]) #remove when REST URL are normalized

        self._log_response(response, model)
        if not response.status_code == requests.codes.ok:
            model = False

        return model

    def _delete(self, uri, query_parameters=None):
        return self._session.delete("{}{}".format(self._base_url(), uri),
                                    auth=CytomineAuth(
                                        self._public_key, self._private_key,
                                        self._base_url(), self._base_path),
                                    headers=self._headers(content_type='application/json'),
                                    params=query_parameters)

    def delete(self, uri, query_parameters=None):
        response = self._delete(uri, query_parameters)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            return True

        return False

    def delete_model(self, model, query_parameters=None):
        response = self._delete(model.uri(), query_parameters)
        self._log_response(response, model)
        if response.status_code == requests.codes.ok:
            return True

        return False

    def _post(self, uri, data=None, query_parameters=None, with_base_path=True):
        return self._session.post("{}{}".format(self._base_url(with_base_path), uri),
                                  auth=CytomineAuth(
                                      self._public_key, self._private_key,
                                      self._base_url(), self._base_path),
                                  headers=self._headers(content_type='application/json'),
                                  params=query_parameters,
                                  data=data)

    def post(self, uri, data=None, query_parameters=None):
        response = self._post(uri, data=data, query_parameters=query_parameters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def post_model(self, model, query_parameters=None):
        response = self._post(model.uri(), model.to_json(), query_parameters)

        if response.status_code == requests.codes.ok:
            try:
                if model.callback_identifier.lower() in response.json() :
                    model = model.populate(response.json()[model.callback_identifier.lower()])
                else :
                    model = model.populate(response.json()[model.__class__.__name__.lower()]) #remove when REST URL are normalized
            except KeyError:
                self._logger.warning(response.json())

        self._log_response(response, model)

        if not response.status_code == requests.codes.ok:
            model = False

        return model

    def post_collection(self, collection, query_parameters=None):
        response = self._post(collection.uri(without_filters=True), collection.to_json(), query_parameters)
        self._log_response(response, read_response_message(response, key="message"))
        return response.status_code == requests.codes.ok

    def open_admin_session(self):
        uri = "/session/admin/open.json"
        response = self._get(uri, None, with_base_path=False)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            self.set_current_user() # refetch user to update *ByNow properties
            # self._current_user.poulate(response.json())
            # response not consistent with the properties returned by user/current.json
            return True
        else:
            return False

    def close_admin_session(self):
        uri = "/session/admin/close.json"
        response = self._get(uri, None, with_base_path=False)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            self.set_current_user() # refetch user to update *ByNow properties
            return True
        else:
            return False

    def is_alive(self):
        uri = "/server/ping"
        try:
            response = self._get(uri, None, with_base_path=False)
            self._log_response(response, uri)
            return response.status_code == requests.codes.ok
        except Exception:
            return False

    def wait_to_accept_connection(self, timeout_in_seconds=120, delay_between_retry_in_seconds=1):
        mustend = time.time() + timeout_in_seconds
        while time.time() < mustend:
            if self.is_alive():
                return True
            time.sleep(delay_between_retry_in_seconds)
        return False


    def upload_file(self, model, filename, query_parameters=None, uri=None):
        if not uri:
            uri = model.uri()

        m = MultipartEncoder(fields={"files[]": (filename, open(filename, 'rb'))})
        response = self._session.post("{}{}".format(self._base_url(), uri),
                                      auth=CytomineAuth(
                                          self._public_key, self._private_key,
                                          self._base_url(), self._base_path),
                                      headers=self._headers(content_type=m.content_type),
                                      params=query_parameters,
                                      data=m)

        if response.status_code == requests.codes.ok:
            model = model.populate(response.json())  # [model.callback_identifier.lower()])
            self._logger.info("File uploaded successfully to {}".format(uri))
        else:
            model = False
            self._logger.error("Error during file uploading to {}".format(uri))

        return model

    def download_file(self, url, destination, override=False, payload=None):
        if not url.startswith("http"):
            url = "{}{}".format(self._base_url(), url)

        if override or not os.path.exists(destination):
            response = self._session.get(url,
                                         auth=CytomineAuth(
                                             self._public_key, self._private_key,
                                             self._base_url(), self._base_path),
                                         headers=self._headers(content_type='application/json'),
                                         params=payload,
                                         stream=True)

            if not response.status_code == requests.codes.ok:
                self._log_response(response, url)
                return False

            with open(destination, "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

                parameters = str(dict(filter(lambda item: item[1] is not None, payload.items()))) if payload else {}
                self._logger.info("File downloaded successfully from {} with parameters {}".format(url, parameters))
            return True
        else:
            return True

    def upload_image(self, upload_host, filename, id_storage, id_project=None,
                     properties=None, sync=False, protocol=None):
        if not protocol:
            protocol = self._protocol
        upload_host, protocol = self._parse_url(upload_host, protocol)
        upload_host = "{}://{}".format(protocol, upload_host)

        cytomine_core = "{}://{}".format(self._protocol, self._host)
        query_parameters = {
            "idStorage": id_storage,  # backwards compatibility
            "storage": id_storage,
            "cytomine": cytomine_core,  # backwards compatibility
            "core": cytomine_core,
            "sync": sync
        }

        if id_project:
            query_parameters["idProject"] = id_project  # backwards compatibility
            query_parameters["projects"] = id_project

        if properties:
            query_parameters["keys"] = ','.join(list(properties.keys()))
            query_parameters["values"] = ','.join(list(properties.values()))

        m = MultipartEncoder(fields={"files[]": (filename, open(filename, 'rb'))})
        response = self._session.post("{}/upload".format(upload_host),
                                      auth=CytomineAuth(
                                          self._public_key, self._private_key,
                                          upload_host, ""),
                                      headers=self._headers(content_type=m.content_type),
                                      params=query_parameters,
                                      data=m)

        if response.status_code == requests.codes.ok:
            uf = self._process_upload_response(response.json()[0])
            self._logger.info("Image uploaded successfully to {}".format(upload_host))
            return uf
        else:
            self._logger.error("Error during image upload.")
            return False

    def upload_crop(self, ims_host, filename, id_annot, id_storage,
                id_project=None, sync=False, protocol=None):
        """
        Upload the crop associated with an annotation as a new image.

        Parameters
        ----------
        ims_host: str
            Cytomine IMS host, with or without the protocol
        filename: str
            Filename to give to the newly created image
        id_annot: int
            Identifier of the annotation to crop
        id_storage: int
            Identifier of the storage to use to upload the new image
        id_project: int, optional
            Identifier of a project in which the new image should be added
        sync: bool, optional
            True:   the server will answer once the uploaded file is
                    deployed (response will include the created image)
            False (default): the server will answer as soon as it receives the file
        protocol: str ("http", "http://", "https", "https://")
            The default protocol - used only if the host value does not specify one

        Return
        ------
        uf: UploadedFile
            The uploaded file. Its images attribute is populated with the collection of created abstract images.
        """

        if not protocol:
            protocol = self._protocol
        ims_host, protocol = self._parse_url(ims_host, protocol)
        ims_host = "{}://{}".format(protocol, ims_host)

        query_parameters = {
            "annotation" : id_annot,
            "storage": id_storage,
            "cytomine": "{}://{}".format(self._protocol, self._host),
            "name": filename,
            "sync": sync
        }

        if id_project:
            query_parameters["project"] = id_project

        response = self._session.post("{}/uploadCrop".format(ims_host),
                                      auth=CytomineAuth(
                                          self._public_key,
                                          self._private_key,
                                          ims_host, ""),
                                      headers=self._headers(),
                                      params=query_parameters)

        if response.status_code == requests.codes.ok:
            uf = self._process_upload_response(response.json())
            self._logger.info("Image crop uploaded successfully to {}".format(ims_host))
            return uf
        else:
            self._logger.error("Error during crop upload. Response: %s", response)
            return False

    def _process_upload_response(self, response_data):
        from .models.storage import UploadedFile
        from .models.image import AbstractImage, AbstractSliceCollection, AbstractSlice, ImageInstance, \
            ImageInstanceCollection, AbstractImageCollection

        self._logger.debug("Entering _process_upload_response(response_data=%s)", response_data)

        if "uploadFile" in response_data:
            # backwards compatibility
            uf = UploadedFile().populate(response_data["uploadFile"])

            uf.images = AbstractImageCollection()
            if "images" in response_data:
                for image in response_data["images"]:
                    if "attr" in image:
                        uf.images.append(AbstractImage().populate(image["attr"]))

            return uf
        else:
            uf = UploadedFile().populate(response_data["uploadedFile"])

            uf.images = []
            if "images" in response_data:
                for image in response_data["images"]:
                    data = dict()

                    if "slices" in image:
                        abstract_slices = AbstractSliceCollection()
                        for abstract_slice in image["slices"]:
                            abstract_slices.append(AbstractSlice().populate(abstract_slice))
                        data["abstractSlices"] = abstract_slices

                    if "imageInstances" in image:
                        image_instances = ImageInstanceCollection()
                        for image_instance in image["imageInstances"]:
                            image_instances.append(ImageInstance().populate(image_instance))
                        data["imageInstances"] = image_instances

                    if "image" in image:
                        data["abstractImage"] = AbstractImage().populate(image["image"])
                    uf.images.append(data)

            return uf

    """
    Following methods are deprecated methods, only temporary here for backwards compatibility.
    Do not use them on new projects.
    Please update your existing projects with client's new methods.
    All old methods (should) have an equivalent with this new client, except:
    - add_user_job() : use CytomineJob utility instead.
    - union_polygons() : already deprecated in previous client.
    - upload_job_data_file() : already in add_job_data()
    """

    # Project
    @deprecated
    def add_project(self, project_name, id_ontology):
        from .models.project import Project
        return Project(project_name, id_ontology).save()

    @deprecated
    def edit_project(self, id_project, project_name, id_ontology):
        from .models.project import Project
        project = Project().fetch(id_project)
        project.name = project_name
        project.ontology = id_ontology
        return project.update()

    @deprecated
    def delete_project(self, id_project):
        from .models.project import Project
        return Project().delete(id_project)

    @deprecated
    def get_project(self, id_project):
        from .models.project import Project
        return Project().fetch(id_project)

    @deprecated
    def get_projects(self):
        from .models.project import ProjectCollection
        return ProjectCollection().fetch()

    # Ontology
    @deprecated
    def add_ontology(self, name):
        from .models.ontology import Ontology
        return Ontology(name).save()

    @deprecated
    def delete_ontology(self, id_ontology):
        from .models.ontology import Ontology
        return Ontology().delete(id_ontology)

    @deprecated
    def get_ontology(self, id_ontology):
        from .models.ontology import Ontology
        return Ontology().fetch(id_ontology)

    # Term
    @deprecated
    def add_term(self, name, id_ontology, color="#ff0000"):
        from .models.ontology import Term
        return Term(name, id_ontology, color).save()

    @deprecated
    def delete_term(self, id_term):
        from .models.ontology import Term
        return Term().delete(id_term)

    @deprecated
    def get_term(self, id_term):
        from .models.ontology import Term
        return Term().fetch(id_term)

    @deprecated
    def get_terms(self, id_ontology=None):
        from .models.ontology import TermCollection
        terms = TermCollection()
        if id_ontology:
            terms.filters["ontology"] = id_ontology
        return terms.fetch()

    @deprecated
    def add_relation_term(self, id_parent, id_child):
        from .models.ontology import RelationTerm
        return RelationTerm(id_parent, id_child).save()

    # uploadedfile
    @deprecated
    def get_uploaded_file(self, id_uploaded_file):
        from .models.storage import UploadedFile
        return UploadedFile().fetch(id_uploaded_file)

    # storage
    @deprecated
    def get_storage(self, id_storage):
        from .models.storage import Storage
        return Storage().fetch(id_storage)

    # annotations
    @deprecated
    def get_annotation(self, id_annotation=None):
        from .models.annotation import Annotation, AnnotationCollection
        if id_annotation:
            return Annotation().fetch(id_annotation)
        else:
            return AnnotationCollection().fetch()

    @deprecated
    def get_annotations(self, id_project=None, id_user=None, id_image=None, id_term=None, showGIS=None,
                        showWKT=None, showMeta=None, bbox=None, id_bbox=None, reviewed_only=False):
        from .models.annotation import AnnotationCollection
        return AnnotationCollection(project=id_project, user=id_user, image=id_image, term=id_term,
                                    showMeta=showMeta, bbox=bbox, bboxAnnotation=id_bbox, reviewed=reviewed_only,
                                    showTerm=(showMeta or showGIS or showWKT)).fetch()

    @deprecated
    def get_reviewed_annotations(self, id_project=None):
        from .models.annotation import AnnotationCollection
        return AnnotationCollection(project=id_project, reviewed=True, showMeta=True,
                                    showTerm=True, showGIS=True).fetch()

    @deprecated
    def included_annotations(self, id_image, id_user, id_annotation_roi, id_terms=None, reviewed_only=False):
        from .models.annotation import AnnotationCollection

        if not id_terms:
            id_terms = []

        return AnnotationCollection(user=id_user, image=id_image, terms=id_terms, reviewed=reviewed_only,
                                    included=True, annotation=id_annotation_roi).fetch()

    @deprecated
    def add_annotation(self, location, id_image, minPoint=None, maxPoint=None):
        from .models.annotation import Annotation
        annotation = Annotation(location, id_image)
        annotation.query_parameters["minPoint"] = minPoint
        annotation.query_parameters["maxPoint"] = maxPoint
        annotation.save()

    @deprecated
    def add_annotations(self, locations, id_image):
        return self.add_annotations_with_term(locations, id_image, None)

    @deprecated
    def add_annotations_with_term(self, locations, id_image, id_term):
        from .models.image import ImageInstance
        from .models.annotation import Annotation, AnnotationCollection
        image = ImageInstance.fetch(id_image)
        id_term = [id_term] if id_term else None
        collection = AnnotationCollection()
        [collection.append(Annotation(location, id_image, id_term, image.project)) for location in locations]
        return collection

    @deprecated
    def delete_annotation(self, id_annotation):
        from .models.annotation import Annotation
        return Annotation().delete(id_annotation)

    @deprecated
    def dump_annotations(self, annotations, get_image_url_func=None, dest_path="/tmp", override=False,
                         excluded_terms=None, desired_zoom=None, desired_max_size=None, tile_size=None,
                         translate=None):
        from .models.annotation import Annotation

        if not excluded_terms:
            excluded_terms = []

        mask = False
        alpha = False
        if get_image_url_func == Annotation.get_annotation_alpha_crop_url:
            mask = True
            alpha = True
        elif get_image_url_func == Annotation.get_annotation_mask_url:
            mask = True
            alpha = False
        else:
            NotImplementedError("Crop tiled translated not implemented")
            # # extend the area to use a fixed-size tile (assuming the tile is larger than the annotation bounding box)
            # # print "Fixed tile cropURL"
            # p_annotation = self.get_annotation(annot.id)
            # p = loads(p_annotation.location)
            # minx, miny, maxx, maxy = int(p.bounds[0]), int(p.bounds[1]), int(p.bounds[2]), int(p.bounds[3])
            # image = self.get_image_instance(p_annotation.image)
            # for t in range(0, translate):
            #     original_cropURL = get_image_url_func(annot, desired_zoom, desired_max_size)
            #     # print "original cropURL = %s" % original_cropURL
            #     cropURL = self.__protocol + self.__host + self.__base_path
            # + Annotation.get_annotation_crop_tiled_translated(
            #         annot, minx, maxx, miny, maxy, p_annotation.image, image.height, tile_size, translate)
            #     # print "tiled cropURL: %s" % cropURL
            #     filename = "%s/%d_%d_%d_translated_%d.png" % (termPath, annot.image, annot.id, tile_size, t)
            #     # queue.put((cropURL, filename, annot))

        dest_pattern = os.path.join(dest_path, "{term}", "{image}_{id}.png")
        for annotation in annotations:
            for term in annotation.term:
                if term in excluded_terms:
                    continue
                annotation.dump(dest_pattern, override, mask, alpha, bits=8, zoom=desired_zoom,
                                max_size=desired_max_size)

        return annotations

    # annotation_term
    @deprecated
    def add_annotation_term(self, id_annotation, term, expected_term, rate, annotation_term_model=None):
        from .models.annotation import AnnotationTerm, AlgoAnnotationTerm
        if annotation_term_model == AlgoAnnotationTerm:
            return AlgoAnnotationTerm(id_annotation, term, expected_term, rate).save()
        else:
            return AnnotationTerm(id_annotation, term).save()

    @deprecated
    def add_user_annotation_term(self, id_annotation, term):
        return self.add_annotation_term(id_annotation, term, None, None)

    # abstract image
    @deprecated
    def get_image(self, id_image):
        from .models.image import AbstractImage
        return AbstractImage().fetch(id_image)

    @deprecated
    def edit_image(self, id_image, filename=None, path=None, mime=None, id_sample=None, id_scanner=None,
                   magnification=None, resolution=None):
        from .models.image import AbstractImage
        image = AbstractImage()
        image = image.fetch(id_image)
        image.filename = filename if filename else image.filename
        image.path = path if path else image.path
        image.mime = mime if mime else image.mime
        image.scanner = id_scanner if id_scanner else image.scanner
        image.sample = id_sample if id_sample else image.sample
        image.magnification = magnification if magnification else image.magnification
        image.resolution = resolution if resolution else image.resolution
        image.update()

    @deprecated
    def delete_image(self, id_image):
        from .models.image import AbstractImage
        return AbstractImage().delete(id_image)

    # image_instance
    @deprecated
    def add_image_instance(self, id_base_image, id_project):
        from .models.image import ImageInstance
        return ImageInstance(id_base_image, id_project).save()

    @deprecated
    def delete_image_instance(self, id_image_instance):
        from .models.image import ImageInstance
        return ImageInstance().delete(id_image_instance)

    @deprecated
    def get_image_instance(self, id_image_instance, include_server_urls=False):
        from .models.image import ImageInstance
        image = ImageInstance().fetch(id_image_instance)

        if include_server_urls:
            image.image_servers()

        return image

    @deprecated
    def get_project_image_instances(self, id_project):
        from .models.image import ImageInstanceCollection
        return ImageInstanceCollection(filters={"project": id_project}).fetch()

    @deprecated
    def dump_project_images(self, id_project=None, dest_path="imageinstances/", override=False,
                            image_instances=None, max_size=None):
        from .models.image import ImageInstanceCollection

        dest_pattern = os.path.join(self._working_path, dest_path, "{project}", "{id}.jpg")

        if not image_instances:
            image_instances = ImageInstanceCollection({"project": id_project}).fetch()
        for image_instance in image_instances:
            image_instance.dump(dest_pattern, override, max_size=max_size)

        return image_instances

    # imagegroup
    @deprecated
    def get_image_group(self, id_image_group=None):
        from .models.imagegroup import ImageGroup, ImageGroupCollection
        if id_image_group:
            return ImageGroup().fetch(id_image_group)
        else:
            return ImageGroupCollection().fetch()

    @deprecated
    def delete_image_group(self, id_image_group):
        from .models.imagegroup import ImageGroup
        return ImageGroup().delete(id_image_group)

    # software
    @deprecated
    def get_software(self, id_software):
        from .models.software import Software
        return Software().fetch(id_software)

    @deprecated
    def add_software(self, name, service_name, result_name, execute_command=None):
        from .models.software import Software
        return Software(name, service_name, result_name, execute_command).save()

    # software project
    @deprecated
    def add_software_project(self, project, software):
        from .models.software import SoftwareProject
        return SoftwareProject(software, project).save()

    # software_parameters
    @deprecated
    def add_software_parameter(self, name, id_software, type, default_value, required, index, set_by_server,
                               uri=None, uriPrintAttribut=None, uriSortAttribut=None):
        from .models.software import SoftwareParameter
        return SoftwareParameter(name, type, id_software, default_value, required, index, set_by_server, uri,
                                 uriSortAttribut, uriPrintAttribut).save()

    @deprecated
    def get_software_parameter(self, id_software_parameter):
        from .models.software import SoftwareParameter
        return SoftwareParameter().fetch(id_software_parameter)

    @deprecated
    def delete_software_parameter(self, id_software_parameter):
        from .models.software import SoftwareParameter
        return SoftwareParameter().delete(id_software_parameter)

    # Job
    @deprecated
    def get_job(self, id_job):
        from .models.software import Job
        return Job().fetch(id_job)

    @deprecated
    def update_job_status(self, job, status=None, status_comment=None, progress=None):
        job.status = status if status else job.status
        job.statusComment = status_comment if status_comment else job.statusComment
        job.progress = progress if progress else job.progress
        job.update()

    # Job Parameter
    @deprecated
    def add_job_parameter(self, id_job, id_software_parameter, value):
        from .models.software import JobParameter
        return JobParameter(id_job, id_software_parameter, value).save()

    @deprecated
    def add_job_parameters(self, job, software, values):
        from .models.software import JobParameter, Job
        param_values = {}

        cjob = Job().fetch(job)
        for software_parameter in software.parameters:
            id = software_parameter["id"]
            name = software_parameter["name"]
            if cjob.algoType == "jobtemplate" and name == "annotation":
                print("Do not add annotation param if JobTemplate")
            else:
                if values[name]:
                    v = values[name]
                else:
                    v = software_parameter["defaultParamValue"]
                param_values[id] = name, v
                JobParameter(job, id, v).save()
        return param_values

    # JobTemplate
    @deprecated
    def get_job_template(self, id_job_template):
        from .models.software import JobTemplate
        return JobTemplate.fetch(id_job_template)

    @deprecated
    def add_job_template(self, name, id_project, id_software):
        from .models.software import JobTemplate
        return JobTemplate(name, id_software, id_project).save()

    @deprecated
    def delete_job_template(self, id_job_template):
        from .models.software import JobTemplate
        return JobTemplate().delete(id_job_template)

    # JobData
    @deprecated
    def add_job_data(self, job, key, filename):
        from .models.software import JobData
        job_data = JobData(id_job=job, key=key, filename=filename).save()
        job_data.upload(filename)
        return job_data

    @deprecated
    def get_job_data_file(self, id_job_data, dest_path):
        from .models.software import JobData
        return JobData().fetch(id_job_data).download(dest_path)

    # positions
    @deprecated
    def get_positions(self, id_image, id_user=None, showDetails=None, afterthan=None,
                      beforethan=None, maxperpage=None):
        from .models.social import PositionCollection
        positions = PositionCollection(filters={"imageinstance": id_image}, max=maxperpage)
        positions.user = id_user
        positions.afterThan = afterthan
        positions.beforeThan = beforethan
        positions.showDetails = showDetails
        return positions.fetch()

    # User
    @deprecated
    def get_user(self, id_user=None):
        from .models.user import User, UserCollection
        if id_user:
            return User().fetch(id_user)
        else:
            return UserCollection().fetch()

    @deprecated
    def get_project_users(self, id_project):
        from .models.user import UserCollection
        return UserCollection(filters={"project": id_project}).fetch()

    @deprecated
    def get_current_user(self):
        return self.current_user

    @deprecated
    def add_user(self, username, firstname, lastname, email, password):
        from .models.user import User
        return User(username, firstname, lastname, email, password).save()

    @deprecated
    def edit_user(self, id_user, username, firstname, lastname, email, password):
        from .models.user import User
        user = User().fetch(id_user)
        user.username = username
        user.firstname = firstname
        user.lastname = lastname
        user.email = email
        user.password = password
        return user.update()

    @deprecated
    def delete_user(self, id_user):
        from .models.user import User
        return User().delete(id_user)

    @deprecated
    def add_user_job(self, software, project):
        from .models.user import User
        from .models.software import Job
        job = Job(project, software).save()
        return User().fetch(job.userJob)

    # Role
    @deprecated
    def get_role(self, id):
        from .models.user import Role
        return Role().fetch(id)

    @deprecated
    def get_roles(self, filter_by_authority=None):
        # filter_by_authority : ROLE_USER or ROLE_ADMIN
        from .models.user import RoleCollection
        roles = RoleCollection().fetch()
        if filter_by_authority:
            roles = [role for role in roles if role.authority == filter_by_authority]
        return roles

    # UserRole
    @deprecated
    def add_user_role(self, id_user, id_role):
        from .models.user import UserRole
        return UserRole(id_user, id_role).save()

    @deprecated
    def delete_user_role(self, id_user, id_role):
        from .models.user import UserRole
        return UserRole().fetch(id_user, id_role).delete()

    @deprecated
    def get_user_role(self, id_user=None, id_role=None):
        from .models.user import UserRole
        return UserRole().fetch(id_user, id_role)

    # group
    @deprecated
    def add_group(self, name):
        from .models.user import Group
        return Group(name).save()

    @deprecated
    def get_group(self, id_group=None):
        from .models.user import Group, GroupCollection
        if id_group:
            return Group().fetch(id_group)
        else:
            return GroupCollection().fetch()

    @deprecated
    def edit_group(self, id_group, name):
        from .models.user import Group
        group = Group().fetch(id_group)
        group.name = name
        return group.update()

    @deprecated
    def delete_group(self, id_group):
        from .models.user import Group
        return Group().delete(id_group)

    # userGroup
    @deprecated
    def add_user_group(self, id_user, id_group):
        from .models.user import UserGroup
        return UserGroup(id_user, id_group).save()

    @deprecated
    def get_user_group(self, id_user, id_group):
        from .models.user import UserGroup
        return UserGroup().fetch(id_user, id_group)

    @deprecated
    def delete_user_group(self, id_user, id_group):
        from .models.user import UserGroup
        return UserGroup().fetch(id_user, id_group).delete()

    # property
    @deprecated
    def get_annotation_property(self, annotation_id, annotation_property_id):
        from .models.annotation import Annotation
        from .models.property import Property
        return Property(Annotation().fetch(annotation_id)).fetch(id=annotation_property_id)

    @deprecated
    def add_annotation_property(self, annotation_id, key, value):
        from .models.annotation import Annotation
        from .models.property import Property
        return Property(Annotation().fetch(annotation_id), key, value).save()

    @deprecated
    def edit_annotation_property(self, annotation_id, annotation_property_id, key, value):
        from .models.annotation import Annotation
        from .models.property import Property
        prop = Property(Annotation().fetch(annotation_id)).fetch(annotation_property_id)
        prop.key = key
        prop.value = value
        return prop.update()

    @deprecated
    def delete_annotation_property(self, annotation_id, annotation_property_id):
        from .models.annotation import Annotation
        from .models.property import Property
        return Property(Annotation().fetch(annotation_id)).delete(annotation_property_id)

    @deprecated
    def get_annotation_properties(self, annotation_id):
        from .models.annotation import Annotation
        from .models.property import PropertyCollection
        return PropertyCollection(Annotation().fetch(annotation_id)).fetch()

    @deprecated
    def get_abstract_image_properties(self, abstract_image_id):
        from .models.property import PropertyCollection
        from .models.image import AbstractImage
        ai = AbstractImage()
        ai.id = abstract_image_id
        return PropertyCollection(ai).fetch()

    @deprecated
    def fetch_url_into_file(self, url, filename, is_image=True, override=False):
        return self.download_file(url, filename, override)

    # def __getstate__(self):  # Make cytomine client serializable
    #     self.__conn = None
    #     return self.__dict__
