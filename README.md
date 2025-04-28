# Cytomine Python client

> Cytomine-python-client is an open-source Cytomine client written in Python. This client is a Python wrapper around Cytomine REST API gateway.

[![GitHub release](https://img.shields.io/github/release/cytomine/Cytomine-python-client.svg)](https://github.com/cytomine/Cytomine-python-client/releases)
[![GitHub](https://img.shields.io/github/license/cytomine/Cytomine-python-client.svg)](https://github.com/cytomine/Cytomine-python-client/blob/master/LICENSE)

## Overview

All data available from the Cytomine graphical interface can be manipulated programmatically from your computer. This page introduces the key concepts on how to interact with Cytomine without this graphical interface. Cytomine is a RESTful application.
It means that the data stored and managed by Cytomine can be obtained through specific URLs. Contrary to the graphical interface, these URLs only provide relevant information data.
To ease interaction with Cytomine, the Cytomine API client for Python encapsulates all the technical details relative to the HTTP API so that you can manipulate Cytomine resources without complexity.

- See [https://doc.uliege.cytomine.org/](https://doc.uliege.cytomine.org/dev-guide/clients/python/usage) for more details.
- See [https://uliege.cytomine.org/](https://uliege.cytomine.org/) for more information about Cytomine.

## Requirements

- Python 3.5+

## Installation

`cytomine-python-client` is available on [PyPi](https://pypi.org/project/cytomine-python-client/) using pip:

```bash
pip install cytomine-python-client
```

For versions lower than `2.3.4`, refer to [manual installation guide](https://doc.uliege.cytomine.org/dev-guide/clients/python/installation).

## Usage

See [detailed usage documentation](https://doc.uliege.cytomine.org/dev-guide/clients/python/usage) for the complete documentation.

### Basic example

Three parameters are required to connect:
* `HOST`: The full URL of Cytomine core (e.g. “http://demo.cytomine.be”).
* `PUBLIC_KEY`: Your cytomine public key.
* `PRIVATE_KEY`: Your cytomine private key. 

First, the connection object has to be initialised.

```python
from cytomine import Cytomine

host = "demo.cytomine.be"
public_key = "XXX" # check your own keys from your account page in the web interface
private_key = "XXX"

cytomine = Cytomine.connect(host, public_key, private_key)
```

The next sample code should print “Hello {username}” where {username} is replaced by your Cytomine username and print the list of available projects.

```python
from cytomine.models import ProjectCollection

print(f"Hello {cytomine.current_user}")
projects = ProjectCollection().fetch()
print(projects)
for project in projects:
    print(project)
```

### Other examples

* [Scripts in examples directory](https://github.com/cytomine/Cytomine-python-client/tree/main/examples)
* [Documentation by examples](https://doc.uliege.cytomine.org/dev-guide/clients/python/examples)

## License

Apache-2.0
