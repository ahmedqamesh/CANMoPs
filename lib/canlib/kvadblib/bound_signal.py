class BoundSignal(object):
    def __init__(self, signal, frame):
        self.frame = frame
        self.signal = signal

    def __repr__(self):
        txt = ("<{}: name={!r}, phys={!r}>".
               format(self.__class__.__name__, self.name, self.phys))
        if self.unit:
            txt += ", unit:{}".format(self.unit)
        return txt

    @property
    def phys(self):
        """`int` or `float`: Signal's physical value"""
        value = self.signal.phys_from(self.frame.data)
        return value

    @phys.setter
    def phys(self, value):
        self.frame.data = self.signal.data_from(self.frame.data, phys=value)

    @property
    def raw(self):
        """`int`: Signal's raw value"""
        value = self.signal.raw_from(self.frame.data)
        return value

    @raw.setter
    def raw(self, value):
        self.frame.data = self.signal.data_from(self.frame.data, raw=value)

    @property
    def unit(self):
        """`str`: Signal's unit string"""
        return self.signal.unit

    @property
    def name(self):
        """`str`: Signal's name string"""
        return self.signal.name
