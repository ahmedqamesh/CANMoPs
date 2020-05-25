"""Wrapper for the Kvaser kvaDbLib library

A CAN database contains information about messages. Each message has (among
other attributes) an identifier, a name and one or several signals. The
kvaDbLib library is an API for these CAN databases.

"""

from .attribute import Attribute
from .attributedef import DefaultDefinition, EnumDefaultDefinition, MinMaxDefinition
from .attributedef import AttributeDefinition, FloatDefinition, IntegerDefinition
from .attributedef import StringDefinition, EnumDefinition
from .dbc import Dbc, DATABASE_FLAG_J1939
from .constants import *
from .enums import AttributeOwner, AttributeType, ProtocolType, SignalByteOrder
from .enums import SignalMultiplexMode, SignalType, Error, MessageFlag
from .exceptions import KvdError, KvdErrInParameter, KvdNoAttribute, KvdNoMessage, KvdNoNode, KvdNotFound, KvdWrongOwner, KvdOnlyOneAllowed
from .framebox import FrameBox
from .bound_message import BoundMessage
from .bound_signal import BoundSignal
from .message import Message
from .node import Node
from .signal import ValueLimits, ValueScaling, ValueSize, Signal, EnumSignal
from .wrapper import bytes_to_dlc, dlc_to_bytes, get_protocol_properties, dllversion
