# Copyright (c) 2009-2018. Authors: see NOTICE file.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION

RUN apt-get update -y && \
    apt-get install --no-install-recommends --no-install-suggests -y curl libglib2.0-0 unzip && \
    rm -rf /var/lib/apt/lists/*

ARG VERSION
ARG NAMESPACE=Cytomine-ULiege
ARG RELEASE_PATH=https://github.com/${NAMESPACE}/Cytomine-python-client/releases/download/v${VERSION}
ADD ${RELEASE_PATH}/Cytomine-Python-Client-${VERSION}.zip /tmp/cytomine-client.zip
RUN unzip -n /tmp/cytomine-client.zip && \
    pip install --upgrade pip && \
    pip install -r /tmp/cytomine-client/requirements.txt && \
    pip install /tmp/cytomine-client.zip && \
    rm -rf /tmp/*
