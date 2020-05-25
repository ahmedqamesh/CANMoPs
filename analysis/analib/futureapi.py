"""futureapi -- module for handling functions not necessarily present

This module defines a number of function with the same name as a C function
newly added to one of the CANlib dlls. When `dllLoader.MyDll` can't find a
foreign function specified in a ``function_prototypes``, it consults this
module; if a function with an identical name exists in this module that
function will be used instead.

This allows us to essentially monkey-patch our C dlls.

Each function needs to have an identical name to the C function it is supposed
to patch and should for clarity's sake have the same arguments. It should also
immediately raise `NotYetSupportedError` (defined in this module) with a
message saying what is not yet supported and when (what version) it will be
supported.

"""
from .exceptions import CanlibException


class NotYetSupportedError(CanlibException, NotImplementedError):
    """An operation that is not yet supported by the loaded dll was attempted
    """
    pass


def linGetVersion(major, minor, build):
    raise NotYetSupportedError(
        "Accessing LINlib version requires CANlib SDK v5.23 or newer.")


def kvaDbGetAttributeByName(dh, attrName, ah):
    raise NotYetSupportedError(
        "Reading database attributes (by name) requires CANlib SDK v5.23 or newer.")


def kvaDbGetFirstAttribute(dh, nah):
    raise NotYetSupportedError(
        "Reading database attributes requires CANlib SDK v5.23 or newer.")


def kvaDbAddAttribute(dh, adh, ah):
    raise NotYetSupportedError(
        "Adding database attribute requires CANlib SDK v5.23 or newer.")


def kvaDbDeleteAttribute(dh, ah):
    raise NotYetSupportedError(
        "Deleting database attribute requires CANlib SDK v5.23 or newer.")


def kvScriptTxeGetData(*args):
    raise NotYetSupportedError(
        "Accessing CANlib kvScriptTxeGetData requires CANlib SDK v5.23 or newer.")


def canGetVersionEx(itemCode):
    raise NotYetSupportedError(
        "Accessing canGetVersionEx in Linux requires CANlib SDK v5.23 or newer.")


def kvaDbGetAttributeDefinitionEnumFirst(adh, eValue, eName, buflen):
    raise NotYetSupportedError(
        "Accessing kvadblib kvaDbGetAttributeDefinitionEnumFirst requires CANlib SDK v5.23 or newer.")


def kvaDbGetAttributeDefinitionEnumNext(adh, eValue, eName, buflen):
    raise NotYetSupportedError(
        "Accessing kvadblib kvaDbGetAttributeDefinitionEnumNext requires CANlib SDK v5.23 or newer.")
