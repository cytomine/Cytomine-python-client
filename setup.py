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

from setuptools import setup
from io import open

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name='Cytomine-Python-Client',
    version='2.1.1',
    description='Python client to interact with Cytomine.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['cytomine', 'cytomine.models', 'cytomine.utilities'],
    url='http://www.cytomine.org',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent'
    ],
    install_requires=['requests-toolbelt',
                      'CacheControl',
                      'numpy',
                      'Shapely',
                      'six',
                      'future',
                      'opencv-python-headless',
                      'Pillow',
                      'requests'],
    setup_requires=['pytest-runner'],
    extra_requires={
        "test": ['pytest']
    },
    test_suite='cytomine.tests',
    license='LICENSE',
)
