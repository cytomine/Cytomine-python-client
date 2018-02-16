#!/bin/bash

# ---------------------------------------------------------------------------------------------------------
# * Copyright (c) 2009-2015. Authors: see NOTICE file.
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
# */


#__author__          = "Marée Raphael <raphael.maree@ulg.ac.be>"
#__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"


#Example to browse a whole slide tile per tile
#Warning: it saves each tile locally to an existing directory
# $working_path/image-id_image-tile*** (see code)

# Replace XXX values by your settings
host="XXX"
public_key="XXX"
private_key="XXX"
working_path=/bigdata/tmp/cytomine/
cytomine_id_image=XXX
cytomine_zoom_level=2 #zoom level
cytomine_tile_size=512 #size of the tile
cytomine_tile_overlap=0 #overlap between successive tiles


#Note: The script will go through a whole slide at given zoom_level and saves locally the tile image
python browse_slide_with_tiling.py --cytomine_host $host --cytomine_public_key $public_key --cytomine_private_key $private_key --cytomine_base_path /api/ --cytomine_working_path $working_path --cytomine_id_image $cytomine_id_image --cytomine_tile_size $cytomine_tile_size --cytomine_zoom_level $cytomine_zoom_level --cytomine_tile_overlap $cytomine_tile_overlap
