"""Wrapper for the Kvaser kvmlib library

The kvmlib is used to interact with Kvaser Memorator devices that can record
CAN messages (E.g. Kvaser Memorator Professional 5xHS). You can download
configuration data (e.g. triggers, filters, scripts) allowing you to disconnect
the device from your computer, connect the device to a CAN bus and let it
record the traffic autonomously. When done, you can reconnect the device with
your computer and use kvmlib to get the recorded data.

"""

from .constants import *
from .enums import Error, Device, FileType, LoggerDataFormat
from .events import MessageEvent, RTCEvent, TriggerEvent, VersionEvent, LogEvent
from .exceptions import KvmError, KvmDiskError, KvmNoDisk, KvmDiskNotFormated
from .exceptions import KvmNoLogMsg, LockedLogError
from .memorator import openDevice, Memorator
from .kmf import openKmf, Kmf, KmfSystem
from .log import UnmountedLog, MountedLog
from .logfile import LogFile
from .structures import memoLogMsgEx, memoLogRtcClockEx, memoLogTriggerEx
from .structures import memoLogVersionEx, memoLogRaw, memoLogMrtEx, memoLogEventEx
from .wrapper import dllversion

from .messages import memoMsg, logMsg, rtcMsg, trigMsg, verMsg  # Deprecated classes
from .deprecated import KvmLib as kvmlib  # for backwards-compatibility

kvmError = KvmError
kvmDiskError = KvmDiskError
kvmNoDisk = KvmNoDisk
kvmDiskNotFormated = KvmDiskNotFormated
kvmNoLogMsg = KvmNoLogMsg
