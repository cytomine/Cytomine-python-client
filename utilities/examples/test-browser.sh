#!/bin/bash

#Example to browse a whole slide tile per tile
#Warning: it saves each tile locally to an existing directory
# $working_path/image-id_image-tile*** (see code)

# Replace XXX values by your settings
host="XXX"
public_key="XXX"
private_key="XXX"
id_image=XXX
working_path=/bigdata/tmp/cytomine/
zoom_level=2 #zoom level
window_size=1024 #size of the tile
filter="adaptive" #filter applied to the tile
min_area=100 #minimum area of geometries to keep
max_area=100000 #maximum area of geometries to keep
overlap=0 #overlap between successive tile


#Note: The script will go through a whole slide at given zoom_level, apply filtering at each tile,
# and eventually upload detected connected components to Cytomine server (if cytomine_publish is activated)
python browse_slide_with_tiling.py --cytomine_host $host --cytomine_public_key $public_key --cytomine_private_key $private_key --cytomine_base_path /api/ --cytomine_working_path $working_path -i $id_image -m "AUTO" --window_size $window_size --zoom $zoom_level --overlap $overlap --binary_filter $filter #--cytomine_publish #--min_area $min_area --max_area $max_area
