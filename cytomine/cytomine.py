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

# pylint: disable=import-outside-toplevel

import base64
import functools
import hashlib
import hmac
import http.client as http_client
import logging
import os
import shutil
import sys
import time
import warnings
from argparse import ArgumentParser
from json.decoder import JSONDecodeError
from time import gmtime, strftime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import requests  # type: ignore
from cachecontrol import CacheControlAdapter
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.utils import dump

if TYPE_CHECKING:
    from cytomine.models.collection import Collection
    from cytomine.models.model import Model
    from cytomine.models.storage import UploadedFile
    from cytomine.models.user import CurrentUser


def _cytomine_parameter_name_synonyms(name: str, prefix: str = "--") -> List[str]:
    """For a given parameter name, returns all the possible usual synonym
    (and the parameter itself). Optionally, the
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
        [
            "host",
            "cytomine_host",
        ],
        [
            "public_key",
            "publicKey",
            "cytomine_public_key",
        ],
        [
            "private_key",
            "privateKey",
            "cytomine_private_key",
        ],
        [
            "base_path",
            "basePath",
            "cytomine_base_path",
        ],
        [
            "id_project",
            "cytomine_project_id",
            "cytomine_id_project",
            "idProject",
            "project_id",
        ],
    ]
    synonyms_dict = {
        params[i]: params[:i] + params[(i + 1) :]
        for params in synonyms
        for i in range(len(params))
    }

    if name not in synonyms_dict:
        return [prefix + name]

    return [prefix + n for n in ([name] + synonyms_dict[name])]


class CytomineAuth(requests.auth.AuthBase):
    def __init__(
        self,
        public_key: str,
        private_key: str,
        base_url: str,
        base_path: str,
        sign_with_base_path: bool = True,
    ) -> None:
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = base_url
        self.base_path = base_path if sign_with_base_path else ""

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        content_type = r.headers.get("content-type", "")
        token = (
            f"{r.method}\n\n"
            f"{content_type}\n"
            f"{r.headers['date']}\n"
            f"{self.base_path}"
            f"{r.url.replace(self.base_url, '')}"  # type: ignore
        )

        signature = base64.b64encode(
            hmac.new(
                bytes(self.private_key, "utf-8"),
                token.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        )

        authorization = f"CYTOMINE {self.public_key}:{signature.decode('utf-8')}"
        r.headers["authorization"] = authorization
        return r


def deprecated(func: Callable[..., Any]) -> Callable[..., Any]:
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args: Any, **kwargs: Any) -> Any:
        warnings.simplefilter("always", DeprecationWarning)  # turn off filter
        warnings.warn(
            f"Call to deprecated function {func.__name__}.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        warnings.simplefilter("default", DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


def read_response_message(
    response: requests.Response,
    key: str = "message",
    encoding: str = "utf-8",
) -> str:
    content = response.content.decode(encoding)
    try:
        return response.json().get(key, content)
    except JSONDecodeError:
        return content


class URLRedirectionException(BaseException):
    def __init__(self, status_code: int, url: str) -> None:
        self.status_code = status_code
        self.message = f"HTTP return code : {status_code}. URL was redirected to {url}."
        super().__init__(self.message)


class Cytomine:
    __instance = None

    def __init__(
        self,
        host: str,
        public_key: str,
        private_key: str,
        verbose: Optional[int] = None,
        use_cache: bool = True,
        protocol: Optional[str] = None,
        working_path: str = "/tmp",
        configure_logging: bool = True,
        **kwargs: Any,
    ) -> None:
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
        self._current_user = None

        if configure_logging:
            logging.basicConfig(
                stream=sys.stdout,
                format="[%(asctime)s][%(levelname)s] %(message)s",
            )

        self._logger = logging.getLogger("cytomine.client")

        # Deprecated adding of logging handlers - To be removed in next major release
        logging_handlers = kwargs.get("logging_handlers", None)
        if logging_handlers:
            for handler in logging_handlers:
                self._logger.addHandler(handler)
        # ---

        if not verbose and self._logger.level == logging.NOTSET:
            # Here for backwards compatibility, but the logging level should be
            # set by the application and not this low-level library.
            log_level = logging.INFO
        elif isinstance(verbose, str):
            log_level = logging.getLevelName(verbose)
        elif verbose is None:
            log_level = self._logger.level
        else:
            log_level = verbose
        self._verbose = log_level
        self._logger.setLevel(log_level)

        if log_level == logging.DEBUG:
            http_client.HTTPConnection.debuglevel = 1
            requests_log = logging.getLogger("urllib3")
            requests_log.setLevel(logging.DEBUG)

        # Deprecated
        self._working_path = working_path

        # Should be only in connect() and __enter__(), but here for backwards compatibility.
        self._start()

    @classmethod
    def connect(
        cls,
        host: str,
        public_key: str,
        private_key: str,
        verbose: int = 0,
        use_cache: bool = True,
    ) -> "Cytomine":
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
    def connect_from_cli(cls, argv: List[str], use_cache: bool = True) -> "Cytomine":
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
        return cls.connect(
            params.host,
            params.public_key,
            params.private_key,
            log_level,
            use_cache=use_cache,
        )

    @staticmethod
    def _add_cytomine_cli_args(argparse: ArgumentParser) -> ArgumentParser:
        """
        Add cytomine CLI args to the ArgumentParser object:
        cytomine_host,
        cytomine_public_key,
        cytomine_private_key and
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
        argparse.add_argument(
            *_cytomine_parameter_name_synonyms("host"),
            dest="host",
            help="The Cytomine host (without protocol).",
            required=True,
        )
        argparse.add_argument(
            *_cytomine_parameter_name_synonyms("public_key"),
            dest="public_key",
            help="The Cytomine public key.",
            required=True,
        )
        argparse.add_argument(
            *_cytomine_parameter_name_synonyms("private_key"),
            dest="private_key",
            help="The Cytomine private key.",
            required=True,
        )
        argparse.add_argument(
            "--verbose",
            "--cytomine_verbose",
            dest="verbose",
            type=int,
            default=logging.INFO,
            help="The verbosity level of the client (as an integer value).",
        )
        argparse.add_argument(
            "-l",
            "--log_level",
            "--cytomine_log_level",
            dest="log_level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="The logging level of the client (as a string value)",
        )
        return argparse

    @staticmethod
    def _parse_url(
        host: str,
        provided_protocol: Optional[str] = None,
    ) -> Tuple[str, str]:
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
        protocol = "http"  # default protocol

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

    def _start(self) -> None:
        self._session = requests.session()
        if self._use_cache:
            self._session.mount(f"{self._protocol}://", CacheControlAdapter())

        Cytomine.__instance = self
        self.wait_to_accept_connection()
        self._current_user = None
        self.set_current_user()

    def __enter__(self) -> "Cytomine":
        # self._start()
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self._session.close()

    @staticmethod
    def get_instance() -> "Cytomine":
        if Cytomine.__instance is None:
            raise ConnectionError("You must be connected to get the Cytomine instance.")
        return Cytomine.__instance

    @property
    def host(self) -> str:
        return self._host

    @property
    def current_user(self) -> Optional["CurrentUser"]:
        return self._current_user

    def set_current_user(self) -> None:
        from cytomine.models.user import CurrentUser

        self._current_user = CurrentUser().fetch()  # type: ignore

    def set_credentials(self, public_key: str, private_key: str) -> None:
        self._public_key = public_key
        self._private_key = private_key
        self.set_current_user()

    def _base_url(self, with_base_path: bool = True) -> str:
        url = f"{self._protocol}://{self._host}"
        if with_base_path:
            url += self._base_path
        return url

    @staticmethod
    def _headers(
        accept: str = "application/json, */*",
        content_type: Optional[str] = None,
    ) -> Dict[str, str]:
        headers = {}

        if accept is not None:
            headers["accept"] = accept

        if content_type is not None:
            headers["content-type"] = content_type

        headers["date"] = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        headers["X-Requested-With"] = "XMLHTTPRequest"

        return headers

    def _log_response(
        self,
        response: requests.Response,
        message: Union[str, "Collection", "Model"],
    ) -> None:
        try:
            msg = (
                f"[{response.request.method}] {message} | "
                f"{response.status_code} {response.reason}"
            )
            if (
                response.status_code == requests.codes.ok
                or response.status_code >= requests.codes.server_error
            ):
                self.log(msg)
            elif response.status_code in (301, 302):
                redirected_url = response.headers["Location"]
                raise URLRedirectionException(response.status_code, redirected_url)
            else:
                self.log(
                    f"{msg} ({read_response_message(response, key='errors')})",
                    level=logging.ERROR,
                )
            self._logger.debug("DUMP:\n%s", dump.dump_all(response).decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError):
            self._logger.debug("DUMP:\nImpossible to decode.")
        except URLRedirectionException:  # pylint: disable=try-except-raise
            raise

    def log(self, msg: str, level: int = logging.INFO) -> None:
        self._logger.log(level, msg)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def _get(
        self,
        uri: str,
        query_parameters: Optional[Dict[str, Any]],
        with_base_path: bool = True,
    ) -> requests.Response:
        return self._session.get(
            f"{self._base_url(with_base_path)}{uri}",
            allow_redirects=False,
            auth=CytomineAuth(
                self._public_key,
                self._private_key,
                self._base_url(),
                self._base_path,
            ),
            headers=self._headers(),
            params=query_parameters,
        )

    def get(
        self,
        uri: str,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, Dict[str, str]]:
        response = self._get(uri, query_parameters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def get_model(
        self,
        model: "Model",
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, "Model"]:
        response = self._get(model.uri(), query_parameters)

        if response.status_code == requests.codes.ok:
            response_json = response.json()
            model = model.populate(response_json)
            self._log_response(response, model)

        if not response.status_code == requests.codes.ok:
            self._log_response(response, model.uri())
            return False

        return model

    def get_collection(
        self,
        collection: "Collection",
        query_parameters: Optional[Dict[str, Any]] = None,
        append_mode: bool = False,
    ) -> Union[bool, "Collection"]:
        response = self._get(collection.uri(), query_parameters)
        if response.status_code == requests.codes.ok:
            collection = collection.populate(response.json(), append_mode)

        self._log_response(response, collection)
        if not response.status_code == requests.codes.ok:
            return False

        return collection

    def _put(
        self,
        uri: str,
        data: Optional[Any] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        return self._session.put(
            f"{self._base_url()}{uri}",
            auth=CytomineAuth(
                self._public_key,
                self._private_key,
                self._base_url(),
                self._base_path,
            ),
            headers=self._headers(content_type="application/json"),
            params=query_parameters,
            data=data,
        )

    def put(
        self,
        uri: str,
        data: Optional[Any] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, Dict[str, str]]:
        response = self._put(uri, data=data, query_parameters=query_parameters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def put_model(
        self,
        model: "Model",
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, "Model"]:
        response = self._put(model.uri(), model.to_json(), query_parameters)
        if response.status_code == requests.codes.ok:
            if model.callback_identifier.lower() in response.json():
                model = model.populate(
                    response.json()[model.callback_identifier.lower()]
                )
            else:
                model = model.populate(
                    response.json()[model.__class__.__name__.lower()]
                )  # remove when REST URL are normalized

        self._log_response(response, model)
        if not response.status_code == requests.codes.ok:
            return False

        return model

    def _delete(
        self,
        uri: str,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        return self._session.delete(
            f"{self._base_url()}{uri}",
            auth=CytomineAuth(
                self._public_key,
                self._private_key,
                self._base_url(),
                self._base_path,
            ),
            headers=self._headers(content_type="application/json"),
            params=query_parameters,
        )

    def delete(
        self,
        uri: str,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        response = self._delete(uri, query_parameters)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            return True

        return False

    def delete_model(
        self,
        model: "Model",
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        response = self._delete(model.uri(), query_parameters)
        self._log_response(response, model)
        if response.status_code == requests.codes.ok:
            return True

        return False

    def _post(
        self,
        uri: str,
        data: Optional[Any] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
        with_base_path: bool = True,
    ) -> requests.Response:
        return self._session.post(
            f"{self._base_url(with_base_path)}{uri}",
            auth=CytomineAuth(
                self._public_key,
                self._private_key,
                self._base_url(),
                self._base_path,
            ),
            headers=self._headers(content_type="application/json"),
            params=query_parameters,
            data=data,
        )

    def post(
        self,
        uri: str,
        data: Optional[Any] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, Dict[str, str]]:
        response = self._post(uri, data=data, query_parameters=query_parameters)
        self._log_response(response, uri)
        if not response.status_code == requests.codes.ok:
            return False

        return response.json()

    def post_model(
        self,
        model: "Model",
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> Union[bool, "Model"]:
        response = self._post(model.uri(), model.to_json(), query_parameters)

        if response.status_code == requests.codes.ok:
            try:
                if model.callback_identifier.lower() in response.json():
                    model = model.populate(
                        response.json()[model.callback_identifier.lower()]
                    )
                else:
                    model = model.populate(
                        response.json()[model.__class__.__name__.lower()]
                    )  # remove when REST URL are normalized
            except KeyError:
                self._logger.warning(response.json())

        self._log_response(response, model)

        if not response.status_code == requests.codes.ok:
            return False

        return model

    def post_collection(
        self,
        collection: "Collection",
        query_parameters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        response = self._post(
            collection.uri(without_filters=True),
            collection.to_json(),
            query_parameters,
        )
        self._log_response(response, read_response_message(response, key="message"))
        return response.status_code == requests.codes.ok

    def open_admin_session(self) -> bool:
        uri = "/session/admin/open.json"
        response = self._get(uri, None, with_base_path=False)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            self.set_current_user()  # refetch user to update *ByNow properties
            # self._current_user.poulate(response.json())
            # response not consistent with the properties returned by user/current.json
            return True

        return False

    def close_admin_session(self) -> bool:
        uri = "/session/admin/close.json"
        response = self._get(uri, None, with_base_path=False)
        self._log_response(response, uri)
        if response.status_code == requests.codes.ok:
            self.set_current_user()  # refetch user to update *ByNow properties
            return True

        return False

    def is_alive(self) -> bool:
        uri = "/server/ping"
        try:
            response = self._get(uri, None, with_base_path=False)
            self._log_response(response, uri)
            return response.status_code == requests.codes.ok
        except Exception:  # pylint: disable=broad-except
            return False

    def wait_to_accept_connection(
        self,
        timeout_in_seconds: int = 120,
        delay_between_retry_in_seconds: int = 1,
    ) -> bool:
        mustend = time.time() + timeout_in_seconds
        while time.time() < mustend:
            if self.is_alive():
                return True
            time.sleep(delay_between_retry_in_seconds)
        return False

    def upload_file(
        self,
        model: "Model",
        filename: str,
        query_parameters: Optional[Dict[str, Any]] = None,
        uri: Optional[str] = None,
    ) -> Union[bool, "Model"]:
        if not uri:
            uri = model.uri()

        with open(filename, "rb") as file:
            m = MultipartEncoder(fields={"files[]": (filename, file)})
            response = self._session.post(
                f"{self._base_url()}{uri}",
                auth=CytomineAuth(
                    self._public_key,
                    self._private_key,
                    self._base_url(),
                    self._base_path,
                ),
                headers=self._headers(content_type=m.content_type),
                params=query_parameters,
                data=m,
            )

        if not response.status_code == requests.codes.ok:
            self._logger.error("Error during file uploading to %s", uri)
            return False

        model = model.populate(response.json())
        self._logger.info("File uploaded successfully to %s", uri)

        return model

    def download_file(
        self,
        url: str,
        destination: str,
        override: bool = False,
        payload: Any = None,
    ) -> bool:
        if not url.startswith("http"):
            url = f"{self._base_url()}{url}"

        if override or not os.path.exists(destination):
            response = self._session.get(
                url,
                auth=CytomineAuth(
                    self._public_key,
                    self._private_key,
                    self._base_url(),
                    self._base_path,
                ),
                headers=self._headers(content_type="application/json"),
                params=payload,
                stream=True,
            )

            if not response.status_code == requests.codes.ok:
                self._log_response(response, url)
                return False

            with open(destination, "wb") as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

                parameters = (
                    str(dict(filter(lambda item: item[1] is not None, payload.items())))
                    if payload
                    else {}
                )
                self._logger.info(
                    "File downloaded successfully from %s with parameters %s",
                    url,
                    parameters,
                )
            return True

        return True

    def upload_image(
        self,
        filename: str,
        id_storage: int,
        id_project: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Union[bool, "UploadedFile"]:
        upload_host = self._base_url(with_base_path=False)

        query_parameters: Dict[str, Any] = {
            "idStorage": id_storage,  # backwards compatibility
            "storage": id_storage,
            "sync": sync,
        }

        if id_project:
            query_parameters["idProject"] = id_project  # backwards compatibility
            query_parameters["projects"] = id_project

        if properties:
            query_parameters["keys"] = ",".join(list(properties.keys()))
            query_parameters["values"] = ",".join(list(properties.values()))

        basename = os.path.basename(filename)
        with open(filename, "rb") as file:
            m = MultipartEncoder(fields={"files[]": (basename, file)})
            response = self._session.post(
                f"{upload_host}/upload",
                auth=CytomineAuth(self._public_key, self._private_key, upload_host, ""),
                headers=self._headers(content_type=m.content_type),
                params=query_parameters,
                data=m,
            )

        if response.status_code == requests.codes.ok:
            uf = self._process_upload_response(response.json()[0])
            self._logger.info("Image uploaded successfully")
            return uf

        self._logger.error("Error during image upload.")
        return False

    def _process_upload_response(self, response_data: Dict[str, Any]) -> "UploadedFile":
        from .models.image import (
            AbstractImage,
            ImageInstance,
            ImageInstanceCollection,
        )
        from .models.storage import UploadedFile

        self._logger.debug(
            "Entering _process_upload_response(response_data=%s)",
            response_data,
        )

        uf: UploadedFile = UploadedFile().populate(response_data["uploadedFile"])  # type: ignore

        uf.images = []  # type: ignore
        if "images" in response_data:
            for image in response_data["images"]:
                data: Dict[str, Any] = {}

                if "imageInstances" in image:
                    image_instances = ImageInstanceCollection()
                    for image_instance in image["imageInstances"]:
                        image_instances.append(ImageInstance().populate(image_instance))
                    data["imageInstances"] = image_instances

                if "image" in image:
                    data["abstractImage"] = AbstractImage().populate(image["image"])

                uf.images.append(data)  # type: ignore

        return uf

    def import_datasets(
        self,
        storage_id: int,
        dataset_names: Optional[str] = None,
        create_project: bool = False,
    ) -> Dict[str, str]:
        """Import datasets from a given path."""

        upload_host = self._base_url(with_base_path=False)

        response = self._session.post(
            f"{upload_host}/import",
            auth=CytomineAuth(
                self._public_key,
                self._private_key,
                upload_host,
                "",
            ),
            headers=self._headers(content_type="text/plain"),
            params={
                "storage_id": storage_id,
                "dataset_names": dataset_names,
                "create_project": create_project,
            },
        )

        if response.status_code != requests.codes.ok:
            self._logger.error("Error during datasets upload: %s", response.text)
            return {}

        self._logger.info("Datasets uploaded successfully")
        return response.json()
