import os
from pathlib import Path

from cytomine import Cytomine
from cytomine.models._utilities import makedirs
from cytomine.utilities.annotations import get_annotations

TASK_CLASSIFY = "classify"
TASK_COUNTING = "counting"
TASK_SEGMENT = "segment"
TASK_LANDMARK = "landmark"


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def stringify(l):
    return ",".join(map(str, l))


def parse_domain_list(s):
    if s is None or len(s) == 0:
        return []
    return list(map(int, s.split(',')))


def setup_classify(args, logger, root_path=None, image_folder="images", set_folder=None, **annot_params):
    """Download annotations for classification
    Parameters
    ----------
    args: Namespace
        Command-line parameters
    logger: CytomineJobLogger
        For logging
    root_path: str
        Root path for data
    image_folder: str
        Name of the image folder in the root
    set_folder: str|None
        Name of the set folder (e.g. 'train') to be included in the image folder.
    :return:
    """
    if root_path is None:
        root_path = Path.home()

    # setup folder structure for annotations
    logger.abs_update(progress=0, statusComment="Set up directories for download.")
    base_path = os.path.join(root_path, image_folder)

    if hasattr(args, "cytomine_zoom_level"):
        base_path = os.path.join(base_path, "zoom_level", str(args.cytomine_zoom_level))
    if hasattr(args, "cytomine_download_alpha"):
        base_path = os.path.join(base_path, "alpha", str(int(args.cytomine_download_alpha)))
    if set_folder is not None:
        base_path = os.path.join(base_path, set_folder)

    makedirs(base_path)

    # fetch annotations
    filter_projects = parse_domain_list(args.cytomine_id_projects)
    filter_terms = parse_domain_list(args.cytomine_id_terms)
    filter_images = parse_domain_list(args.cytomine_id_images)
    filter_users = parse_domain_list(args.cytomine_id_users)

    if filter_projects is None or len(filter_projects) == 0:  # if projects is missing, fetch only from current project
        filter_projects = [args.cytomine_id_project]

    logger.abs_update(progress=30, statusComment="Download annotations.")
    annotations = get_annotations(
        projects=filter_projects,
        terms=filter_terms,
        images=filter_images,
        users=filter_users,
        **annot_params
    )

    # download annotations
    logger.abs_update(progress=65, statusComment="Download crops of annotations.")
    downloaded = annotations.dump_crops(
        dest_pattern=os.path.join(base_path, "{term}", "{image}_{id}.png"),
        override=True, **{
            "alpha": args.cytomine_download_alpha,
            "zoom": args.cytomine_zoom_level
        },
        n_workers=args.n_jobs
    )

    return base_path, downloaded
