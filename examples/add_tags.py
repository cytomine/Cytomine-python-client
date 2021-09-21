# -*- coding: utf-8 -*-
#
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
# -----------------------------------------------------------------------------------------------------------
# *
# * This script is just an example to show how to add a tag to Cytomine, 
# * and to associate it to a project, an image inside a project (ImageInstance) or an annotation
# * Compliant with Cytomine v3.0.0 or later and using the 
# * Cytomine Python client (https://github.com/cytomine/Cytomine-python-client) v2.2.0 or later.
# *
# -----------------------------------------------------------------------------------------------------------
# *
# * Exemple of command :
# * python add_tags.py --host "YOUR-CYTOMINE-URL" --public_key "YOUR-USER-PUBLIC-KEY" --private_key "YOUR-USER-PRIVATE-KEY" --tag "NEW-TAG" 
# * with all values set to your use case: --id_project "YOUR-PROJECT-ID" and/or --id_image "YOUR-IMAGE-ID-IN-A-PROJECT" and/or --id_annotation "YOUR-ANNOTATION-ID"
# * Exemple :
# * python add_tags.py --host "http://demo.cytomine.local" --public_key "091d732d-89ae-43d7-bdfb-cc455d38680f" --private_key "54efff2a-01e2-4f7f-b833-cbe609686ddf" --tag "MyTag" --id_project "10966" --id_image "10978" --id_annotation "11431"
# * 
# * The ouput of this command applied to https://cytomine.coop/collection/cmu-1/cmu-1-tiff uploaded in a local Cytomine gives :
# [2020-09-10 17:10:41,137][INFO] [GET] [currentuser] CURRENT USER - 61 : admin | 200 OK
# [2020-09-10 17:10:41,209][INFO] [GET] [tag collection] 1 objects | 200 OK
# [2020-09-10 17:10:41,426][INFO] [POST] [tag] 15990 : MyTag | 200 OK
# [2020-09-10 17:10:41,454][INFO] [GET] [project] 10966 : Test tags | 200 OK
# [2020-09-10 17:10:41,589][INFO] [POST] [tag_domain_association] 15996 : None | 200 OK
# [tag_domain_association] 15996 : None
# [2020-09-10 17:10:41,615][INFO] [GET] [imageinstance] 10978 : /1594767914587/CMU-1.tiff | 200 OK
# [2020-09-10 17:10:41,662][INFO] [POST] [tag_domain_association] 16002 : None | 200 OK
# [tag_domain_association] 16002 : None
# [2020-09-10 17:10:41,727][INFO] [GET] [annotation] 11431 | 200 OK
# [2020-09-10 17:10:41,792][INFO] [POST] [tag_domain_association] 16008 : None | 200 OK
# [tag_domain_association] 16008 : None
# *
# -----------------------------------------------------------------------------------------------------------
# *
# * HOWTO get your user public and private keys : https://doc.cytomine.org/Get%20Started%20V2?structure=UsersV2#Check_your_account_page
# * HOWTO get your project id : look at the URL of your project when exploring it in the web ui and take the value after /project/ :
# *         if URL = http://demo.cytomine.local/#/project/10359 then your project id = 10359
# * HOWTO get your image instance id : look at the URL of your image when exploring it in the web ui and take the value after /image/ :
# *         if URL = http://demo.cytomine.local/#/project/10359/image/10372 then your image instance id = 10372
# * HOWTO get your annotation id : select your annotation using the web ui and click on "Copy URL". Then paste your URL in any document or browser and get the value after /annotation/:
# *         if URL = http://demo.cytomine.local/#/project/10359/image/10372/annotation/11431 then your annotation id = 11431
# * 
# -----------------------------------------------------------------------------------------------------------
# Import of all python necessary modules, including the Cytomine Python client
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import sys
from argparse import ArgumentParser
from cytomine import Cytomine
from cytomine.models import TagDomainAssociation, Tag, TagCollection, Project, Annotation, ImageInstance
# -----------------------------------------------------------------------------------------------------------
__author__ = "Grégoire Vincke <gregoire.vincke@cytomine.coop> and Renaud Hoyoux <renaud.hoyoux@cytomine.coop>"
__maintainer__ = "Renaud Hoyoux <renaud.hoyoux@cytomine.coop>"
__status__ = "Production"
__copyright__ = "Apache 2 license. Made by Cytomine SCRLFS, Belgium, https://cytomine.coop/"
__version__ = "1.0.0"
# -----------------------------------------------------------------------------------------------------------
# Parsing all the arguments from the command line
if __name__ == '__main__':
    parser = ArgumentParser(prog="Cytomine Python client example to add a tag to a project, an image, or an annotation")
    parser.add_argument('--host', default='localhost-core', help="The Cytomine host")
    parser.add_argument('--public_key', help="The Cytomine public key")
    parser.add_argument('--private_key', help="The Cytomine private key")
    parser.add_argument('--tag', help="The tag value")
    parser.add_argument('--id_project', required=False, help="The project to which the tag will be associated (optional)")
    parser.add_argument('--id_image_instance', required=False, help="The image to which the tag will be associated (optional)")
    parser.add_argument('--id_annotation', required=False, help="The annotation to which the tag will be associated (optional)")
    params, other = parser.parse_known_args(sys.argv[1:])
# -----------------------------------------------------------------------------------------------------------
    with Cytomine(host=params.host, public_key=params.public_key, private_key=params.private_key, verbose=logging.INFO) as cytomine:
        # Fetch all tags already existing in this Cytomine instance
        tags = TagCollection().fetch()
        inCollection=False
        # Add the tag to Cytomine only if it do not yet exist, and if exist, select it
        for t in tags:
            if t.name == params.tag :
                inCollection = True
                break    # break here as we only need to know that this proposed tag is already in the list, and as we need t to be this tag
                
        if inCollection == True:
            print("Tag already in collection")
            tag = t
        else:
            tag = Tag(params.tag).save()

        # Add the tag to the mentioned domain 
        if params.id_project:
            association = TagDomainAssociation(Project().fetch(params.id_project), tag.id).save()
            print(association)
        if params.id_image_instance:
            association = TagDomainAssociation(ImageInstance().fetch(params.id_image_instance), tag.id).save()
            print(association)
        if params.id_annotation:
            association = TagDomainAssociation(Annotation().fetch(params.id_annotation), tag.id).save()
            print(association)
# -----------------------------------------------------------------------------------------------------------
# Check for other example scripts using the Cytomine Python Client 
# on https://github.com/cytomine/Cytomine-python-client/tree/master/examples
# -----------------------------------------------------------------------------------------------------------