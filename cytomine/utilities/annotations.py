from cytomine.models import AnnotationCollection


REVIEWED_INCLUDE = 1
REVIEWED_ONLY = 2
REVIEWED_EXCLUDE = 0


def get_annotations(projects, images=None, terms=None,
                    users=None, reviewed=REVIEWED_EXCLUDE,
                    **collection_params):
    """Returns a list annotations filtered with the following criterion.

    Parameters
    ----------
    projects: list
        List of projects where the annotation should be downloaded from
    images: iterable|None
        Identifiers of images in which annotation should be taken.
    terms: iterable|None
        Identifiers of terms. If present, only annotations that have at least one of the listed terms will be taken.
        Otherwise, no filtering based on terms is applied.
    users: iterable|None
        Identifiers of users. If present, only annotations that were created one of the the given users will be taken.
        Otherwise, no filtering based on users is applied.
    reviewed: int
        One of the following values:
           * REVIEWED_EXCLUDE: only get non-reviewed annotations
           * REVIEWED_INCLUDE: get both non-reviwed and reviewed annotations
           * REVIEWED_ONLY: only get reviwed annotations
    collection_params: dict
        Additional Annotation parametes such as showTerm, showWKT,...

    Returns
    -------
    collection: AnnotationCollection
        The annotations resulting from the filtering
    """
    if projects is None or len(projects) == 0:
        raise ValueError("You should select at least one project to select annotation(s) from.")
    if reviewed not in {REVIEWED_EXCLUDE, REVIEWED_ONLY, REVIEWED_INCLUDE}:
        raise ValueError("Unknown value '{}' for reviewed annotation selection. ".format(reviewed) +
                         "Expects one of : EXCLUDE ({}) or INCLUDE ({}) or ONLY ({}).".format(
                            REVIEWED_EXCLUDE, REVIEWED_INCLUDE, REVIEWED_ONLY
                         ))

    annotations = AnnotationCollection()
    for id_project in projects:
        if reviewed != REVIEWED_ONLY:
            annotations += AnnotationCollection(
                project=id_project, images=images, term=terms,
                users=users, reviewed=False, **collection_params
            ).fetch()

        if reviewed != REVIEWED_EXCLUDE:
            annotations += AnnotationCollection(
                project=id_project, images=images, term=terms,
                users=users, reviewed=True, **collection_params
            ).fetch()

    return annotations
