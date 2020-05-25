import ctypes as ct
import os

from .. import deprecation
from . import wrapper


class Converter(object):
    """A kvlclib converter

    This class wraps all kvlclib functions related to converters, and saves you
    from keeping track of a handle and passing that to the functions.

    `kvlcCreateConverter` and `kvlcDeleteConverter` are not wrapped as they are
    called when Converter objects are created and deleted,
    respectively. However, if it is necessary to force the converter to write
    its files, `flush` can be used to simulate destroying and recreating the
    converter object.

    Note:
        No more than 128 converters can be open at the same time.

    """

    def __init__(self, filename, file_format):
        self.format = file_format
        self.handle = ct.c_void_p(None)
        self.filename = filename
        self.file_format = file_format
        wrapper.dll.kvlcCreateConverter(
            ct.byref(self.handle), filename.encode(), file_format.id_)

    def __del__(self):
        """Delete the converter and close all files."""
        if wrapper and wrapper.dll:
            wrapper.dll.kvlcDeleteConverter(self.handle)

    def addDatabaseFile(self, filename, channel_mask):
        """Add a database file.

        Converters with the property PROPERTY_SIGNAL_BASED will match
        events against all entries in the database and write signals to the
        output file.

        """
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        wrapper.dll.kvlcAddDatabaseFile(self.handle, ct_filename, channel_mask)

    def attachFile(self, filename):
        """Attach file to be included in the output file.

        E.g. used to add a database or a movie to the output.

        Note that the output format must support the property
        PROPERTY_ATTACHMENTS.
        """
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        wrapper.dll.kvlcAttachFile(self.handle, ct_filename)

    def convertEvent(self):
        """Convert next event.

        Convert one event from input file and write it to output file.
        """
        wrapper.dll.kvlcConvertEvent(self.handle)

    def flush(self):
        """Recreate the converter so changes are saved to disk

        Converters do not write changes to disk until they are deleted. This
        method deletes and recreates the underlying C converter, without
        needing to recreate the Python object.

        """
        self.__del__()
        self.__init__(self.filename, self.file_format)

    def getProperty(self, wr_property):
        """Get current value for a writer property."""
        buf = wr_property['type']
        wrapper.dll.kvlcGetProperty(
            self.handle, wr_property['value'], ct.byref(buf), ct.sizeof(buf))
        return buf.value

    def getOutputFilename(self):
        """Get the filename of the current output file."""
        filename = ct.create_string_buffer(256)
        wrapper.dll.kvlcGetOutputFilename(
            self.handle, filename, ct.sizeof(filename))
        return filename.value.decode('utf-8')

    def nextInputFile(self, filename):
        """Select next input file."""
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        wrapper.dll.kvlcNextInputFile(self.handle, ct_filename)

    def eventCount(self):
        """Get extimated number of events left.

        Get the estimated number of remaining events in the input file. This
        can be useful for displaying progress during conversion.
        """
        count = ct.c_uint(0)
        wrapper.dll.kvlcEventCount(self.handle, ct.byref(count))
        return count.value

    def setProperty(self, wr_property, value):
        """Set a property value.

        Args:
            wr_property (int): Any one of the defined PROPERTY_xxx
        """
        buf = wr_property['type']
        buf.value = value
        wrapper.dll.kvlcSetProperty(
            self.handle, wr_property['value'], ct.byref(buf), ct.sizeof(buf))

    def isOutputFilenameNew(self):
        """Check if the converter has created a new file.

        This is only true once after a a new file has been created. Used when
        splitting output into multiple files.
        """
        updated = ct.c_int()
        wrapper.dll.kvlcIsOutputFilenameNew(
            self.handle, ct.byref(updated))
        return updated.value

    @deprecation.deprecated.replacedby(isOutputFilenameNew)
    def IsOutputFilenameNew(self):
        pass

    def isOverrunActive(self):
        """Get overrun status.

        Overruns can occur during logging with a Memorator if the bus load
        exceeds the logging capacity. This is very unusual, but can occur if a
        Memorator runs complex scripts and triggers.
        """
        overrun = ct.c_int()
        wrapper.dll.kvlcIsOverrunActive(self.handle, ct.byref(overrun))
        return overrun.value

    @deprecation.deprecated.replacedby(isOverrunActive)
    def IsOverrunActive(self):
        pass

    def resetOverrunActive(self):
        """Reset overrun status."""
        wrapper.dll.kvlcResetOverrunActive(self.handle)

    def isDataTruncated(self):
        """Get truncation status.

        Truncation occurs when the selected output converter can't write all
        bytes in a data frame to file. This can happen if CAN FD data is
        extracted to a format that only supports up to 8 data bytes,
        e.g. FILE_FORMAT_KME40.

        Truncation can also happen if PROPERTY_LIMIT_DATA_BYTES is set
        to limit the number of data bytes in output.

        Returns True if data has been truncated
        """
        truncated = ct.c_int()
        wrapper.dll.kvlcIsDataTruncated(self.handle, ct.byref(truncated))
        return truncated.value

    @deprecation.deprecated.replacedby(isDataTruncated)
    def IsDataTruncated(self):
        pass

    def resetStatusTruncated(self):
        """Reset data trunctation status."""
        wrapper.dll.kvlcResetDataTruncated(self.handle)

    def setInputFile(self, filename, file_format):
        """Select input file.

        Args:
            filename (string): Name of input file
            file_format (int): Any of the supported input FILE_FORMAT_xxx
        """
        filename = os.path.realpath(filename)
        ct_filename = ct.c_char_p(filename.encode('utf-8'))
        wrapper.dll.kvlcSetInputFile(self.handle, ct_filename, file_format)

    @deprecation.deprecated.favour(".format.getPropertyDefault")
    def getPropertyDefault(self, wr_property):
        """Get default value for a writer property."""
        return self.format.getPropertyDefault(wr_property)

    @deprecation.deprecated.favour(".format.isPropertySupported")
    def isPropertySupported(self, wr_property):
        """Check if specified wr_property is supported by the current format.

        Retuns True if the property is supported by the current format.

        Args:
            wr_property (int): Any one of the defined PROPERTY_xxx
        """
        return self.format.isPropertySupported(wr_property)
