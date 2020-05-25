import sys

from .. import deprecation
from .converter import Converter
from . import wrapper


class KvlcLib(Converter):
    """Deprecated wrapper class for the Kvaser converter library kvlclib.

    .. deprecated:: 1.5

    Most functionality of this class has been moved to kvlclib.Converter::

      # deprecated
      from canlib import kvlclib
      lc = kvlclib.KvlcLib("filename", WriterFormat(kvlclib.FileFormat.KME24))
      lc.functionName()

      # use this instead
      from canlib import kvlclib
      converter = kvlclib.Converter("filename", WriterFormat(kvlclib.FileFormat.KME24))
      converter.functionName()

    `deleteConverter()` has been deprecated, converters are automatically deleted
    when garbage collected. Also see the new `Converter.flush()`

    `getVersion()` is now a function in kvlclib:

      # deprecated
      from canlib import kvlclib
      lc = kvlclib.KvlcLib("filename", WriterFormat(kvlclib.FileFormat.KME24))
      lc.getVersion()

      # use this instead
      from canlib import kvlclib
      kvlclib.getVersion()

    """

    def __init__(self, filename, file_format):
        super(KvlcLib, self).__init__(filename, file_format)

        deprecation.manual_warn(
            "Creating KvlcLib objects is deprecated, "
            "most functionality has been moved to the kvlclib.Converter.")
        self._module = wrapper

    def __getattr__(self, name):
        try:
            return getattr(self._module, name)
        except AttributeError:
            raise AttributeError("{t} object has no attribute {n}".format(
                t=str(type(self)), n=name))

    def deleteConverter(self):
        deprecation.manual_warn(
            "Manually deleting converters is deprecated. Also see flush().")
        self.flush()
