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


import sys
import os
import time
from abc import ABCMeta, abstractmethod

__all__ = ["Logger", "StandardLogger", "FileLogger", "VoidLogger",
           "ProgressLogger", "Progressable", "format_duration", "format_size"]


def format_duration(duration):
    """
    Format the duration expressed in seconds as string

    Parameters
    ----------
    duration : float
        a duration in seconds
    Return
    ------
    formated : str
        the given duration formated

    Example
    -------
    >>> days = 1
    >>> hours = 4
    >>> minutes = 52
    >>> seconds = 23
    >>> duration = seconds + 60*(minutes + 60*(hours + 24*days))
    >>> format_duration(duration)
    '1d 4h 52m 23s'
    """
    sec = duration % 60
    excess = int(duration) // 60  # minutes
    res = str(sec) + "s"
    if excess == 0:
        return res
    minutes = excess % 60
    excess = excess // 60  # hours
    res = str(minutes) + "m " + res
    if excess == 0:
        return res
    hour = excess % 24
    excess = excess // 24  # days
    res = str(hour) + "h " + res
    if excess == 0:
        return res
    res = str(excess)+"d " + res
    return res


def format_size(nb_bytes):
    """
    Format a size expressed in bytes as a string

    Parameters
    ----------
    nb_bytes : int
        the number of bytes

    Return
    ------
    formated : str
        the given number of bytes fromated

    Example
    -------
    >>> format_size(100)
    '100.0 bytes'
    >>> format_size(1000)
    '1.0 kB'
    >>> format_size(1000000)
    '1.0 MB'
    >>> format_size(1000000000)
    '1.0 GB'
    >>> format_size(1000000000000)
    '1.0 TB'
    >>> format_size(1000000000000000000)
    '1000000.0 TB'

    """
    for x in ['bytes', 'kB', 'MB', 'GB']:
        if nb_bytes < 1000.0:
            return "%3.1f %s" % (nb_bytes, x)
        nb_bytes /= 1000.0
    return "%3.1f %s" % (nb_bytes, 'TB')


class Logger:
    """
    ======
    Logger
    ======
    A abstract base class for the logging facility. The logger actually logs
    the messages if:
        1. the message's minimum verbosity is equal or greater to the logger's
            verbosity
        2. or it contains a tag which is followed by the logger

    Class constants
    ---------------
    MAX_VERBOSITY : int
        The maximum level of verbosity
    TAG_ERROR : string
        The error tag
    TAG_DEBUG : string
        The debug tag

    Attributes
    ----------
    verbosity : int [0,MAX_VERBOSITY] (default : MAX_VERBOSITY)
        the degree of verbosity (the more, the more verbose)

    Constructor parameters
    ----------------------
    verbosity : int [0,50] (default : 50)
        the degree of verbosity (the more, the more verbose)
    """
    __metaclass__ = ABCMeta

    MAX_VERBOSITY = 50
    TAG_ERROR = "Error"
    TAG_DEBUG = "Debug"

    def __init__(self, verbosity=MAX_VERBOSITY):
        self.set_verbosity(verbosity)
        self._follow_dictionary = {}

    def set_verbosity(self, verbosity):
        """
        Set the verbosity level

        Parameters
        ----------
        verbosity : int [0,50] (default : 50)
            the degree of verbosity (the more, the more verbose)
        """
        if verbosity < 0:
            verbosity = 0
        self.verbosity = verbosity

    def follow(self, *tags):
        """
        Add tags to follow

        Parameters
        ----------
        tags : strings
            The tags to follow
        """
        for tag in tags:
            self._follow_dictionary[tag] = True

    def stop_following(self, *tags):
        """
        Stop following some tags

        Parameters
        ----------
        tags : strings
            The tags to stop  following
        """
        for tag in tags:
            self._follow_dictionary.pop(tag)

    def _tag_message(self, message, *tags):
        """
        Tags the given message by the provided tags

        Parameters
        ----------
        message : string
            The message to tag
        tags : strings
            The tags to apply to the message
        """
        if len(tags) == 0:
            return message
        actual_message = ""
        for tag in tags:
            actual_message += ("#" + str(tag) + " ")
        actual_message += ("| " + message)
        return actual_message

    def should_log(self, min_verbosity, *tags):
        """
        Wether to log the message or not

        Parameters
        ----------
        min_verbosity : int >= 0 (default : 1)
            The minimum verbosity required to log this message
        tags : strings
            The tags associated to the message

        Return
        ------
        should_log : boolean
            True is the message should be logged. False if it should be ignored
        """
        if self.verbosity >= min_verbosity:
            return True
        for tag in tags:
            if tag in self._follow_dictionary:
                return True
        return False

    def log_msg(self, message, min_verbosity, *tags):
        """
        Log the given message

        Parameters
        ----------
        message : str
            The message string to log
        min_verbosity : int >= 0 (default : 1)
            The minimum verbosity required to log this message
        tags : strings
            The tags associated to the message
        """
        if self.should_log(min_verbosity, *tags):
            msg = self._tag_message(message, *tags)
            self._do_log_msg(msg)

    @abstractmethod
    def _do_log_msg(self, message):
        """
        Log the given message. This is where the actual logging should take
        place.

        Parameters
        ----------
        message : str
            The message string to log
        """
        pass

    def log_error(self, error_message, min_verbosity, *tags):
        """
        Log the error message. By default, the log is transmitted to the
        tradition log channel (see :method:`log_msg`).

        Note : an error tag is automatically prepended to the message

        Parameters
        ----------
        error_message : str
            The error message to log
        min_verbosity : int >= 0 (default : 0)
            The minimum verbosity required to log this message
        tags : strings
            The tags associated to the message
        """
        if self.should_log(min_verbosity, *tags):
            msg = self._tag_message(error_message, Logger.TAG_ERROR, *tags)
            self._do_log_error_msg(msg)

    def _do_log_error_msg(self, message):
        """
        Log the given error message. This is where the actual logging should
        take place.

        Parameters
        ----------
        message : str
            The message string to log
        """
        self._do_log_msg(message)

    def log_size(self, message, nb_bytes, min_verbosity, *tags):
        """
        Log a message which is appended by a size

       Parameters
       ----------
       message : str
           The message to log
       nb_bytes : number
           The size (in bytes) to log
       min_verbosity : int
           The minimum verbosity required to log this message
        """
        self.log_msg(message+format_size(nb_bytes),
                     min_verbosity=min_verbosity, *tags)

    def append_newline(self, message):
        """
        Append line ending (os.linesep) if necessary.

        Paramters
        ---------
        message : str
            a message

        Return
        ------
        msgLn : str
            the same message with a new line added if necessary
        """
        if not message.endswith(os.linesep):
            message += os.linesep
        return message


class VoidLogger(Logger):
    """
    ==========
    VoidLogger
    ==========
    A class:`Logger` class which discards all its messages
    """
    def __init__(self):
        Logger.__init__(self, 0)

    def should_log(self, min_verbosity, *tags):
        return False

    def _do_log_msg(self, message):
        pass


class StandardLogger(Logger):
    """
    ==============
    StandardLogger
    ==============
    A class:`Logger` class which prints messages in the standard outputs

    Parameters
    ----------
    auto_flush : boolean (Default : False)
        Whether to flush after each log or not
    verbosity : int [0,50] (default : 50)
        the degree of verbosity (the more, the more verbose)
    """

    def __init__(self, auto_flush=False, verbosity=50):
        Logger.__init__(self, verbosity)
        self._auto_flush = auto_flush

    def _do_log_msg(self, msg):
        msg = self.append_newline(msg)
        sys.stdout.write(msg)
        if self._auto_flush:
            sys.stdout.flush()

    def _do_log_error_msg(self, msg):
        msg = self.append_newline(msg)
        sys.stderr.write(msg)
        if self._auto_flush:
            sys.stderr.flush()


class FileLogger(Logger):
    """
    ==========
    FileLogger
    ==========
    A class:`Logger` class which prints messages in the files

    Parameters
    ----------
    output_file : file
        the output file to write to. It can also be another class which
        supports wirte and flush operations.
    error_file : file
        the output file to write error to. It can also be another class
        which supports wirte and flush operations.
    auto_flush : boolean (Default : False)
        Whether to flush after each log or not
    verbosity : int [0,50] (default : 50)
        the degree of verbosity (the more, the more verbose)
    """

    def __init__(self, output_file=sys.stdout, error_file=sys.stderr,
                 auto_flush=False, verbosity=50):
        Logger.__init__(self, verbosity)
        self._str = output_file  # stream
        self._err = error_file
        self._auto_flush = auto_flush

    def _do_log_msg(self, msg):
        msg = self.append_newline(msg)
        self._str.write(msg)
        if self._auto_flush:
            self._str.flush()

    def _do_log_error_msg(self, msg):
        msg = self.append_newline(msg)
        self._err.write(msg)
        if self._auto_flush:
            self._err.flush()

    def append_newline(self, msg):
        if not msg.endswith("\n"):
            msg += "\n"


class ProgressableTask:
    """
    ================
    ProgressableTask
    ================
    A :class:`ProgressableTask` is a task whose progression can n steps.
    Once the progression hits the max, the task status goes
    from `ProgressableTask.RUNNING` to `ProgressableTask.DONE`

    Class attributes
    ----------------
    nb_tasks : int
        The number of already created tasks. Beware that this is not
        thread-safe

    Class constants
    ---------------
    RUNNING : int
        State of a running task
    DONE : int
        State of a completed task

    Instance attributes
    -------------------
    id : int
        The id of the task
    name : str
        The name of the task

    Constructor parameters
    ----------------------
    nb_steps : int
        The number of step before completion
    name : str
        The name of the task
    verbosity : int (default : 1)
        The verbosity level of the task
    tag_list : list of strings (Default : [])
        The tags associated to the task
    """
    nb_tasks = 0

    RUNNING = 1
    DONE = 2

    def __init__(self, nb_steps, name="", verbosity=1, tag_list=[]):
        self.name = name
        self.id = ProgressableTask.nb_tasks
        ProgressableTask.nb_tasks += 1

        self.verbosity = verbosity
        self.tag_list = tag_list

        self._nb_steps = nb_steps
        self._progress = 0
        self._last_reset = 0
        self._status = ProgressableTask.RUNNING
        self._end_time = None
        self._start_time = time.time()

    def get_nb_steps(self):
        """
        Returns
        -------
        nb_steps : int
            The number of steps required by the task
        """
        return self._nb_steps

    def update(self, progress):
        """
        Update progress (if task is running)

        Parameters
        ----------
        progress : int
            the new progression score

        Return
        ------
        done : boolean
            True if the task is completed, False otherwise
        """
        if self._status == ProgressableTask.DONE:
            return True
        self._progress = progress
        if progress >= self._nb_steps-1:
            self._status = ProgressableTask.DONE
            self._end_time = time.time()
            return True
        else:
            return False

    def reset(self):
        """
        Reset the last progress counter. See method:`get_last_progress`
        """
        self._last_reset = self._progress

    def get_last_progress(self):
        """
        Return
        ------
        progress_percentage : int
            The last recorded percentage of progress
        """
        return int((100*(self._progress - self._last_reset)/self._nb_steps)+.5)

    def progress_as_string(self):
        """
        Return
        ------
        progress : str
            "progress/nb_steps"
        """
        return str(self._progress)+"/"+str(self._nb_steps)

    def duration(self):
        """
        Return
        ------
        duration : float
            the duration of taks in seconds (up to now if still running,
            up to completion if completed)
        """
        if self._status == ProgressableTask.DONE:
            return self._end_time - self._start_time
        else:
            return time.time() - self._start_time


class ProgressLogger(Logger):
    """
    ==============
    ProgressLogger
    ==============
    A :class:`Logger` decorator which can also log progress.
    See :class:`ProgressableTask`

    Class constants
    ---------------
    TASK_CREATION_VERB_LVL : int
        The minimum level of verbosity to log task creation
    TASK_COMPLETION_VERB_LVL : int
        The minimum level of verbosity to log task completion
    TASK_25_PROGRESS_VERB_LVL : int
        The minimum level of verbosity to log the progress every 25%
    TASK_10_PROGRESS_VERB_LVL : int
        The minimum level of verbosity to log the progress every 10%
    TASK_5_PROGRESS_VERB_LVL : int
        The minimum level of verbosity to log the progress every 5%
    TASK_1_PROGRESS_VERB_LVL : int
        The minimum level of verbosity to log the progress every 1%

    Constructor parameters
    ----------------------
    Logger : :class:`Logger`
        The decorated :class:`Logger`. Verbosity is deduced from that
        logger.
    """
    TASK_CREATION_VERB_LVL = 8
    TASK_COMPLETION_VERB_LVL = TASK_CREATION_VERB_LVL  # 8
    TASK_25_PROGRESS_VERB_LVL = TASK_CREATION_VERB_LVL  # 8
    TASK_10_PROGRESS_VERB_LVL = min((2.5*TASK_25_PROGRESS_VERB_LVL,
                                     Logger.MAX_VERBOSITY))  # 20
    TASK_5_PROGRESS_VERB_LVL = min((2*TASK_10_PROGRESS_VERB_LVL,
                                    Logger.MAX_VERBOSITY))  # 40
    TASK_1_PROGRESS_VERB_LVL = min((5*TASK_10_PROGRESS_VERB_LVL,
                                    Logger.MAX_VERBOSITY))  # 50

    def __init__(self, logger):
        Logger.__init__(self, logger.verbosity)
        self._decorated_logger = logger
        self._task_dictionary = {}

    def log_msg(self, msg, min_verbosity, *tags):
        self._decorated_logger.log_msg(msg, min_verbosity, *tags)

    def log_error(self, msg, min_verbosity, *tags):
        self._decorated_logger.log_error(msg, min_verbosity, *tags)

    def _do_log_msg(self, message):
        raise NotImplementedError("This method should not be called directly")

    def follow(self, *tags):
        self._decorated_logger.follow(*tags)

    def stop_following(self, *tags):
        self._decorated_logger.stop_following(*tags)

    def _log_progress(self, task, msg):
        """
        Log the progress message

        Parameters
        ----------
        task_id : int
            The id of the task
        msg : str
            The progression message to log
        """
        logging_message = ("Task " + str(task.id) + " '" + task.name + "' : " + msg)
        self.log_msg(logging_message, task.verbosity, *task.tag_list)

    def add_task(self, nb_steps, name="", min_verbosity=1, tag_list=[]):
        """
        Add a new task

        Parameters
        ----------
        nb_steps : int
            The number of step before completion
        name : str
            The name of the taks
        min_verbosity : int (default : 1)
            The minimum verbosity to log the task
        tag_list : list of strings (Default : [])
            The tags associated to the task

        Return
        ------
        task_id : int
            The id of the task
        """
        task = ProgressableTask(nb_steps, name, min_verbosity, tag_list)
        task_id = task.id
        self._task_dictionary.update({task_id: task})
        #Logging the message
        if self.verbosity >= ProgressLogger.TASK_CREATION_VERB_LVL:
            self._log_progress(task,
                              "Creation " + " (" + str(nb_steps) + " steps)")
        return task_id

    def update_progress(self, task_id, progress):
        """
        Log progress (if task is running)

        Parameters
        ----------
        task_id : int
            The id of the task
        progress : int
            The new progression score
        """
        task = self._task_dictionary[task_id]

        should_log = self._decorated_logger.should_log(task.verbosity, *task.tag_list)

        if task.update(progress):
            # True = Task completed
            del self._task_dictionary[task_id]

            #Logging the message
            if should_log and self.verbosity >= ProgressLogger.TASK_COMPLETION_VERB_LVL:
                duration = format_duration(task.duration())
                self._log_progress(task, "Completion in " + duration)
        else:
            # False = Task imcomplete
            if not should_log:
                return
            # Logging the message if necessary
            percProg = task.get_last_progress()
            if (self.verbosity >= ProgressLogger.TASK_1_PROGRESS_VERB_LVL
                    and percProg >= 1):
                task.reset()
                self._log_progress(task, task.progress_as_string())
                return
            if (self.verbosity >= ProgressLogger.TASK_5_PROGRESS_VERB_LVL
                    and percProg >= 5):
                task.reset()
                self._log_progress(task, task.progress_as_string())
                return
            if (self.verbosity >= ProgressLogger.TASK_10_PROGRESS_VERB_LVL
                    and percProg >= 10):
                task.reset()
                self._log_progress(task, task.progress_as_string())
                return
            if (self.verbosity >= ProgressLogger.TASK_25_PROGRESS_VERB_LVL
                    and percProg >= 25):
                task.reset()
                self._log_progress(task, task.progress_as_string())
                return


class Progressable(Logger):
    """
    ============
    Progressable
    ============

    A superclass for object which would like to monitor progress on maximum
    one task at a time

    Parameters
    ----------
    progressLogger : :class:`ProgressLogger` (default : VoidLogger)
        the object to report to. Can be None (nothing is reported).
        If None, a :class:`StandardLogger` is provided
    verbosity : int [0,50] (default : 10)
        the degree of verbosity (the higher, the more verbose)
    """
    def __init__(self, progressLogger=ProgressLogger(VoidLogger()), verbosity=10):
        Logger.__init__(self, verbosity)
        self.set_logger(progressLogger)
        self._task = None

    def set_logger(self, progressLogger):
        """
        Set the logger

        Parameters
        ----------
        progressLogger : :class:`ProgressLogger`
            the object to report to. Can be None (nothing is reported)

        Note
        ----
        The verbosity level is deduced from that logger
        """
        self._logger = progressLogger
        if progressLogger is not None:
            self.set_verbosity(progressLogger.verbosity)

    def set_task(self, nb_steps, name=None, min_verbosity=1, tag_list=[]):
        """
        Set the task whose progress to monitor

        Parameters
        ----------
        nb_steps : int
            The number of step before completion
        name : str (default : None)
            The name of the taks. If None, a name will be given to the task
        min_verbosity : int (default : 1)
            The verbosity level of the task. If None, the instance verbosity
            will be taken.
        tag_list : list of strings (Default : [])
            The tags associated to the task
        """
        if name is None:
            name = str(self)
        if min_verbosity is None:
            min_verbosity = self.verbosity
        self._task = self._logger.add_task(nb_steps, name, min_verbosity, tag_list)

    def update_progress(self, progress):
        """
        Log progress (if task is running)

        Parameters
        ----------
        progress : int
            The new progression score
        """
        if self._task is not None:
            self._logger.update_progress(self._task, progress)

    def end_task(self):
        """
        Ends the current task
        """
        if self._task is not None:
            self.update_progress(sys.maxsize)

    def log_msg(self, msg, min_verbosity, *tags):
        self._logger.log_msg(str(self)+" : "+msg, min_verbosity, *tags)

    def log_error(self, msg, min_verbosity, *tags):
        self._logger.log_error(str(self)+" : "+msg, min_verbosity, *tags)

    def follow(self, *tags):
        self._logger.follow(*tags)

    def stop_following(self, *tags):
        self._logger.stop_following(*tags)

    def _do_log_msg(self, message):
        raise NotImplementedError("This method should not be called directly")

if __name__ == "__main__":
    import random as rd

    verbosity = 20
    t1max = 100
    t2max = 89
    t3max = 10

    sLog = StandardLogger(verbosity=verbosity)
    logger = ProgressLogger(sLog)

    id1 = logger.add_task(t1max, "t1", 50, ["test_tag"])
    id2 = logger.add_task(t2max, "t2", 1)
    logger.follow("test_tag")

    t1 = 0
    t2 = 0

    for i in xrange(t1max+t2max-1):
        if t1 == t1max-1 and t2 == t2max-1:
            break
        if t1 == t1max-1:
            t2 += 1
            logger.update_progress(id2, t2)
        elif t2 == t2max-1:
            t1 += 1
            logger.update_progress(id1, t1)
        else:
            if rd.random() > .5:
                t2 += 1
                logger.update_progress(id2, t2)
            else:
                t1 += 1
                logger.update_progress(id1, t1)

    id3 = logger.add_task(t3max, "t3")
    for i in xrange(t3max):
        logger.update_progress(id3, i)

    print "=========DONE========"
    pass
