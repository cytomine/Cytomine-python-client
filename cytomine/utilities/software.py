import os
from pathlib import Path

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


def setup_classify(args, logger, root_path=None, image_folder="images", set_folder=None, dest_pattern=None,
                   keep_without_term=False, **annot_params):
    """Download annotations for classification
    Parameters
    ----------
    args: Namespace
        Command-line parameters. Used parameters are:
            * args.cytomine_id_projects
            * args.cytomine_id_terms
            * args.cytomine_id_images
            * args.cytomine_id_users
            * args.cytomine_id_project
            * args.cytomine_reviewed
            * args.n_jobs
            * (optional, default: 1) args.cytomine_zoom_level
            * (optional, default: False) args.cytomine_download_alpha
    logger: CytomineJobLogger
        For logging
    root_path: str
        Root path for data
    image_folder: str
        Name of the image folder in the root
    set_folder: str|None
        Name of the set folder (e.g. 'train') to be included in the image folder.
    dest_pattern: str|None
        Destination pattern for annotation crops. By default (if dest_pattern is None):
            - if "showTerm" is in 'annot_params': "{term}/{image}_{id}.png"
            - otherwise: "{image}_{id}.png"
    keep_without_term: bool
        True for keeping annotations without terms (ignored if showTerm is missing in annot_params)
    annot_params: dict
        Additional parameters for fetching the annotations (e.g. showTerm, showWKT,...)

    Returns
    -------
    base_path: str
        The base_path where the dataset was downloaded.
    downloaded: AnnotationCollection
        The collection of downloaded annotations
    """
    if root_path is None:
        root_path = Path.home()
    if dest_pattern is None:
        if "showTerm" in annot_params:
            dest_pattern = os.path.join("{term}", "{image}_{id}.png")
        else:
            dest_pattern = os.path.join("{image}_{id}.png")

    # setup folder structure for annotations
    logger.abs_update(progress=0, statusComment="Set up directories for download.")
    base_path = os.path.join(root_path, image_folder)

    # check default values
    zoom_level = 1
    download_alpha = False
    if hasattr(args, "cytomine_zoom_level"):
        zoom_level = args.cytomine_zoom_level
        base_path = os.path.join(base_path, "zoom_level", str(zoom_level))
    if hasattr(args, "cytomine_download_alpha"):
        # to download the alphamask as a fourth channel
        download_alpha = args.cytomine_download_alpha
        base_path = os.path.join(base_path, "alpha", str(int(download_alpha)))
    if set_folder is not None:
        base_path = os.path.join(base_path, set_folder)

    if base_path:
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
        reviewed=args.cytomine_reviewed,
        **annot_params
    )

    if 'showTerm' in annot_params and not keep_without_term:
        annotations = annotations.filter(lambda a: hasattr(a.term, '__len__') and len(a.term) > 0)

    # download annotations
    logger.abs_update(progress=65, statusComment="Download crops of annotations.")
    downloaded = annotations.dump_crops(
        dest_pattern=os.path.join(base_path, dest_pattern),
        override=True,
        alpha=download_alpha,
        mask=download_alpha,
        zoom=zoom_level,
        n_workers=args.n_jobs
    )

    logger.abs_update(progress=100, statusComment="Downloaded crops for {} annotation(s).".format(len(downloaded)))

    return base_path, downloaded
