from ..cenum import CEnum, CFlag


class Error(CEnum):
    PARAM = -1
    NOMSG = -2
    NOTFOUND = -3
    NOCHANNELS = -5
    TIMEOUT = -7
    INVHANDLE = -10
    TXBUFOFL = -13
    NOCARD = -26
    SCRIPT_FAIL = -39
    NOT_IMPLEMENTED = -32


class Open(CFlag):
    # canOpen_xxx
    EXCLUSIVE = 0x0008
    REQUIRE_EXTENDED = 0x0010
    ACCEPT_VIRTUAL = 0x0020
    OVERRIDE_EXCLUSIVE = 0x0040
    REQUIRE_INIT_ACCESS = 0x0080
    NO_INIT_ACCESS = 0x0100
    ACCEPT_LARGE_DLC = 0x0200
    CAN_FD = 0x0400
    CAN_FD_NONISO = 0x0800


class IOControlItem(CEnum):
    PREFER_EXT = 1
    PREFER_STD = 2
    CLEAR_ERROR_COUNTERS = 5
    SET_TIMER_SCALE = 6
    SET_TXACK = 7
    GET_RX_BUFFER_LEVEL = 8
    GET_TX_BUFFER_LEVEL = 9
    FLUSH_RX_BUFFER = 10
    FLUSH_TX_BUFFER = 11
    GET_TIMER_SCALE = 12
    SET_TXRQ = 13
    GET_EVENTHANDLE = 14
    SET_BYPASS_MODE = 15
    SET_WAKEUP = 16
    GET_DRIVERHANDLE = 17
    MAP_RXQUEUE = 18
    GET_WAKEUP = 19
    SET_REPORT_ACCESS_ERRORS = 20
    GET_REPORT_ACCESS_ERRORS = 21
    CONNECT_TO_VIRTUAL_BUS = 22
    DISCONNECT_FROM_VIRTUAL_BUS = 23
    SET_USER_IOPORT = 24
    GET_USER_IOPORT = 25
    SET_BUFFER_WRAPAROUND_MODE = 26
    SET_RX_QUEUE_SIZE = 27
    SET_USB_THROTTLE = 28
    GET_USB_THROTTLE = 29
    SET_BUSON_TIME_AUTO_RESET = 30
    GET_TXACK = 31
    SET_LOCAL_TXECHO = 32
    SET_ERROR_FRAMES_REPORTING = 33
    GET_CHANNEL_QUALITY = 34
    GET_ROUNDTRIP_TIME = 35
    GET_BUS_TYPE = 36
    GET_DEVNAME_ASCII = 37
    GET_TIME_SINCE_LAST_SEEN = 38
    GET_TREF_LIST = 39
    TX_INTERVAL = 40
    SET_THROTTLE_SCALED = 41
    GET_THROTTLE_SCALED = 42
    SET_BRLIMIT = 43
    RESET_OVERRUN_COUNT = 44
    LIN_MODE = 45


class ChannelDataItem(CEnum):
    CHANNEL_CAP = 1
    TRANS_CAP = 2
    CHANNEL_FLAGS = 3
    CARD_TYPE = 4
    CARD_NUMBER = 5
    CHAN_NO_ON_CARD = 6
    CARD_SERIAL_NO = 7
    TRANS_SERIAL_NO = 8
    CARD_FIRMWARE_REV = 9
    CARD_HARDWARE_REV = 10
    CARD_UPC_NO = 11
    TRANS_UPC_NO = 12
    CHANNEL_NAME = 13
    DLL_FILE_VERSION = 14
    DLL_PRODUCT_VERSION = 15
    DLL_FILETYPE = 16
    TRANS_TYPE = 17
    DEVICE_PHYSICAL_POSITION = 18
    UI_NUMBER = 19
    TIMESYNC_ENABLED = 20
    DRIVER_FILE_VERSION = 21
    DRIVER_PRODUCT_VERSION = 22
    MFGNAME_UNICODE = 23
    MFGNAME_ASCII = 24
    DEVDESCR_UNICODE = 25
    DEVDESCR_ASCII = 26
    DRIVER_NAME = 27
    CHANNEL_QUALITY = 28
    ROUNDTRIP_TIME = 29
    BUS_TYPE = 30
    DEVNAME_ASCII = 31
    TIME_SINCE_LAST_SEEN = 32
    REMOTE_OPERATIONAL_MODE = 33
    REMOTE_PROFILE_NAME = 34
    REMOTE_HOST_NAME = 35
    REMOTE_MAC = 36
    MAX_BITRATE = 37
    CHANNEL_CAP_MASK = 38
    CUST_CHANNEL_NAME = 39
    IS_REMOTE = 40
    REMOTE_TYPE = 41
    LOGGER_TYPE = 42
    HW_STATUS = 43
    FEATURE_EAN = 44


class Stat(CFlag):
    """canSTAT_xxx

    The following circuit status flags are returned by canReadStatus(). Note
    that more than one flag might be set at any one time.

    Note:

        Usually both canSTAT_HW_OVERRUN and canSTAT_SW_OVERRUN are set when
        overrun has occurred. This is because the kernel driver can't see the
        difference between a software overrun and a hardware overrun. So the
        code should always test for both types of overrun using the flag.

    """
    ERROR_PASSIVE = 0x00000001  # The circuit is error passive
    BUS_OFF = 0x00000002  # The circuit is Off Bus
    ERROR_WARNING = 0x00000004  # At least one error counter > 96
    ERROR_ACTIVE = 0x00000008  # The circuit is error active.
    TX_PENDING = 0x00000010  # There are messages pending transmission
    RX_PENDING = 0x00000020  # There are messages in the receive buffer
    RESERVED_1 = 0x00000040
    TXERR = 0x00000080  # There has been at least one TX error
    RXERR = 0x00000100  # There has been at least one RX error of some sort
    HW_OVERRUN = 0x00000200  # There has been at least one HW buffer overflow
    SW_OVERRUN = 0x00000400  # There has been at least one SW buffer overflow
    OVERRUN = (HW_OVERRUN | SW_OVERRUN)  # For convenience.


class MessageFlag(CFlag):
    """Message information flags

    The following flags can be returned from canRead() et al, or passed to
    canWrite().

    This enum is a combination of flags for messages, CAN FD messages, and
    message errors. Normal messages flags are the flags covered by `MSG_MASK`,
    CAN FD message flags are those covered by `FDMSG_MASK`, and message errors
    are those covered by `MSGERR_MASK`.

    Note:
        `FDF`, `BRS`, and `ESI` require CAN FD.

        `RTR` cannot be set for CAN FD messages.

        Not all hardware platforms can detect the difference between hardware
        overruns and software overruns, so your application should test for
        both conditions. You can use the symbol `OVERRUN` for this
        purpose.

    """
    # canMSG_xxx
    MSG_MASK = 0x00ff
    RTR = 0x0001
    STD = 0x0002
    EXT = 0x0004
    WAKEUP = 0x0008
    NERR = 0x0010
    ERROR_FRAME = 0x0020
    TXACK = 0x0040
    TXRQ = 0x0080

    # canFDMSG_xxx
    FDMSG_MASK = 0xff0000  # obsolete
    EDL = 0x010000  # obsolete
    FDF = 0x010000
    BRS = 0x020000
    ESI = 0x040000

    # canMSGERR_xxx
    MSGERR_MASK = 0xff00
    HW_OVERRUN = 0x0200
    SW_OVERRUN = 0x0400
    STUFF = 0x0800
    FORM = 0x1000
    CRC = 0x2000
    BIT0 = 0x4000
    BIT1 = 0x8000
    OVERRUN = 0x0600
    BIT = 0xC000
    BUSERR = 0xF800


class Driver(CEnum):
    NORMAL = 4
    SILENT = 1
    SELFRECEPTION = 8
    OFF = 0


class ScriptStop(CEnum):
    NORMAL = 0
    FORCED = -9

class TxeDataItem(CEnum):
    FILE_VERSION = 1
    COMPILER_VERSION = 2
    DATE = 3
    DESCRIPTION = 4
    SOURCE = 5
    SIZE_OF_CODE = 6
    IS_ENCRYPTED = 7

class DeviceMode(CEnum):
    # kvDEVICE_MODE_xxx
    INTERFACE = 0
    LOGGER = 1


class EnvVarType(CEnum):
    INT = 1
    FLOAT = 2
    STRING = 3


class AcceptFilterFlag(CEnum):
    """canFILTER_SET_xxx"""
    # Flags for canAccept().
    SET_CODE_STD = 3
    SET_MASK_STD = 4
    SET_CODE_EXT = 5
    SET_MASK_EXT = 6
    NULL_MASK = 0


class LEDAction(CEnum):
    """kvLED_ACTION_xxx

    The following can be used together with `canlib.canlib.Channel.flashLeds`.

    """
    ALL_LEDS_ON = 0   #: Turn all LEDs on.
    ALL_LEDS_OFF = 1   #: Turn all LEDs off.
    LED_0_ON = 2   #: Turn LED 0 on.
    LED_0_OFF = 3   #: Turn LED 0 off.
    LED_1_ON = 4   #: Turn LED 1 on.
    LED_1_OFF = 5   #: Turn LED 1 off.
    LED_2_ON = 6   #: Turn LED 2 on.
    LED_2_OFF = 7   #: Turn LED 2 off.
    LED_3_ON = 8   #: Turn LED 3 on.
    LED_3_OFF = 9   #: Turn LED 3 off.


class TransceiverType(CEnum):
    """Transceiver (logical) types

    The following constants can be returned from canGetChannelData(), using the
    canCHANNELDATA_TRANS_TYPE item code. They identify the bus transceiver type
    for the channel specified in the call to canGetChannelData.

    Note:

        If the type starts with a number ``T_`` has been prepended to the name.

        They indicate a hardware type, but not necessarily a specific circuit
        or product.

    """
    UNKNOWN = 0
    T_251 = 1
    T_252 = 2
    DNOPTO = 3
    W210 = 4
    SWC_PROTO = 5
    SWC = 6
    EVA = 7
    FIBER = 8
    K251 = 9
    K = 10  # K-line, without CAN.
    T_1054_OPTO = 11
    SWC_OPTO = 12
    TT = 13
    T_1050 = 14
    T_1050_OPTO = 15
    T_1041 = 16
    T_1041_OPTO = 17
    RS485 = 18
    LIN = 19
    KONE = 20
    CANFD = 22
    CANFD_LIN = 24
    LINX_LIN = 64
    LINX_J1708 = 66
    LINX_K = 68
    LINX_SWC = 70
    LINX_LS = 72


class ChannelFlags(CFlag):
    """canCHANNEL_IS_xxx

    These channelFlags are used in `Channel.getChannelData` and in conjunction with
    `ChannelDataItem.CHANNEL_FLAGS`.

    """
    IS_EXCLUSIVE = 0x0001
    IS_OPEN = 0x0002
    IS_CANFD = 0x0004
    IS_LIN = 0x0010
    IS_LIN_MASTER = 0x0020
    IS_LIN_SLAVE = 0x0040


class BusTypeGroup(CEnum):
    """kvBUSTYPE_GROUP_xxx

    Bus type group.

    """
    VIRTUAL = 1
    LOCAL = 2
    REMOTE = 3
    INTERNAL = 4


class HardwareType(CEnum):
    """canHWTYPE_xxx

    The following constants can be returned from canGetChannelData(), using
    the canCHANNELDATA_CARD_TYPE item code. They identify the hardware type
    for the channel specified in the call to canGetChannelData().

    Note:

        The members indicate a hardware type, but not necessarily a specific
        product. For example, canHWTYPE_LAPCAN is returned both for LAPcan and
        LAPcan II. (You can use canGetChannelData() to obtain the UPC/EAN code
        for the device. This number uniquely identifies the product.)

    """
    NONE = 0  # Unknown or undefined.
    VIRTUAL = 1  # The virtual CAN bus.
    LAPCAN = 2  # LAPcan Family.
    PCCAN = 8  # PCcan Family.
    PCICAN = 9  # PCIcan Family.
    PCICAN_II = 40  # PCIcan II family.
    USBCAN_II = 42  # USBcan II, USBcan Rugged, Kvaser Memorator.
    LEAF = 48  # Kvaser Leaf Family.
    PC104_PLUS = 50  # Kvaser PC104+.
    PCICANX_II = 52  # Kvaser PCIcanx II.
    MEMORATOR_II = 54  # Kvaser Memorator Professional family.
    MEMORATOR_PRO = 54  # Kvaser Memorator Professional family.
    USBCAN_PRO = 56  # Kvaser USBcan Professional.
    BLACKBIRD = 58  # Kvaser BlackBird.
    MEMORATOR_LIGHT = 60  # Kvaser Memorator Light.
    EAGLE = 62  # Kvaser Eagle family.
    BLACKBIRD_V2 = 64  # Kvaser BlackBird v2.
    MINIPCIE = 66  # Kvaser Mini PCI Express.
    USBCAN_KLINE = 68  # USBcan Pro HS/K-Line.
    ETHERCAN = 70  # Kvaser Ethercan.
    USBCAN_LIGHT = 72  # Kvaser USBcan Light.
    USBCAN_PRO2 = 74  # Kvaser USBcan Pro 5xHS and variants.
    PCIE_V2 = 76  # Kvaser PCIEcan 4xHS and variants.
    MEMORATOR_PRO2 = 78  # Kvaser Memorator Pro 5xHS and variants.
    LEAF2 = 80  # Kvaser Leaf Pro HS v2 and variants.
    MEMORATOR_V2 = 82  # Kvaser Memorator (2nd generation)
    CANLINHYBRID = 84  # Kvaser Hybrid CAN/LIN.

    # Obsolete
    CANPARI = 3  # CANpari (obsolete).
    USBCAN = 11  # USBcan (obsolete).
    SIMULATED = 44  # Simulated CAN bus for Kvaser Creator (obsolete).
    ACQUISITOR = 46  # Kvaser Acquisitor (obsolete).
    IRIS = 58  # Obsolete name, use BLACKBIRD instead.
    MINIHYDRA = 62  # Obsolete name, use EAGLE instead.
    BAGEL = 64  # Obsolete name, use BLACKBIRD_V2 instead.


class ChannelCap(CFlag):
    """canCHANNEL_CAP_xxx

    Channel capabilities.

    """
    EXTENDED_CAN = 0x00000001  # Can use extended identifiers.
    BUS_STATISTICS = 0x00000002  # Can report busload etc.
    ERROR_COUNTERS = 0x00000004  # Can return error counters.
    CAN_DIAGNOSTICS = 0x00000008  # Can report CAN diagnostics.
    GENERATE_ERROR = 0x00000010  # Can send error frames.
    GENERATE_OVERLOAD = 0x00000020  # Can send CAN overload frame.
    TXREQUEST = 0x00000040  # Can report when a CAN messsage transmission is initiated.
    TXACKNOWLEDGE = 0x00000080  # Can report when a CAN messages has been transmitted.
    VIRTUAL = 0x00010000  # Virtual CAN channel.
    SIMULATED = 0x00020000  # Simulated CAN channel.
    RESERVED_1 = 0x00040000  # Obsolete, use canCHANNEL_CAP_REMOTE_ACCESS or canGetChannelData() instead.
    CAN_FD = 0x00080000  # CAN-FD ISO compliant channel.
    CAN_FD_NONISO = 0x00100000  # CAN-FD NON-ISO compliant channel.
    SILENT_MODE = 0x00200000  # Channel supports Silent mode.
    SINGLE_SHOT = 0x00400000  # Channel supports Single Shot messages.
    LOGGER = 0x00800000  # Channel has logger capabilities.
    REMOTE_ACCESS = 0x01000000  # Channel has remote capabilities.
    SCRIPT = 0x02000000  # Channel has script capabilities.


class LoggerType(CEnum):
    """kvLOGGER_TYPE_xxx

    Logger type, returned when using canCHANNELDATA_LOGGER_TYPE

    """
    NOT_A_LOGGER = 0
    V1 = 1
    V2 = 2


class OperationalMode(CEnum):
    """canCHANNEL_OPMODE_xxx

    Current WLAN operational mode.

    """
    NONE = 1
    INFRASTRUCTURE = 2
    RESERVED = 3
    ADH = 4


class RemoteType(CEnum):
    """kvREMOTE_TYPExxx

    Remote type, returned when using canCHANNELDATA_REMOTE_TYPE
    """
    NOT_REMOTE = 0
    WLAN = 1
    LAN = 2


class DriverCap(CEnum):
    """canDRIVER_CAP_xxx

    Driver (transceiver) capabilities.
    """
    HIGHSPEED = 0x00000001


class VersionEx(CEnum):
    VERSION = 0
    PRODVER = 1
    PRODVER32 = 2
    BETA = 3
