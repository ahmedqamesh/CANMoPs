import ctypes as ct
import struct
import weakref

from ..frame import Frame
from .. import deprecation
from . import constants as const
from . import wrapper
from .iocontrol import IOControl
from .enums import MessageFlag, DeviceMode, Open
from .envvar import EnvVar
from .exceptions import CanError

dll = wrapper.dll


def openChannel(channel, flags=0, bitrate=None, data_bitrate=None):
    """Open CAN channel

    Retrieves a canChannel object for the given CANlib channel number using
    the supplied flags.

    Args:
        channel (int): CANlib channel number
        flags (int): Flags, a combination of the `canlib.canlib.Open` flag values.
            Default is zero, i.e. no flags.

    Returns:
        A canChannel object created with channel and flags

    .. versionadded:: 1.6
       The `bitrate` and `data_bitrate` arguments.

    """
    ch = Channel(channel, flags)
    if bitrate is not None:
        ch.setBusParams(bitrate)
    if flags & Open.CAN_FD or flags & Open.CAN_FD_NONISO:
        if data_bitrate is not None:
            ch.setBusParamsFd(data_bitrate)
        elif bitrate is not None:
            ch.setBusParamsFd(bitrate)
    else:
        if data_bitrate is not None:
            raise ValueError("data_bitrate requires CAN FD flag")

    return ch


class Channel(object):
    """Helper class that represents a CANlib channel.

    This class wraps the canlib class and tries to implement a more Pythonic
    interface to CANlib.

    Channels are automatically closed on garbage collection, and can
    also be used as context managers in which case they close as soon as the
    context exits.

    """
    _iocontrol_ref = lambda self: None  # noqa
    _MAX_MSG_SIZE = 64

    def __init__(self, channel_number, flags=0):
        self.index = channel_number
        self.handle = dll.canOpenChannel(channel_number, flags)
        self.envvar = EnvVar(self)
        self.flags = flags

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except CanError:
            # For some reason, in python 2 we get "Handle is invalid (-10)
            # here. Probably something to do with the unpredictable way
            # __del__ is called.
            pass

    def _calculate_length(self, dlc, message_flags):
        if message_flags & MessageFlag.FDF:
            length = dlc
        else:
            length = min(8, dlc)
        return length

    @property
    def iocontrol(self):
        """`IOControl`: ``canIoCtl`` helper object for this channel

        See the documentation for `IOControl` for how it can be used to perform
        all functionality of the C function ``canIoCtl``.

        """
        # Because handles are only closed on garbage collection, a weak
        # reference is used to prevent a cyclic reference that would delay
        # garbage collection (in CPython). As a side effect, the iocontrol
        # objects are optimized to only stay alive while someone needs them.
        ioc = self._iocontrol_ref()
        if ioc is None:
            ioc = IOControl(self)
            self._iocontrol_ref = weakref.ref(ioc)

        return ioc

    def close(self):
        """Close CANlib channel

        Closes the channel associated with the handle. If no other threads are
        using the CAN circuit, it is taken off bus.

        Note:

            It is normally not necessary to call this function directly, as the
            internal handle is automatically closed when the `Channel` object
            is garbage collected.

        """
        if self.handle != -1:
            dll.canClose(self.handle)
            self.handle = -1

    def canAccept(self, envelope, flag):
        """Set acceptance filters mask or code.

        This routine sets the message acceptance filters on a CAN channel.

        Setting flag to `canlib.canlib.AcceptFilterFlag.NULL_MASK` (0) removes the filter.

        Note that not all CAN boards support different masks for standard and
        extended CAN identifiers.

        Args:
            envelope:  The mask or code to set.
            flag:      Any of `canlib.canlib.AcceptFilterFlag`
        """
        dll.canAccept(self.handle, envelope, flag)

    def canSetAcceptanceFilter(self, code, mask, is_extended=False):
        """Set message acceptance filter.

        This routine sets the message acceptance filters on a CAN channel.
        The message is accepted if 'id AND mask == code' (this is actually
        imlepemented as if ((code XOR id) AND mask) == 0).

        Using standard 11-bit CAN identifiers and setting
        mask = 0x7f0,
        code = 0x080
        accepts CAN messages with standard id 0x080 to 0x08f.

        Setting the mask to canFILTER_NULL_MASK (0) removes the filter.

        Note that not all CAN boards support different masks for standard and
        extended CAN identifiers.

        Args:
            mask (int): A bit mask that indicates relevant bits with '1'.
            code (int): The expected state of the masked bits.
            is_extended (Boolean): If true, both mask and code applies
                to 29-bit CAN identifiers.
        """
        dll.canSetAcceptanceFilter(self.handle, code, mask, is_extended)

    def setBusParams(self, freq, tseg1=0, tseg2=0, sjw=0, noSamp=0,
                     syncmode=0):
        """Set bus timing parameters for classic CAN

        This function sets the bus timing parameters for the specified CAN
        controller.

        The library provides default values for tseg1, tseg2, sjw and noSamp
        when freq is specified to one of the pre-defined constants,
        `canlib.canlib.canBITRATE_xxx`.

        If freq is any other value, no default values are supplied by the
        library.

        If you are using multiple handles to the same physical channel, for
        example if you are writing a threaded application, you must call
        busOff() once for each handle. The same applies to busOn() - the
        physical channel will not go off bus until the last handle to the
        channel goes off bus.

        Args:
            freq: Bitrate in bit/s.
            tseg1: Number of quanta from (but not including) the Sync Segment
                to the sampling point.
            tseg2: Number of quanta from the sampling point to the end of
                the bit.
            sjw: The Synchronization Jump Width, can be 1,2,3, or 4.
            nosamp: The number of sampling points, only 1 is supported.
            syncMode: Unsupported and ignored.

        """
        dll.canSetBusParams(self.handle, freq, tseg1, tseg2, sjw,
                                 noSamp, syncmode)

    def getBusParams(self):
        """Get bus timing parameters for classic CAN

        This function retrieves the current bus parameters for the specified
        channel.

        Returns: A tuple containing:
            freq: Bitrate in bit/s.

            tseg1: Number of quanta from but not including the Sync
            Segment to the sampling point.

            tseg2: Number of quanta from the sampling point to the
            end of the bit.

            sjw: The Synchronization Jump Width, can be 1,2,3, or 4.

            noSamp: The number of sampling points, only 1 is supported.

            syncmode: Unsupported, always read as zero.

        """
        freq = ct.c_long()
        tseg1 = ct.c_uint()
        tseg2 = ct.c_uint()
        sjw = ct.c_uint()
        noSamp = ct.c_uint()
        syncmode = ct.c_uint()
        dll.canGetBusParams(self.handle, ct.byref(freq), ct.byref(tseg1),
                                 ct.byref(tseg2), ct.byref(sjw),
                                 ct.byref(noSamp), ct.byref(syncmode))
        return (freq.value, tseg1.value, tseg2.value, sjw.value, noSamp.value,
                syncmode.value)

    def setBusParamsFd(self, freq_brs, tseg1_brs=0, tseg2_brs=0, sjw_brs=0):
        """Set bus timing parameters for BRS in CAN FD

        This function sets the bus timing parameters used in BRS (Bit rate
        switch) mode for the current CANlib channel.

        The library provides default values for tseg1_brs, tseg2_brs and
        sjw_brs when freq is specified to one of the pre-defined constants,
        `canlib.canlib.canFD_BITRATE_xxx`

        If freq is any other value, no default values are supplied by the
        library.

        Args:
            freq_brs: Bitrate in bit/s.
            tseg1_brs: Number of quanta from (but not including) the Sync
               Segment to the sampling point.
            tseg2_brs: Number of quanta from the sampling point to the
               end of the bit.
            sjw_brs: The Synchronization Jump Width.

        """
        dll.canSetBusParamsFd(self.handle, freq_brs, tseg1_brs,
                                   tseg2_brs, sjw_brs)

    def getBusParamsFd(self):
        """Get bus timing parameters for BRS in CAN FD

        This function retrieves the bus current timing parameters used in BRS
        (Bit rate switch) mode for the current CANlib channel.

        The library provides default values for tseg1_brs, tseg2_brs and
        sjw_brs when freq is specified to one of the pre-defined constants,
        `canlib.canlib.canFD_BITRATE_xxx`

        If freq is any other value, no default values are supplied by the
        library.

        Returns: A tuple containing:
            freq_brs: Bitrate in bit/s.

            tseg1_brs: Number of quanta from (but not including) the Sync
            Segment to the sampling point.

            tseg2_brs: Number of quanta from the sampling point to the
            end of the bit.

            sjw_brs: The Synchronization Jump Width.

        """
        freq_brs = ct.c_long()
        tseg1_brs = ct.c_uint()
        tseg2_brs = ct.c_uint()
        sjw_brs = ct.c_uint()
        dll.canGetBusParamsFd(self.handle, ct.byref(freq_brs),
                                   ct.byref(tseg1_brs), ct.byref(tseg2_brs),
                                   ct.byref(sjw_brs))
        return (freq_brs.value, tseg1_brs.value, tseg2_brs.value,
                sjw_brs.value)

    def busOn(self):
        """Takes the specified channel on-bus.

        If you are using multiple handles to the same physical channel, for
        example if you are writing a threaded application, you must call
        busOn() once for each handle.

        """
        dll.canBusOn(self.handle)

    def busOff(self):
        """Takes the specified channel off-bus.

        Closes the channel associated with the handle. If no other threads are
        using the CAN circuit, it is taken off bus. The handle can not be used
        for further references to the channel.

        """
        dll.canBusOff(self.handle)

    # qqdaca v1.5 This function is complicated by the fact that previously it
    # had the signature of write_wait, and we still want to support that for
    # one more version at least.
    #
    # It would be preferable to merge `write` and `writeWait` by giving `write`
    # an optional `wait` argument. If specified, it would make the function
    # call `canWriteWait` with ``timeout=wait``. However, that would complicate
    # the function too much if the old signature is still to be supported.
    #
    # If this merger is done in the future, also add the same argument to
    # linlib's `writeMessage` and `requestMessage` functions.
    def write(self, frame=None, *args, **kwargs):
        """Send a CAN message.

        This function sends a Frame object as a CAN message. Note that the
        message has been queued for transmission when this calls return. It has
        not necessarily been sent.

        If you are using the same channel via multiple handles, note that the
        default behaviour is that the different handles will "hear" each other
        just as if each handle referred to a channel of its own. If you open,
        say, channel 0 from thread A and thread B and then send a message from
        thread A, it will be "received" by thread B. This behaviour can be
        changed using canIOCTL_SET_LOCAL_TXECHO.

        Also see `Channel.write_raw` for sending messages without constructing
        Frame objects.

        .. deprecated:: 1.5
           Sending the `Frame` contents as separate arguments; this
           functionality has been taken over by `write_raw`.

        Args:
            frame (Frame)

        """
        if len(args) == 0 and len(kwargs) == 0:
            dll.canWrite(
                self.handle, frame.id, bytes(frame.data), frame.dlc, frame.flags)
        else:
            deprecation.manual_warn(
                "Calling Channel.write() with individual arguments is deprecated, "
                "please use a Frame object or Channel.write_raw()")
            if frame is None:
                return self.write_raw(*args, **kwargs)
            else:
                return self.write_raw(frame, *args, **kwargs)

    # The variable name id (as used by canlib) is a built-in function in
    # Python, so we use the name id_ instead
    def write_raw(self, id_, msg, flag=0, dlc=None):
        """Send a CAN message

        See docstring of `Channel.write` for general information about sending
        CAN messages.

        The variable name id (as used by canlib) is a built-in function in
        Python, so the name `id_` is used instead.

        Args:
            id_: The identifier of the CAN message to send.
            msg: An array or bytearray of the message data
            flag: A combination of `canlib.canlib.MessageFlag`. Use this
                parameter e.g. to send extended (29-bit) frames.
            dlc: The length of the message in bytes. For Classic CAN dlc can
                be at most 8, unless `canlib.canlib.Open.ACCEPT_LARGE_DLC` is
                used. For CAN FD dlc can be one of the following 0-8, 12, 16,
                20, 24, 32, 48, 64. Optional, if omitted, dlc is calculated
                from the msg array.

        """
        if not isinstance(msg, (bytes, str)):
            if not isinstance(msg, bytearray):
                msg = bytearray(msg)
            msg = bytes(msg)
        if dlc is None:
            dlc = len(msg)
        dll.canWrite(self.handle, id_, msg, dlc, flag)

    def writeSync(self, timeout):
        """Wait for queued messages to be sent

        Waits until all CAN messages for the specified handle are sent, or the
        timeout period expires.

        Args:
            timeout (int): The timeout in milliseconds, `None` or ``0xFFFFFFFF`` for
                an infinite timeout.

        """
        if timeout is None:
            timeout = 0xFFFFFFFF
        dll.canWriteSync(self.handle, timeout)

    def writeWait(self, frame, timeout, *args, **kwargs):
        """Sends a CAN message and waits for it to be sent.

        This function sends a CAN message. It returns when the message is sent,
        or the timeout expires. This is a convenience function that combines
        write() and writeSync().

        .. deprecated:: 1.5
           Sending the `Frame` contents as separate arguments; this
           functionality has been taken over by `writeWait_raw`.

        Args:
            frame (Frame) : Frame containing the CAN data to be sent
            timeout: The timeout, in milliseconds. 0xFFFFFFFF gives an infinite
                timeout.
        """
        if len(args) == 0 and len(kwargs) == 0:
            dll.canWriteWait(
                self.handle, frame.id, bytes(frame.data), frame.dlc, frame.flags, timeout)
        else:
            deprecation.manual_warn(
                "Calling Channel.writeWait() with individual arguments is deprecated, "
                "please use a Frame object or Channel.writeWait_raw()")
            return self.writeWait_raw(frame, timeout, *args, **kwargs)

    def writeWait_raw(self, id_, msg, flag=0, dlc=0, timeout=0):
        """Sends a CAN message and waits for it to be sent.

        This function sends a CAN message. It returns when the message is sent,
        or the timeout expires. This is a convenience function that combines
        write() and writeSync().

        Args:
            id_: The identifier of the CAN message to send.
            msg: An array or bytearray of the message data
            flag: A combination of `canlib.canlib.MessageFlag`. Use this
                parameter e.g. to send extended (29-bit) frames.
            dlc: The length of the message in bytes. For Classic CAN dlc can
                be at most 8, unless `canlib.canlib.Open.ACCEPT_LARGE_DLC` is
                used. For CAN FD dlc can be one of the following 0-8, 12, 16,
                20, 24, 32, 48, 64. Optional, if omitted, dlc is calculated
                from the msg array.
            timeout: The timeout, in milliseconds. 0xFFFFFFFF gives an infinite
                timeout.

        """
        if not isinstance(msg, (bytes, str)):
            if not isinstance(msg, bytearray):
                msg = bytearray(msg)
            msg = bytes(msg)

        if (dlc == 0):
            dlc = len(msg)

        dll.canWriteWait(self.handle, id_, msg, dlc, flag, timeout)

    def readTimer(self):
        """Read the hardware clock on the specified device

        Returns the time value.
        """
        time = ct.c_int()
        dll.kvReadTimer(self.handle, time)
        return time.value

    def read(self, timeout=0):
        """Read a CAN message and metadata.

        Reads a message from the receive buffer. If no message is available,
        the function waits until a message arrives or a timeout occurs.

        Args:
            timeout (int):  Timeout in milliseconds, -1 gives an
                infinite timeout.

        Returns:
            (Frame): Frame object
        """
        # msg will be replaced by class when CAN FD is supported
        msg = ct.create_string_buffer(self._MAX_MSG_SIZE)
        id_ = ct.c_long()
        dlc = ct.c_uint()
        flag = ct.c_uint()
        time = ct.c_ulong()
        dll.canReadWait(self.handle, id_, msg, dlc, flag, time, timeout)
        try:
            flags = MessageFlag(flag.value)
            # In Python 2 this will fail because the value is a long, and the
            # enums only accept int.
        except ValueError:
            flags = MessageFlag(int(flag.value))

        length = self._calculate_length(dlc.value, flags)
        return Frame(
            id_=id_.value,
            data=bytearray(msg.raw[:length]),
            dlc=dlc.value,
            flags=flags,
            timestamp=time.value,
        )

    def readDeviceCustomerData(self, userNumber=100, itemNumber=0):
        buf = ct.create_string_buffer(8)
        user = ct.c_int(userNumber)
        item = ct.c_int(itemNumber)
        dll.kvReadDeviceCustomerData(self.handle, user, item, buf,
                                     ct.sizeof(buf))
        return struct.unpack('!Q', buf)[0]

    def readSpecificSkip(self, id_):
        # msg will be replaced by class when CAN FD is supported
        msg = ct.create_string_buffer(self._MAX_MSG_SIZE)
        id_ = ct.c_long(id_)
        dlc = ct.c_uint()
        flag = ct.c_uint()
        time = ct.c_ulong()
        dll.canReadSpecificSkip(self.handle, id_, msg, dlc, flag, time)
        try:
            flags = MessageFlag(flag.value)
            # In Python 2 this will fail because the value is a long, and the
            # enums only accept int.
        except ValueError:
            flags = MessageFlag(int(flag.value))

        length = self._calculate_length(dlc.value, flags)
        return Frame(
            id_=id_.value,
            data=bytearray(msg.raw[:length]),
            dlc=dlc.value,
            flags=flags,
            timestamp=time.value,
        )

    def requestChipStatus(self):
        dll.canRequestChipStatus(self.handle)

    def readStatus(self):
        flags = ct.c_ulong(0)
        dll.canReadStatus(self.handle, ct.byref(flags))
        return flags.value

    def readSyncSpecific(self, id_, timeout=0):
        id_ = ct.c_long(id_)
        dll.canReadSyncSpecific(self.handle, id_, timeout)

    def scriptSendEvent(self, slotNo=0, eventType=const.kvEVENT_TYPE_KEY,
                        eventNo=ord('a'), data=0):
        dll.kvScriptSendEvent(self.handle, ct.c_int(slotNo),
                              ct.c_int(eventType), ct.c_int(eventNo),
                              ct.c_uint(data))

    def setBusOutputControl(self, drivertype=const.canDRIVER_NORMAL):
        dll.canSetBusOutputControl(self.handle, drivertype)

    @deprecation.deprecated.favour(".iocontrol.flush_rx_buffer()")
    def ioCtl_flush_rx_buffer(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.flush_rx_buffer()``.

        """
        dll.canIoCtl(self.handle, const.canIOCTL_FLUSH_RX_BUFFER, None, 0)

    @deprecation.deprecated.favour("'Channel.iocontrol.timer_scale = scale'")
    def ioCtl_set_timer_scale(self, scale):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.timer_scale = scale``

        """
        scale = ct.c_long(scale)
        dll.canIoCtl(self.handle, const.canIOCTL_SET_TIMER_SCALE,
                     ct.byref(scale), ct.sizeof(scale))

    @deprecation.deprecated.favour("'Channel.iocontrol.report_access_errors' attribute")
    def ioCtl_get_report_access_errors(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.report_access_errors``

        """
        buf = ct.c_ubyte()
        dll.canIoCtl(self.handle, const.canIOCTL_GET_REPORT_ACCESS_ERRORS,
                     ct.byref(buf), ct.sizeof(buf))
        return buf.value

    @deprecation.deprecated.favour("'Channel.iocontrol.report_access_errors = on'")
    def ioCtl_set_report_access_errors(self, on=0):
        """Deprecated function

        .. deprecated:: 1.5
           Use `IOControl`; ``Channel.iocontrol.report_access_errors = on``

        """
        buf = ct.c_ubyte(on)
        dll.canIoCtl(self.handle, const.canIOCTL_SET_REPORT_ACCESS_ERRORS,
                     ct.byref(buf), ct.sizeof(buf))

    def flashLeds(self, action, timeout_ms):
        """Turn Leds on or off.

        Args:
            action (int): One of `canlib.canlib.LEDAction`, defining
                          which LED to turn on or off.
            timeout_ms (int): Specifies the time, in milliseconds, during which
                              the action is to be carried out. When the timeout
                              expires, the LED(s) will return to its ordinary
                              function.
        """
        dll.kvFlashLeds(self.handle, action, timeout_ms)

    @deprecation.deprecated.favour("ChannelData(Channel.index).device_name")
    def getChannelData_Name(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).device_name``

        """
        return wrapper.getChannelData_Name(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).custom_name")
    def getChannelData_Cust_Name(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).custom_name``

        """
        try:
            return wrapper.getChannelData_Cust_Name(self.index)
        except (CanError) as ex:
            None
            return ""
        return ""

    @deprecation.deprecated.favour("ChannelData(Channel.index).chan_no_on_card")
    def getChannelData_Chan_No_On_Card(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).chan_no_on_card``

        """
        return wrapper.getChannelData_Chan_No_On_Card(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).card_number")
    def getChannelData_CardNumber(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).card_number``

        """
        return wrapper.getChannelData_CardNumber(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).card_upc_no")
    def getChannelData_EAN(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).card_upc_no``

        """
        return wrapper.getChannelData_EAN(self.index)

    @deprecation.deprecated
    def getChannelData_EAN_short(self):
        return wrapper.getChannelData_EAN_short(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).card_serial_no")
    def getChannelData_Serial(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).card_serial_no``

        """
        return wrapper.getChannelData_Serial(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).driver_name")
    def getChannelData_DriverName(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).driver_name``

        """
        return wrapper.getChannelData_DriverName(self.index)

    @deprecation.deprecated.favour("ChannelData(Channel.index).card_firmware_rev")
    def getChannelData_Firmware(self):
        """Deprecated function

        .. deprecated:: 1.5
           Use `ChannelData`; ``ChannelData(Channel.index).card_firmware_rev``

        """
        return wrapper.getChannelData_Firmware(self.index)

    def scriptStart(self, slot):
        dll.kvScriptStart(self.handle, slot)

    def scriptStop(self, slot, mode=const.kvSCRIPT_STOP_NORMAL):
        dll.kvScriptStop(self.handle, slot, mode)

    def scriptUnload(self, slot):
        dll.kvScriptUnload(self.handle, slot)

    def scriptLoadFileOnDevice(self, slot, localFile):
        dll.kvScriptLoadFileOnDevice(self.handle, slot,
                                     ct.c_char_p(localFile))

    def scriptLoadFile(self, slot, filePathOnPC):
        c_filePathOnPC = ct.c_char_p(filePathOnPC.encode())
        dll.kvScriptLoadFile(self.handle, slot, c_filePathOnPC)

    def scriptEnvvarOpen(self, name):
        envvarType = ct.c_int()
        envvarSize = ct.c_int()
        envHandle = dll.kvScriptEnvvarOpen(self.handle, ct.c_char_p(name),
                                           ct.byref(envvarType),
                                           ct.byref(envvarSize))
        return envHandle, envvarType.value, envvarSize.value

    def scriptEnvvarClose(self, envHandle):
        dll.kvScriptEnvvarClose(ct.c_int64(envHandle))

    def scriptEnvvarSetInt(self, envHandle, value):
        value = int(value)
        dll.kvScriptEnvvarSetInt(ct.c_int64(envHandle), ct.c_int(value))

    def scriptEnvvarGetInt(self, envHandle):
        envvarValue = ct.c_int()
        dll.kvScriptEnvvarGetInt(ct.c_int64(envHandle),
                                 ct.byref(envvarValue))
        return envvarValue.value

    def scriptEnvvarSetFloat(self, envHandle, value):
        value = float(value)
        dll.kvScriptEnvvarSetFloat(ct.c_int64(envHandle),
                                   ct.c_float(value))

    def scriptEnvvarGetFloat(self, envHandle):
        envvarValue = ct.c_float()
        dll.kvScriptEnvvarGetFloat(ct.c_int64(envHandle),
                                   ct.byref(envvarValue))
        return envvarValue.value

    def scriptEnvvarSetData(self, envHandle, value, envSize):
        value_p = ct.create_string_buffer(value.encode('utf-8'))
        dll.kvScriptEnvvarSetData(ct.c_int64(envHandle),
                                  value_p, 0,
                                  ct.c_int(envSize))

    def scriptEnvvarGetData(self, envHandle, envSize):
        envvarValue = ct.create_string_buffer(envSize)
        dll.kvScriptEnvvarGetData(ct.c_int64(envHandle),
                                  ct.byref(envvarValue), 0,
                                  ct.c_int(envSize))
        return envvarValue.value

    def fileGetCount(self):
        """Get the number of files on the device.

        Returns:
            count (int): The number of files.
        """
        count = ct.c_int()
        dll.kvFileGetCount(self.handle, ct.byref(count))
        return count.value

    def fileGetName(self, fileNo):
        """Get the name of the file with the supplied number.

        Args:
            fileNo (int): The number of the file.

        Returns:
            fileName (string): The name of the file.
        """
        fileName = ct.create_string_buffer(50)
        dll.kvFileGetName(self.handle, ct.c_int(fileNo), fileName,
                          ct.sizeof(fileName))
        return fileName.value.decode()

    def fileDelete(self, deviceFileName):
        """Delete file from device."""
        dll.kvFileDelete(self.handle, deviceFileName.encode())

    def fileCopyToDevice(self, hostFileName, deviceFileName=None):
        """Copy an arbitrary file from the host to the device.

        Args:
            hostFileName (string):   The target host file name.
            deviceFileName (string, optional): The device file name.
                Defaults to hostFileName.
        """
        if deviceFileName is None:
            deviceFileName = hostFileName
        dll.kvFileCopyToDevice(self.handle, hostFileName.encode(),
                               deviceFileName.encode())

    def fileCopyFromDevice(self, deviceFileName, hostFileName=None):
        """Copy an arbitrary file from the device to the host.

        Args:
            deviceFileName (string): The device file name.
            hostFileName (string, optional):   The target host file name.
                Defaults to deviceFileName.
        """
        if hostFileName is None:
            hostFileName = deviceFileName
        dll.kvFileCopyFromDevice(self.handle, deviceFileName.encode(),
                                 hostFileName.encode())

    def kvDeviceSetMode(self, mode):
        """Set the current device's mode.

        Note:

            The mode is device specific, which means that not all modes are
            implemented in all products.

        Args:
            mode (int): One of `canlib.canlib.DeviceMode`, defining which
                        mode to use.

        """
        dll.kvDeviceSetMode(self.handle, ct.c_int(mode))

    def kvDeviceGetMode(self):
        """Read the current device's mode.

        Note:

            The mode is device specific, which means that not all modes are
            implemented in all products.

        Returns:
            mode (int): One of `canlib.canlib.DeviceMode`, indicating
            which mode is in use.

        """
        mode = ct.c_int()
        dll.kvDeviceGetMode(self.handle, ct.byref(mode))
        return DeviceMode(mode.value)
