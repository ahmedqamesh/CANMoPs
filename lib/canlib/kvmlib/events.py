import binascii

from .. import frame, canlib


def _eq_or_none(a, b):
    return a == b or a is None or b is None


class LogEvent(object):
    _comp_fields = None  # if not None, these attributes will be used to
    # compare objects

    def __init__(self, timestamp=None):
        self.timeStamp = timestamp
        self.ignored = False

    def __str__(self):
        if self.ignored:
            text = "*t:"
        else:
            text = " t:"
        if self.timeStamp is not None:
            text += "%14s " % (self.timeStamp / 1000000000.0)
        else:
            text += "             - "
        return text

    # In python 2, both __eq__ and __ne__ must be defined
    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return eq
        else:
            return not eq

    def __eq__(self, other):
        if not isinstance(other, LogEvent):
            return NotImplemented
        elif self._comp_fields is None:
            return NotImplemented
        elif self._comp_fields != other._comp_fields:
            return NotImplemented

        return all(
            _eq_or_none(getattr(self, name), getattr(other, name))
            for name in self._comp_fields
        )


class MessageEvent(LogEvent):
    """A CAN message recorded by a Memorator"""

    _comp_fields = ('id', 'channel', 'dlc', 'flags', 'data', 'timeStamp')

    def __init__(self, id=None, channel=None, dlc=None, flags=None, data=None,
                 timestamp=None):
        super(MessageEvent, self).__init__(timestamp)
        self.id = id
        self.channel = channel
        self.dlc = dlc
        self.flags = flags
        if data is not None and not isinstance(data, (bytes, str)):
            if not isinstance(data, bytearray):
                data = bytearray(data)
            data = bytes(data)

        self.data = data
        if dlc is not None and data is not None:
            if len(data) > dlc:
                # dlc is (often) number of bytes
                self.data = data[:dlc]

    def asframe(self):
        """Convert this event to a `canlib.Frame`

        Creates a new `canlib.Frame` object with the same contents as this event.

        """
        return frame.Frame(
            id_=self.id,
            data=self.data,
            dlc=self.dlc,
            flags=canlib.MessageFlag(self.flags),
            timestamp=self.timeStamp,
        )

    def __str__(self):
        text = super(MessageEvent, self).__str__()
        text += " ch:%s " % ("-" if self.channel is None else "%x" %
                            self.channel)
        text += "f:%s " % (" -" if self.flags is None else "%5x" % self.flags)
        text += "id:%s " % ("   -" if self.id is None else "%4x" % self.id)
        text += "dlc:%s " % ("-" if self.dlc is None else "%2d" % self.dlc)
        if self.data is not None:
            data = self.data
            if not isinstance(data, (bytes, str)):
                if not isinstance(data, bytearray):
                    data = bytearray(data)
                data = bytes(data)
            try:
                hex = unicode(binascii.hexlify(data))
            except (NameError):
                hex = str(binascii.hexlify(data), 'ascii')
            formatted_data = ' '.join(hex[i:i + 2]
                                      for i in range(0, len(hex), 2))
            text += "d:%s" % formatted_data
        else:
            text += "d: -  -  -  -  -  -  -  -"
        return text


class RTCEvent(LogEvent):
    """An real-time clock message recorded by a Memorator"""
    _comp_fields = ('calendartime', 'timeStamp')

    def __init__(self, calendartime=None, timestamp=None):
        super(RTCEvent, self).__init__(timestamp)
        self.calendartime = calendartime

    def __str__(self):
        text = super(RTCEvent, self).__str__()
        text += " DateTime: %s" % self.calendartime
        return text


class TriggerEvent(LogEvent):
    """A trigger message recorded by a Memorator"""
    _comp_fields = ('type', 'timeStamp', 'pretrigger', 'posttrigger', 'trigno')

    def __init__(self, type=None, timestamp=None, pretrigger=None,
                 posttrigger=None, trigno=None):
        super(TriggerEvent, self).__init__(timestamp)
        self.type = type
        self.pretrigger = pretrigger
        self.posttrigger = posttrigger
        self.trigno = trigno

    def __str__(self):
        text = super(TriggerEvent, self).__str__()
        text += "Log Trigger Event ("
        text += "type: 0x%x, " % (self.type)
        text += "trigno: 0x%02x, " % (self.trigno)
        text += "pre-trigger: %d, " % (self.pretrigger)
        text += "post-trigger: %d)\n" % (self.posttrigger)
        return text


class VersionEvent(LogEvent):
    """A version message recorded by a Memorator"""
    _comp_fields = ('lioMajor', 'lioMinor',
                    'fwMajor', 'fwMinor', 'fwBuild',
                    'serialNumber',
                    'eanHi', 'eanLo')

    def __init__(self, lioMajor, lioMinor, fwMajor, fwMinor, fwBuild,
                 serialNumber, eanHi, eanLo):
        super(VersionEvent, self).__init__(None)
        self.lioMajor = lioMajor
        self.lioMinor = lioMinor
        self.fwMajor = fwMajor
        self.fwMinor = fwMinor
        self.fwBuild = fwBuild
        self.serialNumber = serialNumber
        self.eanHi = eanHi
        self.eanLo = eanLo
        self.ignored = True

    def __str__(self):
        text = super(VersionEvent, self).__str__()
        text += ("EAN:%02x-%05x-%05x-%x  " %
                 (self.eanHi >> 12,
                  ((self.eanHi & 0xfff) << 8) | (self.eanLo >> 24),
                  (self.eanLo >> 4) & 0xfffff, self.eanLo & 0xf))
        text += "s/n:%d  " % (self.serialNumber)
        text += "FW:v%s.%s.%s  " % (self.fwMajor, self.fwMinor, self.fwBuild)
        text += "LIO:v%s.%s" % (self.lioMajor, self.lioMinor)
        return text
