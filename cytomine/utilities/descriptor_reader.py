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

import json


from cytomine.models import Software, SoftwareParameter, SoftwareCollection, SoftwareParameterCollection

__author__ = "Rubens Ulysse <urubens@uliege.be>"


def _format_type(type):
    if type.lower() == "listdomain":
        return "ListDomain"
    else:
        return type.lower().capitalize()


def read_descriptor(filename, schema_version="cytomine-0.1", delete_missing=False):
    """
    Read a software descriptor and add a not executable version of it to Cytomine.
    It should be used only for software development or testing purpose.
    A Cytomine software object will be created so that it is possible to interact with Cytomine.
    The software can be launched from the command line by the developer, faking a real execution from Cytomine WebUI.
    If the software already exists, it is updated.

    DO NOT USE this to provide a production-ready software, it won't work.
    In particular, image pulling is by-passed, software and parameter descriptions are not taken into account,
    nor parameter constraints.

    Parameters
    ----------
    filename:   String
        The descriptor file path.
    schema_version: String
        The version of descriptor schema.
    delete_missing: Bool
        If set to True, deletes the registered parameters missing from the descriptor file.

    Returns
    -------
    software:   Software
        The newly added not-executable Cytomine software
    """
    with open(filename, "r") as f:
        descriptor = json.load(f)
        print(descriptor)

        if "name" not in descriptor.keys():
            raise ValueError("No software name !")

        existing_softwares = SoftwareCollection().fetch()
        existing_software = [s for s in existing_softwares if s.name == descriptor["name"] and not s.softwareVersion]
        if len(existing_software) == 0:
            software = Software(name=descriptor["name"]).save()
        else:
            software = existing_software[0]

        existing_software_parameters = SoftwareParameterCollection().fetch_with_filter("software", software.id)
        processed_parameters = set()

        for parameter_descriptor in descriptor["inputs"]:
            if "id" not in parameter_descriptor.keys():
                raise ValueError("No id for parameter: {}".format(parameter_descriptor))

            if "type" not in parameter_descriptor.keys():
                raise ValueError("No type for parameter: {}".format(parameter_descriptor))

            if "name" not in parameter_descriptor.keys():
                parameter_descriptor["name"] = "@id"

            if "value-key" not in parameter_descriptor.keys():
                parameter_descriptor["value-key"] = "[@ID]"

            if "command-line-flag" not in parameter_descriptor.keys():
                parameter_descriptor["command-line-flag"] = "--@id"

            param = {k: v.replace("@ID", parameter_descriptor["id"].upper())
                         .replace("@id", parameter_descriptor["id"].lower()) if isinstance(v, str) else v
                     for k, v in parameter_descriptor.items()}

            sp = SoftwareParameter(
                name=param["id"],
                type=_format_type(param["type"]),
                id_software=software.id,
                default_value=(param["default-value"] if "default-value" in param.keys() else ""),
                required=(not param["optional"] if "optional" in param.keys() else False),
                set_by_server=(param["set-by-server"] if "set-by-server" in param.keys() else False),
                uri=(param["uri"] if "uri" in param.keys() else None),
                uri_sort_attribut=(param["uri-print-attribute"] if "uri-print-attribute" in param.keys() else None),
                uri_print_attribut=(param["uri-print-attribute"] if "uri-print-attribute" in param.keys() else None),
                server_parameter=(param["server-parameter"] if "server-parameter" in param.keys() else False),
                human_name=param["name"],
                value_key=param["value-key"],
                command_line_flag=param["command-line-flag"]
            )

            existing_software_parameter = [p for p in existing_software_parameters if p.name == param["id"]]
            if len(existing_software) == 0 or len(existing_software_parameter) == 0:
                sp.save()
            else:
                sp.update(existing_software_parameter[0].id)

            processed_parameters.add(param["id"])

        if delete_missing:
            for parameter in existing_software_parameters:
                if parameter.name not in processed_parameters:
                    parameter.delete()

        return software


if __name__ == '__main__':
    from cytomine import Cytomine
    Cytomine.connect("localhost-core", "JKL", "GHI")
    read_descriptor("descriptor.json")
