# -*- coding: utf-8 -*-


#
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


__author__ = "Begon Jean-Michel <jm.begon@gmail.com>"
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"
__version__ = '0.1'


# TODO : add support for threading backend and choice of temp folder


__all__ = ["TaskSplitter", "TaskExecutor", "SerialExecutor",
           "ParallelExecutor"]


from abc import ABCMeta, abstractmethod
import copy_reg
import types


from sklearn.externals.joblib import Parallel, delayed, cpu_count


def piclking_reduction(m):
    """Adds the capacity to pickle method of objects"""
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, piclking_reduction)


class TaskSplitter:
    """
    ===========
    TaskSplitter
    ===========
    A toolkit for preprocessing parallel computation
    """

    def compute_partition(self, nb_tasks, data_size):
        """
        Compute data partitioning for parallel computation :
        min(nb_tasks, data_size)

        Parameters
        ----------
        nb_tasks : int (!=0)
            If >0 : the parallelization factor.
            If <0 : nb_tasks = #cpu+nb_tasks+1 (-1 -> nb_tasks = #cpu)
        data_size : int > 0
            The size of the data to process

        Return
        ------
        triplet = (nb_tasks, counts, starts)
        nb_tasks : int
            The final parallelization factor. It is computed as
            min(#cpu/nb_tasks, data_size)
        starts : list of int
            The start indexes of the data for each parallel task
        """
        # Compute the actual number of core to use
        if nb_tasks < 0:
            cpu = cpu_count()+nb_tasks+1
            if cpu <= 0:
                cpu = 1
            nb_tasks = min(cpu, data_size)
        else:
            if nb_tasks == 0:
                nb_tasks = 1
            nb_tasks = min(nb_tasks, data_size)

        # Compute the minimum load
        increment = data_size//nb_tasks
        starts = [x*y for x, y in zip([increment]*nb_tasks, range(nb_tasks))]
        starts.append(data_size)

        # Distribute the extra load if necessary
        gap = data_size - increment*nb_tasks
        if gap > 0:
            # If there are leftovers, we will increase the number of objects
            # of the first cores : starts[i] = starts[i] + corrections[i]
            # The correction vector is [0]  [1,2,...,gap] [gap,...,gap] [0]
            # The first 0 is so as to start at the first element
            # The second part is to increase the number of datum of the first
            # cores by one.
            # Then we have to shifs all the remaining component to keep the
            # same number of elements...
            # Except for the last one which must correspond to the lenght of
            # the data vector
            corrections = range(gap+1) + ([gap]*(nb_tasks-gap-1)) + [0]

            starts = [x+y for x, y in zip(starts, corrections)]

        return nb_tasks, starts

    def partition(self, nb_tasks, data):
        """
        Partition the data for parallel computation.

        Parameters
        ----------
        nb_tasks : int {-1, >0}
            The parallelization factor. If -1 : the greatest factor is chosen
        data : list
            The data to partition

        Return
        ------
        tuple = (nb_tasks, data_parts, starts)
        nb_tasks : int
            The final parallelization factor. It is computed as
            min(#cpu/nb_tasks, data_size)
        data_parts : list of slices
            each element of data_parts is a contiguous slice of data : the
            partition for a parallel computation unit
        starts : list of int
            The start indices corresponding to the data_parts :
            data_parts[i] = data[starts[i]:starts[i+1]
        """
        nb_tasks, starts = self.compute_partition(nb_tasks, len(data))
        data_parts = []
        for i in xrange(nb_tasks):
            data_parts.append(data[starts[i]:starts[i + 1]])
        return nb_tasks, data_parts, starts


class TaskExecutor:
    """
    ===========
    TaskExecutor
    ===========
    A class responsible for carrying out submitted tasks
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, function, data, *args, **kwargs):
        """
        Get the result of the task directly

        Parameters
        ----------
        function : callable
            The function to process the task. The function must be able to
            work on any subset of the data
        data : an iterable of piece of data
            The data to process
        args : iterable
            Parameters to pass to the function
        kwargs: dictionnary
            Keyword parameters to pass to the function

        Return
        ------
        ls : iterable of results
            each individual result is the execution of the function on a given
            subset of the data. The caller must aggregate the result accordinly
        """
        pass

    @abstractmethod
    def execute_with_index(self, function, data, *args, **kwargs):
        """
        Get the result of the task directly. The difference with meth:`execute`
        comes from the function signature, which now must have a dedicated
        keyword argument "start_index" which indicates the start index of the
        data slice on which the function is called.

        Useful for preallocated shared memory

        Parameters
        ----------
        function : callable : f(...start_index,...)
            The function to process the task. The function must be able to
            work on any subset of the data and must have a dedicated keyword
            argument "start_index" which indicates the start index of the data
            slice on which the function is called
        data : an iterable of piece of data
            The data to process
        args : iterable
            Parameters to pass to the function
        kwargs: dictionnary
            Keyword parameters to pass to the function

        Return
        ------
        ls : iterable of results
            each individual result is the execution of the function on a given
            subset of the data. The caller must aggregate the result accordinly
        """
        pass

    def __call__(self, function, data, *args, **kwargs):
        """Delegate to :meth:`execute`"""
        return self.execute(function, data, *args, **kwargs)


class SerialExecutor(TaskExecutor):
    """
    ==============
    SerialExecutor
    ==============
    :class:`SerialExecutor` simply store the task to execute later

    Note : the :class:`SerialExecutor` is provided for debugging purpose so
    that a parallel code can be executed serially with minor modifications.

    Example
    -------
    >>> executor = SerialExecutor()
    >>> data = range(100)
    >>> executor.execute(sum, data)
    [4950]
    >>>sum([4950])
    4950
    """

    def execute(self, function, data, *args, **kwargs):
        if len(args) == 0:
            if len(kwargs) == 0:
                ls = [function(data)]
            else:
                ls = [function(data, **kwargs)]
        elif len(kwargs) == 0:
            ls = [function(data, *args)]
        else:
            ls = [function(data, *args, **kwargs)]
        return ls

    def execute_with_index(self, function, data, *args, **kwargs):
        if len(args) == 0:
            if len(kwargs) == 0:
                ls = [function(data, start_index=0)]
            else:
                ls = [function(data, start_index=0, **kwargs)]
        elif len(kwargs) == 0:
            ls = [function(data, start_index=0, *args)]
        else:
            ls = [function(data, start_index=0, *args, **kwargs)]
        return ls


class ParallelExecutor(TaskExecutor):
    """
    ================
    ParallelExecutor
    ================
    :class:`ParallelExecutor` splits the data for multiprocessing

    Example
    -------
    >>> executor = ParallelExecutor(4) #If 4 cores are available
    >>> data = range(100)
    >>> executor.execute(sum, data)
    [300, 925, 1550, 2175]
    >>> sum([300, 925, 1550, 2175])
    4950
    """

    def __init__(self, nb_cores=-1, verbose=1):
        """
        Creates an instance of :class:`ParallelExecutor`

        Parameters
        ----------
        nb_cores : int (!=0) (Default : -1)
            The number of core to use.
                If >0 : the parallelization factor.
                If <0 : nb_tasks = #cpu+nb_cores+1
                Set to -1 to use the maximum number of core
        verbose : int [0, 50]
            The verbosity level. The more, the more verbose
        """
        self._nb_cores = nb_cores
        self._verbosity = verbose

    def execute(self, function, data, *args, **kwargs):
        #Splitting task
        tasksplitter = TaskSplitter()
        nb_jobs, splitted_data, starts = tasksplitter.partition(self._nb_cores,
                                                                data)

        #Parallelization
        parallelizer = Parallel(n_jobs=nb_jobs, verbose=self._verbosity)

        if len(args) == 0:
            if len(kwargs) == 0:
                all_data = parallelizer(delayed(function)(
                    splitted_data[i]) for i in xrange(nb_jobs))
            else:
                all_data = parallelizer(delayed(function)(
                    splitted_data[i], **kwargs) for i in xrange(nb_jobs))
        elif len(kwargs) == 0:
            all_data = parallelizer(delayed(function)(
                splitted_data[i], *args) for i in xrange(nb_jobs))
        else:
            all_data = parallelizer(delayed(function)(
                splitted_data[i], *args, **kwargs) for i in xrange(nb_jobs))

        return all_data

    def execute_with_index(self, desc, function, data, *args, **kwargs):
        #Splitting task
        tasksplitter = TaskSplitter()
        nb_jobs, splitted_data, starts = tasksplitter.partition(self._nb_cores,
                                                                data)

        #Parallelization
        parallelizer = Parallel(n_jobs=nb_jobs, verbose=self._verbosity)

        if len(args) == 0:
            if len(kwargs) == 0:
                all_data = parallelizer(delayed(function)(
                    splitted_data[i], start_index=starts[i])
                    for i in xrange(nb_jobs))
            else:
                all_data = parallelizer(delayed(function)(
                    splitted_data[i], start_index=starts[i], **kwargs)
                    for i in xrange(nb_jobs))

        elif len(kwargs) == 0:
            all_data = parallelizer(delayed(function)(
                splitted_data[i], start_index=starts[i], *args)
                for i in xrange(nb_jobs))

        else:
            all_data = parallelizer(delayed(function)(
                splitted_data[i], start_index=starts[i], *args, **kwargs)
                for i in xrange(nb_jobs))

        return all_data

if __name__ == "__main__":
    data = range(100)
    executor = SerialExecutor()
    print executor.execute(sum, data)
    executor = ParallelExecutor()
    print executor.execute(sum, data)
