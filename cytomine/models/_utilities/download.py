import errno
import os
from queue import Queue
from threading import Thread
from multiprocessing import cpu_count


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


def makedirs(path, exist_ok=True):
    """Python 2.7 compatinle"""
    try:
        os.makedirs(path)
    except OSError as e:
        if not (exist_ok and e.errno == errno.EEXIST):
            raise  # Reraise if failed for reasons other than existing already



