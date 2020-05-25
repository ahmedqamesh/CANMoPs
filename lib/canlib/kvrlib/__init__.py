"""Wrapper for the Kvaser kvrlib library

Some Kvaser devices, known as remote devices, can be connected via Ethernet
(E.g. Kvaser Ethercan Light HS and Kvaser BlackBird v2) and you need to
configure those devices before they are connected to your computer. This is
where kvrlib comes into play with functions to discover and connect to a Kvaser
Device on the network, making it accessible for the CANlib functions. The
kvrlib also has functions to configure how the remote device connects to the
network (e.g. dynamic/static IP). It also contains extra functions for wireless
setup, such as scanning and getting connection status.

"""

from .constants import *
from .discovery import start_discovery, Discovery, openDiscovery, Address, DeviceInfo, ServiceStatus
from .discovery import get_default_discovery_addresses, set_clear_stored_devices_on_exit
from .discovery import store_devices, stored_devices
from .enums import DeviceUsage, Accessibility, Availability, Error, NetworkState
from .enums import BasicServiceSet, RegulatoryDomain, RemoteState, AddressTypeFlag, AddressType
from .enums import ServiceState, StartInfo, ConfigMode
from .exceptions import KvrError, KvrBlank
from .infoset import stored_info_set, empty_info_set, discover_info_set, DeviceInfoSet, DeviceNotInSetError
from .remotedevice import RemoteDevice, openDevice, ConfigProfile
from .remotedevice import AddressInfo, ConnectionStatus, ConnectionTestResult, WlanScanResult
from .remotedevice import ConnectionTest, WlanScan
from .structures import kvrAddress, kvrAddressList, kvrDeviceInfo, kvrDeviceInfoList, kvrVersion
from .wrapper import kvrConfig, kvrDiscovery, KvrLib
from .wrapper import addressFromString, stringFromAddress
from .wrapper import ean2ean_hi, ean2ean_lo, ean_hi_lo2ean
from .wrapper import deviceGetServiceStatus, deviceGetServiceStatusText
from .wrapper import configActiveProfileSet, configActiveProfileGet
from .wrapper import configNoProfilesGet, unload, initializeLibrary, getVersion, dllversion, hostname
from .wrapper import generate_wep_keys, generate_wpa_keys, verify_xml, WEPKeys

from .wrapper import KvrLib as kvrlib

from . import service


# for backwards compatibility
kvrDeviceUsage = DeviceUsage
kvrAccessibility = Accessibility
kvrAvailability = Availability
kvrError = KvrError
kvrBlank = KvrBlank
