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

import logging
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models.ontology import (
    Ontology,
    RelationTerm,
    Term,
    TermCollection,
)

logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = ArgumentParser(prog="Cytomine Python client example")

    # Cytomine
    parser.add_argument('--cytomine_host', dest='host',
                        default='demo.cytomine.be', help="The Cytomine host")
    parser.add_argument('--cytomine_public_key', dest='public_key',
                        help="The Cytomine public key")
    parser.add_argument('--cytomine_private_key', dest='private_key',
                        help="The Cytomine private key")

    params, other = parser.parse_known_args(sys.argv[1:])

    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key) as cytomine:
        """
        We will create a new ontology with the following structure:
        _MY_ONTOLOGY_NAME_
        == TERM1
        == CATEGORY1
        ==== TERM2
        ==== TERM3
        """

        # First we create the required resources
        ontology = Ontology("_MY_ONTOLOGY_NAME_").save()
        term1 = Term("TERM1", ontology.id, "#00FF00").save()
        cat1 = Term("CATEGORY1", ontology.id, "#000000").save()
        term2 = Term("TERM2", ontology.id, "#FF0000").save()
        term3 = Term("TERM3", ontology.id, "#0000FF").save()

        # Then, we add relations between terms
        RelationTerm(cat1.id, term2.id).save()
        RelationTerm(cat1.id, term3.id).save()

        # Get all the terms of our ontology
        terms = TermCollection().fetch_with_filter("ontology", ontology.id)
        print(terms)
