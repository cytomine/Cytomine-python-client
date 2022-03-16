import errno
import os

try:
    import queue as queue
except ImportError:
    import Queue as queue

from threading import Thread
from multiprocessing import cpu_count


def is_false(v):
    """Check if v is 'False'"""
    return isinstance(v, bool) and not v


def generic_parallel(data, worker_fn, n_workers=0):
    """Run a function on a batch of data in parallel using a given processing function.

    Parameters
    ----------
    data: iterable
        The data to be downloaded with `download_instance_fn`
    worker_fn: callable
        A functions that execute the operation on the given output. It has one parameter which must be the same type
        as the items of `data`. If needed it can return a value.
    n_workers: int
        Number of workers to use (default: uses all the available processors)

    Returns
    -------
    results: iterable
        List processed items as tuples. First element of the tuple is the item itself, the second element of the tuple
        is the value returned by `worker_fn` for this item.
    """
    def worker(_in, _out):
        while True:
            item = _in.get()
            if item is None:
                break
            _out.put((item, worker_fn(item)))

    if n_workers <= 0:
        n_workers = cpu_count()
    else:
        n_workers = n_workers

    # instantiate multiprocessing objects
    in_queue = queue.Queue()
    out_queue = queue.Queue()
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


def generic_chunk_parallel(data, worker_fn, chunk_size=1, n_workers=0):
    """Execute a worker function on all elements of a data list. Items are processed by batch of size 'chunk_size'.

    Parameters
    ---------
    data: iterable
        Data to be processed (data should be sliceable)
    worker_fn: callable
        A callable function that can process a batch of items from data (received as a list of items)
    chunk_size: int
        Size of the chunk
    n_workers: int
        Number of workers to use (default: uses all the available processors)

    Returns
    -------
    results: iterable
        List processed items as tuples. First element of the tuple is the slice (start,end) of the chunk (end excluded),
        the second element of the tuple is the value returned by `worker_fn` for this slice.
    """
    nb_chunks = (len(data) + chunk_size) // chunk_size
    chunk_limits = list()

    for i in range(nb_chunks):
        start = i * chunk_size
        end = start + chunk_size
        chunk_limits.append([start, end])

    def worker_wrapper(startend):
        _start, _end = startend
        return worker_fn(data[_start:_end])

    return generic_parallel(chunk_limits, worker_wrapper, n_workers=n_workers)


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
    return generic_parallel(data, download_instance_fn, n_workers=n_workers)


def makedirs(path, exist_ok=True):
    """Python 2.7 compatinle"""
    if path:
        try:
            os.makedirs(path)
        except OSError as e:
            if not (exist_ok and e.errno == errno.EEXIST):
                raise  # Reraise if failed for reasons other than existing already



