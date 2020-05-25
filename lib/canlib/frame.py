class Frame(object):
    """Represents a CAN message

    Args:
        id_: Message id
        data : Message data, will pad zero to match dlc (if dlc is given)
        dlc : Message dlc, default is calculated from number of data
        flags : Message flags, default is 0
        timestamp : Optional timestamp
    """

    __slots__ = ('id', 'data', 'dlc', 'flags', 'timestamp')
    _repr_slots = __slots__
    _eq_slots = __slots__[:-1]

    def __init__(self, id_, data, dlc=None, flags=0, timestamp=None):
        data = bytearray(data)

        if dlc is None:
            if len(data) <= 8:
                dlc = len(data)
            elif len(data) <= 12:
                dlc = 12
            elif len(data) <= 16:
                dlc = 16
            elif len(data) <= 20:
                dlc = 20
            elif len(data) <= 24:
                dlc = 24
            elif len(data) <= 32:
                dlc = 32
            elif len(data) <= 48:
                dlc = 48
            else:
                dlc = 64
            if dlc > len(data):
                data.extend([0] * (dlc - len(data)))
        elif dlc <= 8:
            data.extend([0] * (dlc - len(data)))

        self.id = id_
        self.data = data
        self.dlc = dlc
        self.flags = flags
        self.timestamp = timestamp

    # in Python 2 both __eq__ and __ne__ must be implemented
    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Frame):
            return all(
                getattr(self, slot) == getattr(other, slot)
                for slot in self._eq_slots
            )
        else:
            return NotImplemented

    def __getitem__(self, index):
        slot = self.__slots__[index]
        return getattr(self, slot)

    def __setitem__(self, index, val):
        slot = self.__slots__[index]
        return setattr(self, slot, val)

    def __iter__(self):
        for slot in self.__slots__:
            yield getattr(self, slot)

    def __repr__(self):
        return '{cls}({kwargs})'.format(
            cls=self.__class__.__name__,
            kwargs=', '.join(
                slot + '=' + repr(getattr(self, slot))
                for slot in self._repr_slots
            ),
        )


class LINFrame(Frame):
    """Represents a LIN message

    A `Frame` that also has a `info` attribute, which is a
    `linlib.MessageInfo` or `None`. This attribute is initialized via the `info`
    keyword-only argument to `__init__`.

    """
    __slots__ = Frame.__slots__ + ('info', )

    # In python 3 we could just use:
    #
    # def __init__(self, *args, info=None, **kwargs):
    def __init__(self, *args, **kwargs):
        info = kwargs.pop("info", None)
        if 'timestamp' not in kwargs and info is not None:
            kwargs['timestamp'] = info.timestamp
        super(LINFrame, self).__init__(*args, **kwargs)
        self.info = info
