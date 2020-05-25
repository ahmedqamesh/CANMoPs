import ctypes as ct

from ..ean import EAN, IllegalEAN
from .. import VersionNumber
from .enums import ChannelFlags, ChannelDataItem, HardwareType, ChannelCap, LoggerType, Error
from .enums import OperationalMode, RemoteType, DriverCap, TransceiverType, BusTypeGroup
from .exceptions import CanNotImplementedError, CanNotFound, CanError
from .wrapper import dll, getNumberOfChannels


ATTRIBUTES = {
    'channel_cap': dict(
        item=ChannelDataItem.CHANNEL_CAP,
        ctype=ct.c_uint32,
        ptype=ChannelCap,
        __doc__="A `ChannelCap` object with the capabilities of the channel as flags. Also see `channel_cap_mask`.",
    ),
    'trans_cap': dict(
        item=ChannelDataItem.TRANS_CAP,
        ctype=ct.c_uint32,
        ptype=DriverCap,
        __doc__="A `DriverCap` object with the capabilities of the transceiver as flags. Not implemented in Linux.",
    ),
    'channel_flags': dict(
        item=ChannelDataItem.CHANNEL_FLAGS,
        ctype=ct.c_uint32,
        ptype=ChannelFlags,
        __doc__="A `ChannelFlags` object with the status of the channel as flags. Not implemented in Linux.",
    ),
    'card_type': dict(
        item=ChannelDataItem.CARD_TYPE,
        ctype=ct.c_uint32,
        ptype=HardwareType,
        __doc__="A member of the `HardwareType` enum representing the hardware type of the card.",
    ),
    'card_number': dict(
        item=ChannelDataItem.CARD_NUMBER,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the card's number in the computer. Each card type is numbered separately.",
    ),
    'chan_no_on_card': dict(
        item=ChannelDataItem.CHAN_NO_ON_CARD,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` of the channel number on the card.",
    ),
    'card_serial_no': dict(
        item=ChannelDataItem.CARD_SERIAL_NO,
        ctype=ct.c_uint64,
        ptype=int,
        __doc__="An `int` with the serial number of the card, or 0 if it doesn't have a serial number.",
    ),
    'trans_serial_no': dict(
        item=ChannelDataItem.TRANS_SERIAL_NO,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the serial number of the transceiver, or 0 if it doesn't have a serial number. Not implemented in Linux.",
    ),
    'card_firmware_rev': dict(
        item=ChannelDataItem.CARD_FIRMWARE_REV,
        ctype=ct.c_uint16 * 4,
        # little byteorder assumed:
        ptype=lambda t: VersionNumber(t[3], t[2], release=t[1], build=t[0]),
        __doc__="A `VersionNumber` object with the version of the card's firmware.",
    ),
    'card_hardware_rev': dict(
        item=ChannelDataItem.CARD_HARDWARE_REV,
        ctype=ct.c_uint16 * 4,
        ptype=lambda t: VersionNumber(t[1], t[0]),  # little byteorder assumed
        __doc__="A `VersionNumber` object with the version of the card's hardware.",
    ),
    'card_upc_no': dict(
        item=ChannelDataItem.CARD_UPC_NO,
        ctype=ct.c_ubyte * 8,
        ptype=EAN.from_bcd,
        __doc__="An `EAN` object with the EAN of the card, or `None` if it doesn't one.",
    ),
    'trans_upc_no': dict(
        item=ChannelDataItem.TRANS_UPC_NO,
        ctype=ct.c_ubyte * 8,
        ptype=EAN.from_bcd,
        __doc__="An `EAN` object with the EAN of the transceiver, or `None` if it doesn't have one. Not implemented in Linux.",
    ),
    # 'channel_name': dict(  # ~deprecated
    #     item=ChannelDataItem.CHANNEL_NAME,
    # ),
    'dll_file_version': dict(
        item=ChannelDataItem.DLL_FILE_VERSION,
        ctype=ct.c_uint16 * 4,
        ptype=lambda t: VersionNumber(t[3], t[2], t[1]),  # little byteorder assumed,
        __doc__="A `VersionNumber` with the version of the dll file. Not implemented in Linux.",
    ),
    'dll_product_version': dict(
        item=ChannelDataItem.DLL_PRODUCT_VERSION,
        ctype=ct.c_uint16 * 4,
        ptype=lambda t: VersionNumber(t[3], t[2]),  # little byteorder assumed,
        __doc__="A `VersionNumber` with the product version of the dll file. Not implemented in Linux.",
    ),
    'dll_filetype': dict(
        item=ChannelDataItem.DLL_FILETYPE,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="1 if \"kvalapw.dll\" is used, 2 if \"kvalapw2.dll\"",
    ),
    'trans_type': dict(
        item=ChannelDataItem.TRANS_TYPE,
        ctype=ct.c_uint32,
        ptype=TransceiverType,
        __doc__="A member of the `TransceiverType` enum.",
    ),
    'device_physical_position': dict(
        item=ChannelDataItem.DEVICE_PHYSICAL_POSITION,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the address of the device on its underlying bus. Not implemented in Linux.",
    ),
    'ui_number': dict(
        item=ChannelDataItem.UI_NUMBER,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the number associated with the device that can be displayed in the user interface. Not implemented in Linux.",
    ),
    'timesync_enabled': dict(
        item=ChannelDataItem.TIMESYNC_ENABLED,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether legacy time synchronization is enabled. Not implemented in Linux.",
    ),
    'driver_file_version': dict(
        item=ChannelDataItem.DRIVER_FILE_VERSION,
        ctype=ct.c_uint16 * 4,
        ptype=lambda t: VersionNumber(t[3], t[2], t[1]),  # little byteorder assumed,
        __doc__="A `VersionNumber` with the version of the kernel-mode driver. Not implemented in Linux.",
    ),
    'driver_product_version': dict(
        item=ChannelDataItem.DRIVER_PRODUCT_VERSION,
        ctype=ct.c_uint16 * 4,
        ptype=lambda t: VersionNumber(t[3], t[2]),  # little byteorder assumed,
        __doc__="A `VersionNumber` with the product version of the kernel-mode driver. Not implemented in Linux.",
    ),
    'mfgname_unicode': dict(
        item=ChannelDataItem.MFGNAME_UNICODE,
        ctype=ct.c_wchar * 80,
        ptype=str,
        __doc__="A `str` with the manufacturer's name. Not implemented in Linux.",
    ),
    'mfgname_ascii': dict(
        item=ChannelDataItem.MFGNAME_ASCII,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the manufacturer's name.",
    ),
    'devdescr_unicode': dict(
        item=ChannelDataItem.DEVDESCR_UNICODE,
        ctype=ct.c_wchar * 80,
        ptype=str,
        __doc__="A `str` with the product name of the device. Not implemented in Linux.",
    ),
    'devdescr_ascii': dict(
        item=ChannelDataItem.DEVDESCR_ASCII,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the product name of the device.",
    ),
    'driver_name': dict(
        item=ChannelDataItem.DRIVER_NAME,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the name of the device driver.",
    ),
    'channel_quality': dict(
        item=ChannelDataItem.CHANNEL_QUALITY,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` between 0 and 100 (inclusively) with the quality of the channel in percent of optimal quality. Not implemented in Linux.",
    ),
    'roundtrip_time': dict(
        item=ChannelDataItem.ROUNDTRIP_TIME,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the roundtrip time measured in milliseconds. Not implemented in Linux.",
    ),
    'bus_type': dict(
        item=ChannelDataItem.BUS_TYPE,
        ctype=ct.c_uint32,
        ptype=BusTypeGroup,
        __doc__="A member of the `BusTypeGroup` enum. Not implemented in Linux.",
    ),
    'devname_ascii': dict(
        item=ChannelDataItem.DEVNAME_ASCII,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the current device name. Not implemented in Linux.",
    ),
    'time_since_last_seen': dict(
        item=ChannelDataItem.TIME_SINCE_LAST_SEEN,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the time in milliseconds since last communication occured. Not implemented in Linux.",
    ),
    'remote_operational_mode': dict(
        item=ChannelDataItem.REMOTE_OPERATIONAL_MODE,
        ctype=ct.c_uint32,
        ptype=OperationalMode,
        __doc__="A member of the `OperationalMode` enum. Not implemented in Linux.",
    ),
    'remote_profile_name': dict(
        item=ChannelDataItem.REMOTE_PROFILE_NAME,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the remote profile name of the device. Not implemented in Linux.",
    ),
    'remote_host_name': dict(
        item=ChannelDataItem.REMOTE_HOST_NAME,
        ctype=ct.c_char * 80,
        ptype=str,
        __doc__="A `str` with the remote host name of the device. Not implemented in Linux.",
    ),
    'remote_mac': dict(
        item=ChannelDataItem.REMOTE_MAC,
        ctype=ct.c_char * 32,
        ptype=str,
        __doc__="A `str` with the remote mac address of the device. Not implemented in Linux.",
    ),
    'max_bitrate': dict(
        item=ChannelDataItem.MAX_BITRATE,
        ctype=ct.c_uint32,
        ptype=int,
        __doc__="An `int` with the maximum bitrate of the device. Zero means no limit on the bitrate.",
    ),
    'channel_cap_mask': dict(
        item=ChannelDataItem.CHANNEL_CAP_MASK,
        ctype=ct.c_uint32,
        ptype=ChannelCap,
        __doc__="A `ChannelCap` with which flags this device knows about.",
    ),
    'is_remote': dict(
        item=ChannelDataItem.IS_REMOTE,
        ctype=ct.c_uint32,
        ptype=bool,
        __doc__="A `bool` for whether the device is currently connected as a remote device. Not implemented in Linux.",
    ),
    'remote_type': dict(
        item=ChannelDataItem.REMOTE_TYPE,
        ctype=ct.c_uint32,
        ptype=RemoteType,
        __doc__="A member of the `RemoteType` enum. Not implemented in Linux.",
    ),
    'logger_type': dict(
        item=ChannelDataItem.LOGGER_TYPE,
        ctype=ct.c_uint32,
        ptype=LoggerType,
        __doc__="A member of the `LoggerType` enum. Not implemented in Linux.",
    ),
    # 'hw_status': dict(  # internal
    #     item=ChannelDataItem.HW_STATUS,
    # ),
    # 'feature_ean': dict(
    #     item=ChannelDataItem.FEATURE_EAN,
    # ),
}


class ChannelData(object):
    __doc__ = """Object for querying various information about a channel

    After instantiating a `ChannelData` object with a channel number, a variety
    of information is available as attributes. Most attributes are named after
    the C constant used to retrieve the information and are found in the list
    below.

    Other information does not follow the C implementation completely, and are
    documented as separate properties further down.

    There is also the `raw` function, that is used internally to get all
    information and can also be used to interact more directly with the dll.

    Attributes:
{dyn_attrs}
    """.format(
        dyn_attrs='\n'.join(
            '        ' + name + ': ' + d['__doc__']
            for name, d in sorted(ATTRIBUTES.items())
        )
    )

    def __init__(self, channel_number):
        self.channel_number = channel_number

    def __getattr__(self, name):
        try:
            attr = ATTRIBUTES[name]
        except KeyError:
            raise AttributeError("{cls} object has no attribute {name}".format(
                cls=self.__class__.__name__, name=name))

        item = attr['item']
        ctype = attr['ctype']
        ptype = attr['ptype']

        ret = self.raw(item=item, ctype=ctype)
        if ptype:
            if ptype is str and isinstance(ret, bytes):
                ret = ret.decode('utf8')
            else:
                # In python 2, we get `long` and not `int` resulting in ValueError :(
                try:
                    ret = ptype(ret)
                except ValueError as orig_e:
                    try:
                        ret = ptype(int(ret))
                    except Exception:
                        raise orig_e
        return ret

    def raw(self, item, ctype=ct.c_uint32):
        """A raw call to `canGetChannelData`

        Args:
            item (`ChannelDataItem`): The information to be retrieved.
            ctype: The `ctypes` type that the information should be interpreted as.

        """
        buf = ctype()
        try:
            dll.canGetChannelData(
                self.channel_number,
                item,
                ct.byref(buf),
                ct.sizeof(buf),
            )
        except CanError as e:
            # On windows and CANlib < 5.23 Error.PARAM is returned instead of CanNotFound
            if e.status == Error.PARAM and self.channel_number >= getNumberOfChannels():
                raise CanNotFound
            else:
                raise e
        try:
            return buf.value
        except AttributeError:
            return tuple(buf)

    @property
    def device_name(self):
        """`str`: The product name.

        Retrieves the product name of the device connected to channel. The name
        is returned as a string.

        """
        name = self.devdescr_ascii
        no_on_card = self.chan_no_on_card
        return "%s (channel %d)" % (name, no_on_card)

    @property
    def custom_name(self):
        """`str`: The custom channel name if set, or an empty string otherwise"""
        try:
            ret = self.raw(
                item=ChannelDataItem.CUST_CHANNEL_NAME, ctype=ct.c_char * 64
            ).decode('utf8')
        except CanNotImplementedError:
            ret = ""

        return ret
