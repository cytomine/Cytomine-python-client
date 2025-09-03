"""Example to import datasets into Cytomine."""

import logging
import sys
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models import StorageCollection

logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    parser = ArgumentParser(description="Example to import datasets into Cytomine")

    parser.add_argument(
        "--host",
        default="demo.cytomine.be",
        help="The Cytomine host",
    )
    parser.add_argument(
        "--public_key",
        help="The Cytomine public key",
    )
    parser.add_argument(
        "--private_key",
        help="The Cytomine private key",
    )
    params, _ = parser.parse_known_args(sys.argv[1:])

    with Cytomine(
        host=params.host,
        public_key=params.public_key,
        private_key=params.private_key,
    ) as cytomine:
        # To import the datasets, we need to know the ID of your Cytomine storage.
        storages = StorageCollection().fetch()
        storage = next(
            filter(lambda storage: storage.user == cytomine.current_user.id, storages)
        )
        if not storage:
            raise ValueError("Storage not found")

        response = cytomine.import_datasets(storage.id)

        print(response)
