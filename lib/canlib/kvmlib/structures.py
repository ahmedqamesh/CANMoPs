import ctypes as ct
import datetime

from .events import MessageEvent, RTCEvent, TriggerEvent, VersionEvent

# Info we can get from a LogFile:
#  - eventCount    The approximate number of events in the log file
#  - startTime     The time of the first event in the log file


class memoLogMsgEx(ct.Structure):
    _fields_ = [('evType', ct.c_uint32),
                ('id', ct.c_uint32),  # The identifier
                ('timeStamp', ct.c_int64),   # timestamp in units of 1 nanoseconds
                # The channel on which the message arrived (0,1,...)
                ('channel', ct.c_uint32),
                ('dlc', ct.c_uint32),  # The length of the message
                ('flags', ct.c_uint32),  # Message flags
                ('data', ct.c_uint8 * 64)]  # Message data (8 bytes)


class memoLogRtcClockEx(ct.Structure):
    _fields_ = [('evType', ct.c_uint32),
                ('calendarTime', ct.c_uint32),  # RTC date (unix time format)
                ('timeStamp', ct.c_int64),
                ('padding', ct.c_uint8 * 24)]


class memoLogTriggerEx(ct.Structure):
    _fields_ = [('evType', ct.c_uint32),
                ('type', ct.c_int32),
                ('preTrigger', ct.c_int32),
                ('postTrigger', ct.c_int32),
                ('trigNo', ct.c_uint32),  # Bitmask with the activated trigger(s)

                # Timestamp in units of 1 nanoseconds; Can't use int64 here
                # since it is not naturally aligned
                ('timeStampLo', ct.c_uint32),
                ('timeStampHi', ct.c_uint32),

                ('padding', ct.c_uint8 * 8)]


class memoLogVersionEx(ct.Structure):
    _fields_ = [('evType', ct.c_uint32),
                ('lioMajor', ct.c_uint32),
                ('lioMinor', ct.c_uint32),
                ('fwMajor', ct.c_uint32),
                ('fwMinor', ct.c_uint32),
                ('fwBuild', ct.c_uint32),
                ('serialNumber', ct.c_uint32),
                ('eanHi', ct.c_uint32),
                ('eanLo', ct.c_uint32)]


class memoLogRaw(ct.Structure):
    _fields_ = [('evType', ct.c_uint32),
                ('data', ct.c_uint8 * 32)]


class memoLogMrtEx(ct.Union):
    _fields_ = [('msg', memoLogMsgEx),
                ('rtc', memoLogRtcClockEx),
                ('trig', memoLogTriggerEx),
                ('ver', memoLogVersionEx),
                ('raw', memoLogRaw)]


class memoLogEventEx(ct.Structure):

    MEMOLOG_TYPE_INVALID = 0
    MEMOLOG_TYPE_CLOCK = 1
    MEMOLOG_TYPE_MSG = 2
    MEMOLOG_TYPE_TRIGGER = 3
    MEMOLOG_TYPE_VERSION = 4

    _fields_ = [('event', memoLogMrtEx)]

    def _dlcToBytes(self, dlc):
        if dlc < 9:
            return dlc
        if dlc == 9:
            return 12
        if dlc == 10:
            return 16
        if dlc == 11:
            return 20
        if dlc == 12:
            return 24
        if dlc == 13:
            return 32
        if dlc == 14:
            return 48
        return 64

    def createMemoEvent(self):
        type = self.event.raw.evType

        if type == self.MEMOLOG_TYPE_CLOCK:
            cTime = self.event.rtc.calendarTime
            ct = datetime.datetime.fromtimestamp(cTime)
            memoEvent = RTCEvent(timestamp=self.event.rtc.timeStamp,
                                 calendartime=ct)

        elif type == self.MEMOLOG_TYPE_MSG:
            memoEvent = MessageEvent(timestamp=self.event.msg.timeStamp,
                                     id=self.event.msg.id,
                                     channel=self.event.msg.channel,
                                     dlc=self.event.msg.dlc,
                                     flags=self.event.msg.flags,
                                     data=self.event.msg.data)

        elif type == self.MEMOLOG_TYPE_TRIGGER:
            tstamp = (self.event.trig.timeStampLo + (
                self.event.trig.timeStampHi * 4294967296))
            memoEvent = TriggerEvent(timestamp=tstamp, type=self.event.trig.type,
                                     pretrigger=self.event.trig.preTrigger,
                                     posttrigger=self.event.trig.postTrigger,
                                     trigno=self.event.trig.trigNo)

        elif type == self.MEMOLOG_TYPE_VERSION:
            memoEvent = VersionEvent(lioMajor=self.event.ver.lioMajor,
                                     lioMinor=self.event.ver.lioMinor,
                                     fwMajor=self.event.ver.fwMajor,
                                     fwMinor=self.event.ver.fwMinor,
                                     fwBuild=self.event.ver.fwBuild,
                                     serialNumber=self.event.ver.serialNumber,
                                     eanHi=self.event.ver.eanHi,
                                     eanLo=self.event.ver.eanLo)
        else:
            raise Exception("createMemoEvent: Unknown event type :%d" % type)

        return memoEvent

    def __str__(self):
        type = self.event.raw.evType
        text = "Unkown type %d" % type

        if type == self.MEMOLOG_TYPE_CLOCK:
            cTime = self.event.rtc.calendarTime
            text = "t:%11f " % (self.event.rtc.timeStamp / 1000000000.0)
            text += ("DateTime: %s (%d)\n" %
                     (datetime.datetime.fromtimestamp(cTime), cTime))

        if type == self.MEMOLOG_TYPE_MSG:
            timestamp = self.event.msg.timeStamp
            channel = self.event.msg.channel
            flags = self.event.msg.flags
            dlc = self.event.msg.dlc
            id = self.event.msg.id
            data = self.event.msg.data[:self._dlcToBytes(dlc)]
            dataString = " ".join(hex(c).split('x')[1] for c in data)
            text = ("t:%11f ch:%x f:%5x id:%4x dlc:%2d d:%s"
                    % (timestamp / 1000000000.0, channel, flags, id,
                       dlc, dataString))

        if type == self.MEMOLOG_TYPE_TRIGGER:
            # evType = self.event.trig.evType
            ttype = self.event.trig.type
            preTrigger = self.event.trig.preTrigger
            postTrigger = self.event.trig.postTrigger
            trigNo = self.event.trig.trigNo
            tstamp = (self.event.trig.timeStampLo + (
                self.event.trig.timeStampHi * 4294967296))
            text = "t:%11f " % (tstamp / 1000000000.0)
            # text =  "t  : %11x\n" % (tstamp)
            # text += " et: %x (%x)\n" % (evType, type)
            text += "Log Trigger Event ("
            text += "type: 0x%x, " % (ttype)
            text += "trigNo: 0x%02x, " % (trigNo)
            text += "pre-trigger: %d, " % (preTrigger)
            text += "post-trigger: %d)\n" % (postTrigger)

        if type == self.MEMOLOG_TYPE_VERSION:
            lioMajor = self.event.ver.lioMajor
            lioMinor = self.event.ver.lioMinor
            fwMajor = self.event.ver.fwMajor
            fwMinor = self.event.ver.fwMinor
            fwBuild = self.event.ver.fwBuild
            serialNumber = self.event.ver.serialNumber
            eanHi = self.event.ver.eanHi
            eanLo = self.event.ver.eanLo
            text = ("EAN:%02x-%05x-%05x-%x, " %
                    (eanHi >> 12,
                     ((eanHi & 0xfff) << 8) | (eanLo >> 24),
                     (eanLo >> 4) & 0xfffff, eanLo & 0xf))
            text += "S/N %d, " % serialNumber
            text += "FW v%d.%d.%d, " % (fwMajor, fwMinor, fwBuild)
            text += "LIO v%d.%d" % (lioMajor, lioMinor)
        return text
