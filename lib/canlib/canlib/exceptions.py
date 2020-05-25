import ctypes as ct

from ..exceptions import DllException
from .enums import Error


_all_errors_by_status = {}


def _remember(cls):
    _all_errors_by_status[cls.status] = cls
    return cls


def can_error(status):
    if status in _all_errors_by_status:
        return _all_errors_by_status[status]()
    else:
        return CanGeneralError(status)


class CanError(DllException):
    """Base class for exceptions raised by the canlib class

    Looks up the error text in the canlib dll and presents it together with the
    error code and the wrapper function that triggered the exception.

    """
    @staticmethod
    def _get_error_text(status):
        try:
            from .wrapper import dll  # import here to prevent circular imports
            msg_buf = ct.create_string_buffer(80)
            dll.canGetErrorText(status, msg_buf, ct.sizeof(msg_buf))
            msg = msg_buf.value.decode('utf-8')
        except:
            msg = "Unknown error text"
        msg += ' (%d)' % status
        return msg


class CanGeneralError(CanError):
    """A canlib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `CanError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `CanError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super(CanGeneralError, self).__init__()


@_remember
class CanNoMsg(CanError):
    """Raised when no matching message was available"""
    status = Error.NOMSG


@_remember
class CanScriptFail(CanError):
    """Raised when a script call failed.

    This exception represents several different failures, for example:
    - Trying to load a corrupt file or not a .txe file
    - Trying to start a t script that has not been loaded
    - Trying to load a t script compiled with the wrong version
    of the t compiler
    - Trying to unload a t script that has not been stopped
    - Trying to use an envvar that does not exist
    """
    status = Error.SCRIPT_FAIL


@_remember
class CanNotFound(CanError):
    """Specified device or channel not found

    There is no hardware available that matches the given search criteria. For
    example, you may have specified canOPEN_REQUIRE_EXTENDED but there's no
    controller capable of extended CAN. You may have specified a channel number
    that is out of the range for the hardware in question. You may have
    requested exclusive access to a channel, but the channel is already
    occupied.

    .. versionadded:: 1.6

    """
    status = Error.NOTFOUND


@_remember
class CanNotImplementedError(CanError):
    """Not implemented

    The requested feature or function is not implemented in the device you are
    trying to use it on.

    """
    status = Error.NOT_IMPLEMENTED


class EnvvarException(Exception):
    """Base class for exceptions related to environment variables."""
    pass


class EnvvarValueError(EnvvarException):
    """
    Raised when the type of the value does not match the type of the
    environment variable.

    """
    def __init__(self, envvar, type_, value):
        msg = ("invalid literal for envvar ({envvar}) with"
               " type {type_}: {value}")
        msg.format(envvar=envvar, type_=type_, value=value)
        super(EnvvarValueError, self).__init__(msg)


class EnvvarNameError(EnvvarException):
    """
    Raised when the name of the environment variable is illegal.

    """
    def __init__(self, envvar):
        msg = "envvar names must not start with an underscore: {envvar}"
        msg.format(envvar=envvar)
        super(EnvvarValueError, self).__init__(msg)

class TxeFileIsEncrypted(Exception):
    """
    Raised when trying to access `Txe.source` and the source and byte-code
    sections of the .txe binary have been encrypted.
    """
    pass
