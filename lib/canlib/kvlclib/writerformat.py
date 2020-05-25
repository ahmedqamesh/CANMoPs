import ctypes as ct

from .enums import FileFormat
from .wrapper import dll


class WriterFormat(object):
    """Helper class that encapsulates a Writer.

    You may list available Writers, and query properties.
    """

    @classmethod
    def getFirstWriterFormat(cls):
        """Get the first supported output format."""
        id_ = ct.c_int()
        dll.kvlcGetFirstWriterFormat(ct.byref(id_))
        return FileFormat(id_.value)

    @classmethod
    def getNextWriterFormat(cls, previous_id):
        """Get the next supported output format."""
        id_ = ct.c_int()
        dll.kvlcGetNextWriterFormat(previous_id, ct.byref(id_))
        return FileFormat(id_.value)

    def __init__(self, id_):
        self.id_ = id_
        self.name = "Unknown name"
        self.extension = "Unknown extension"
        self.description = "Unknown description"

        text = ct.create_string_buffer(256)
        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterName(self.id_, text, text_len)
        self.name = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterExtension(self.id_, text, text_len)
        self.extension = text.value.decode('utf-8')

        text_len = ct.c_int(ct.sizeof(text))
        dll.kvlcGetWriterDescription(self.id_, text, text_len)
        self.description = text.value.decode('utf-8')

    def isPropertySupported(self, wr_property):
        """Check if specified write property is supported.

        Retuns True if the property is supported by output format.

        Args:
            wr_property (int): Any one of the defined PROPERTY_xxx
        """
        supported = ct.c_int()
        # qqqmac check that error handling works in class WriterFormat
        dll.kvlcIsPropertySupported(
            self.id_, wr_property['value'], ct.byref(supported))
        return supported.value

    def getPropertyDefault(self, wr_property):
        """Get default value for property."""
        if wr_property['type'] is None:
            buf = ct.c_bool()
        else:
            buf = wr_property['type']
        dll.kvlcGetWriterPropertyDefault(
            self.id_, wr_property['value'], ct.byref(buf), ct.sizeof(buf))
        return buf.value

    def __str__(self):
        text = "%4d: %s (.%s)" % (self.id_, self.name, self.extension)
        text += ", %s" % self.description
        return text
