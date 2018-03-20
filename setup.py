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

setup(
    name='Cytomine Python Client',
    version='1.1',
    description='Python client to interact with Cytomine.',
    packages=['cytomine', 'cytomine.models', 'cytomine.utilities'],
    url='http://www.cytomine.be',
    install_requires=['requests',
                      'requests-toolbelt',
                      'cachecontrol',
                      'numpy',
                      'shapely',
                      'six',
                      'future',
                      'opencv-python'],
    setup_requires=['pytest-runner'],
    extra_requires={
        "test": ['pytest']
    },
    test_suite='cytomine.tests',
    license='LICENSE',
)
