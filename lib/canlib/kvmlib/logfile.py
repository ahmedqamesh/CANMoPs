import ctypes as ct
import datetime
from functools import wraps

from .exceptions import KvmNoLogMsg
from .structures import memoLogEventEx
from .wrapper import dll


class LogFile(object):
    """A log file read from a `MountedLog` object

    This class is normally not directly instantiated but retrieved from a
    `MountedLog` object.

    The most common use of this class is iterating through it to get the
    individual events as `LogEvent` subclasses::

        for event in logfile:
            ...

    Note:

        While iterating over a `LogFile`, accessing any other `LogFile` is will
        result in a `LockedLogError`. Make sure to finish the loop (or when
        using iteration objects directly call the `close` method) before
        interacting with any other log files.

    The number of events is available as the ``len()`` of this object::

        num_events = len(logfile)

    Finally this class has several read-only properties for getting information
    about the log file itself.

    Note:
        Before any data is fetched from the dll, this class will make sure that
        the correct file has been mounted on the underlying ``kvmHandle``.

        Manually mounting or unmounting log files by calling the dll directly
        is not supported.

    .. versionadded:: 1.6

    """
    def _mounted_handle(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cont = self._container
            if cont._mounted_index != self.index:
                self._remount()
            return func(self, cont.handle, *args, **kwargs)

        return wrapper

    def __init__(self, container, index):
        self._container = container
        self.index = index

    def __iter__(self):
        # force a remount, to reset the dll's internal event counter
        self._remount()

        try:
            self._container._mount_lock = True
            while True:
                # It is currently up to the user to make sure the handle/device
                # stays mounted on this file during iteration.
                eventstruct = memoLogEventEx()
                dll.kvmLogFileReadEvent(self._container.handle, ct.byref(eventstruct))
                event = eventstruct.createMemoEvent()
                yield event
        except (KvmNoLogMsg, GeneratorExit):
            # GeneratorExit is raised when close() is called on this
            # generator. This means that if we iterate over the LogFile
            # manually (it = iter(LogFile) and then next(it)) we can also
            # release the lock when we close it (it.close())
            self._container._mount_lock = False
            return

    @property
    @_mounted_handle
    def creator_serial(self, handle):
        """`int`: The serial number of the interface that created the log file"""
        serial = ct.c_uint32()
        dll.kvmLogFileGetCreatorSerial(handle, ct.byref(serial))
        return serial.value

    @property
    @_mounted_handle
    def end_time(self, handle):
        """`datetime.datetime`: The time of the last event in the log file"""
        time = ct.c_uint32()
        dll.kvmLogFileGetEndTime(handle, ct.byref(time))
        return datetime.datetime.fromtimestamp(time.value)

    @property
    @_mounted_handle
    def start_time(self, handle):
        """`datetime.datetime`: The time of the first event in the log file"""
        time = ct.c_uint32()
        dll.kvmLogFileGetStartTime(handle, ct.byref(time))
        return datetime.datetime.fromtimestamp(time.value)

    def _remount(self):
        return self._container._mount(self.index)
