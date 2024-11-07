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
# -----------------------------------------------------------------------------------------------------------
# *
# * This script is just an example to show how to calibrate an image inside Cytomine  
# * using the Cytomine Python client (https://github.com/cytomine/Cytomine-python-client).
# *
# * This script updates the resolution and/or magnification of an abstract image (image at storage level)
# * based on the id of one of it's instance in a project.
# * Note that all future instances of the image will be affected.
# * Every instance of this image can still have custom calibration and/or mangification values if set from the UI.
# * 
# -----------------------------------------------------------------------------------------------------------
# *
# * Exemple of command :
# * python calibrate_image.py --host "YOUR-CYTOMINE-URL" --public_key "YOUR-USER-PUBLIC-KEY" --private_key "YOUR-USER-PRIVATE-KEY" --id_image "YOUR-IMAGE-ID-IN-A-PROJECT" --resolution "NEW-RESOLUTION" --magnification "NEW-MAGNIFICATION"
# * with all values set to your use case.
# * Exemple :
# * python calibrate_image.py --host "http://demo.cytomine.local" --public_key "091d732d-89ae-43d7-bdfb-cc455d38680f" --private_key "54efff2a-01e2-4f7f-b833-cbe609686ddf" --id_image "10372" --resolution "0.499" --magnification "20"
# * will set a resolution of 0.499µm/px and magnification to 20x to the abstract image related to image instance of id 10372.
# *
# * The ouput of this command applied to https://cytomine.coop/collection/cmu-1/cmu-1-tiff uploaded in a local Cytomine gives :
# * [2020-07-15 01:17:08,318][INFO] [GET] [currentuser] CURRENT USER - 61 : admin | 200 OK
# * [2020-07-15 01:17:08,335][INFO] [GET] [imageinstance] 10372 : /1594767914587/CMU-1.tiff | 200 OK
# * [2020-07-15 01:17:08,357][INFO] [GET] [abstractimage] 10335 : /1594767914587/CMU-1.tiff | 200 OK
# * [2020-07-15 01:17:08,584][INFO] [PUT] [abstractimage] 10335 : /1594767914587/CMU-1.tiff | 200 OK
# *
# -----------------------------------------------------------------------------------------------------------
# *
# * HOWTO get your user public and private keys : https://doc.cytomine.org/Get%20Started%20V2?structure=UsersV2#Check_your_account_page
# * HOWTO get your image instance id : look at the URL of your image when exploring it in the web ui and take the value after /image/ :
# *         if URL = http://demo.cytomine.local/#/project/10359/image/10372 then your image instance id = 10372
# * 
# -----------------------------------------------------------------------------------------------------------
__version__ = "1.0.0"
# -----------------------------------------------------------------------------------------------------------
# Import of all python necessary modules, including the Cytomine Python client
import logging
from argparse import ArgumentParser

from cytomine import Cytomine
from cytomine.models import AbstractImage, ImageInstance

# -----------------------------------------------------------------------------------------------------------
# Parsing all the arguments from the command line
if __name__ == '__main__':
    parser = ArgumentParser(prog="Set calibration of an image (note that all instances of the image will be affected)")
    parser.add_argument('--host', default='localhost-core', help="The Cytomine host")
    parser.add_argument('--public_key', help="The Cytomine public key")
    parser.add_argument('--private_key', help="The Cytomine private key")
    parser.add_argument('--id_image', help="The identifier of the image instance to calibrate")
    parser.add_argument('--resolution', required=False, help="The resolution to set, in µm/px (optional)")
    parser.add_argument('--magnification', required=False, help="The magnification to set (optional)")
    params, _ = parser.parse_known_args()
# -----------------------------------------------------------------------------------------------------------
# Set resolution and/or magnification if setted
    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key, verbose=logging.INFO) as cytomine:
        image_instance = ImageInstance().fetch(params.id_image) # Fetch the image instance
        abstract_image = AbstractImage().fetch(image_instance.baseImage) # Retrieve the abstract image
        modification = False
        if params.resolution is not None:
            abstract_image.resolution = params.resolution
            modification = True
        if params.magnification is not None:
            abstract_image.magnification = params.magnification
            modification = True
        if not modification:
            logging.error("You should set either resolution or magnification")
        else:
            abstract_image.update()
# -----------------------------------------------------------------------------------------------------------