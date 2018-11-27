import errno
import os
from queue import Queue
from shutil import copyfile
from threading import Thread
from multiprocessing import cpu_count

from cytomine.utilities.pattern_matching import resolve_pattern

from cytomine import Cytomine


class DumpError(Exception):
    pass


def makedirs(path, exist_ok=True):
    """Python 2.7 compatinle"""
    try:
        os.makedirs(path)
    except OSError as e:
        if not (exist_ok and e.errno == errno.EEXIST):
            raise  # Reraise if failed for reasons other than existing already


def is_false(v):
    """Check if v is 'False'"""
    return isinstance(v, bool) and not v


def generic_download(data, download_instance_fn, n_workers=0):
    """Download a set of data in parallel using a given download function.

    Parameters
    ----------
    data: iterable
        The data to be downloaded with `download_instance_fn`
    download_instance_fn: callable
        A functions that downloads what needs to be downloaded. It has one parameter which must be the same type as the
        items of `data`. If needed it can return a value.
    n_workers: int
        Number of workers to use (default: uses all the available processors)

    Returns
    -------
    results: iterable
        List processed items as tuples. First element of the tuple is the item itself, the second element of the tuple
        is the value returned by `download_instance_fn` for this item.
    """
    def worker(_in, _out):
        while True:
            item = _in.get()
            if item is None:
                break
            _out.put((item, download_instance_fn(item)))

    if n_workers <= 0:
        n_workers = cpu_count()
    else:
        n_workers = n_workers

    # instantiate multiprocessing objects
    in_queue = Queue()
    out_queue = Queue()
    threads = [Thread(target=worker, args=[in_queue, out_queue]) for _ in range(n_workers)]

    for t in threads:
        t.daemon = True
        t.start()

    for item in data:
        if item is None:
            continue
        in_queue.put(item)

    # feed `n_workers` None values in the queue to stop the workers
    for _ in range(n_workers):
        in_queue.put(None)

    # wait for the jobs to finish
    for t in threads:
        t.join()

    results = list()
    while not out_queue.empty():
        results.append(out_queue.get_nowait())

    return results


def generic_image_dump(dest_pattern, model, url_fn, override=True, **parameters):
    """A generic function for 'dumping' a model as an image (crop, windows,...).
    Parameters
    ----------
    dest_pattern: str
        The destination pattern for the image.
    model: Model
        A Cytomine model
    url_fn: callable
        A function for generating the url of the image. The function call would be like the following:
            url_fn(model, file_path, **parameters)
        where model is the cytomine model, file_path is the destination filepath and paramters are the dump
        parameters.
    override: bool
        True for overriding the file. False
    parameters: dict

    Returns
    -------
    downloaded: iterable
        The list of downloaded files

    Raises
    ------
    DumpError:
        When the download fails.
    """
    # generate download path(s)
    files_to_download = list()
    for file_path in resolve_pattern(dest_pattern, model):
        destination = os.path.dirname(file_path)
        filename, extension = os.path.splitext(os.path.basename(file_path))
        extension = extension[1:]

        if extension not in ("jpg", "png", "tif", "tiff"):
            extension = "jpg"

        makedirs(destination, exist_ok=True)

        files_to_download.append(os.path.join(destination, "{}.{}".format(filename, extension)))

    if len(files_to_download) == 0:
        raise ValueError("Couldn't generate a dump path.")

    # download once
    file_path = files_to_download[0]
    url = url_fn(model, file_path, **parameters)
    if not Cytomine.get_instance().download_file(url, file_path, override, parameters):
        raise DumpError("Could not dump the image.")

    # copy the file to the other paths (if any)
    for dest_file_path in files_to_download[1:]:
        if override or not os.path.isfile(dest_file_path):
            copyfile(file_path, dest_file_path)

    return files_to_download


def download_annotation_crops(annotations, n_workers=0, **dump_params):
    """Download the crops of the given annotations
    Parameters
    ----------
    annotations: AnnotationCollection
        The annotations of which the crops should be downloaded
    n_workers: int
        Number of workers to use (default: uses all the available processors)
    dump_params: dict
        Parameters for dumping the annotations

    Returns
    -------
    annotations: AnnotationCollection
        List of annotations (containing a `filenames` attribute)
    """
    def dump_crop(an):
        if is_false(an.dump(**dump_params)):
            return False
        else:
            return an

    results = generic_download(annotations, download_instance_fn=dump_crop, n_workers=n_workers)

    # check errors
    count_fail = 0
    failed = list()
    for in_annot, out_annot in results:
        if is_false(out_annot):
            count_fail += 1
            failed.append(in_annot.id)

    logger = Cytomine.get_instance().logger
    if count_fail > 0:
        n_annots = len(annotations)
        ratio = 100 * count_fail / float(n_annots)
        logger.info("Failed to download crops for {}/{} annotations ({:3.2f} %).".format(count_fail, n_annots, ratio))
        logger.debug("Annotation with crop download failure: {}".format(failed))

    from cytomine.models import AnnotationCollection  # to avoid circular import
    collection = AnnotationCollection()
    collection.extend([an for _, an in results if not isinstance(an, bool) or an])
    return collection
