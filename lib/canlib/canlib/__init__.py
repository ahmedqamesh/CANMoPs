"""Wrapper for the Kvaser CANlib library

At the core of canlib you have functions to set bus parameters (e.g. bit rate),
go bus on/off and read/write CAN messages. You can also use CANlib to download
and start t programs on your device. All of this is done on a device that is
attached to your computer, and they are universally available across all
supported Kvaser Devices. If you can see your device listed in the Kvaser
Hardware tool, it is connected and you can communicate with it through CANlib.

"""


from ._channel import canChannel
from .channel import Channel, openChannel
from .channeldata import ChannelData
from .constants import *
from .envvar import EnvVar
from .enums import Error, Open, IOControlItem, ChannelDataItem, Stat, MessageFlag
from .enums import Driver, ScriptStop, DeviceMode, EnvVarType
from .enums import AcceptFilterFlag, LEDAction, TransceiverType
from .enums import ChannelFlags, BusTypeGroup, HardwareType, ChannelCap
from .enums import LoggerType, OperationalMode, RemoteType, DriverCap
from .enums import TxeDataItem
from .exceptions import EnvvarException, EnvvarValueError, EnvvarNameError
from .exceptions import CanError, CanNoMsg, CanScriptFail, CanNotFound, TxeFileIsEncrypted
from .iocontrol import IOControl
from .txe import Txe, SourceElement
from .wrapper import CANLib, bitrateSetting
from .wrapper import getErrorText, getVersion, dllversion, getNumberOfChannels, getChannelData_Channel_Flags
from .wrapper import getChannelData_Name, getChannelData_Cust_Name, getChannelData_Chan_No_On_Card
from .wrapper import getChannelData_CardNumber, getChannelData_EAN, getChannelData_EAN_short, getChannelData_Serial
from .wrapper import getChannelData_DriverName, getChannelData_Firmware, translateBaud
from .wrapper import unloadLibrary, initializeLibrary, reinitializeLibrary

from .wrapper import CANLib as canlib  # for backwards-compatibility
from .envvar import EnvVar as envvar  # for backwards-compatibility
from .wrapper import ChannelData_Channel_Flags_bits, ChannelData_Channel_Flags  # deprecated


canError = CanError
canNoMsg = CanNoMsg
canScriptFail = CanScriptFail
