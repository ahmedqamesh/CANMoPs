from ..exceptions import DllException
from .enums import Error

KVD_ERROR_MESSAGES = {
    0: 'OK - no error.',
    Error.FAIL: 'General failure.',
    Error.NO_DATABASE: 'No database was found.',
    Error.PARAM: 'One or more of the parameters in call is erronous.',
    Error.NO_MSG: 'No message was found. ',
    Error.NO_SIGNAL: 'No signal was found.',
    Error.INTERNAL: 'An internal error occured in the library.',
    Error.DB_FILE_OPEN: 'Could not open the database file.',
    Error.DATABASE_INTERNAL:
        'An internal error occured in the database handler.',
    Error.NO_NODE: 'Could not find the database node.',
    Error.NO_ATTRIB: 'No attribute found.',
    Error.ONLY_ONE_ALLOWED: 'Only one such structure is allowed.',
    Error.WRONG_OWNER: 'Wrong owner for attribute.',
}

assert all(err in KVD_ERROR_MESSAGES for err in Error), (
    "Not all kvadblib error codes have messages defined!")

_all_errors_by_status = {}


def _remember(cls):
    _all_errors_by_status[cls.status] = cls
    return cls


def kvd_error(status):
    """Create and return an exception object corresponding to `status`"""
    if status in _all_errors_by_status:
        return _all_errors_by_status[status]()
    else:
        return KvdGeneralError(status)


class KvdError(DllException):
    @staticmethod
    def _get_error_text(status):
        try:
            status = Error(status)
        except ValueError:
            msg = 'Unknown error text'
        else:
            msg = KVD_ERROR_MESSAGES[status]
        msg += ' (%d)' % status
        return msg


class KvdGeneralError(KvdError):
    """A kvadblib error that does not (yet) have its own Exception

    WARNING: Do not explicitly catch this error, instead catch `KvdError`. Your
    error may at any point in the future get its own exception class, and so
    will no longer be of this type. The actual status code that raised any
    `KvdError` can always be accessed through a `status` attribute.

    """

    def __init__(self, status):
        self.status = status
        super(KvdGeneralError, self).__init__()


@_remember
class KvdErrInParameter(KvdError):
    status = Error.PARAM


class KvdNotFound(KvdError):
    pass


@_remember
class KvdNoAttribute(KvdNotFound):
    status = Error.NO_ATTRIB


@_remember
class KvdNoMessage(KvdNotFound):
    status = Error.NO_MSG


@_remember
class KvdNoNode(KvdNotFound):
    status = Error.NO_NODE

@_remember
class KvdNoSignal(KvdNotFound):
    status = Error.NO_SIGNAL


@_remember
class KvdWrongOwner(KvdNotFound):
    status = Error.WRONG_OWNER


@_remember
class KvdOnlyOneAllowed(KvdError):
    status = Error.ONLY_ONE_ALLOWED
