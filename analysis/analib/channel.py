# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 20:56:57 2018

@author: Sebastian Scholz
"""

import ctypes as ct
import logging
import time
import ipaddress

from .wrapper import dll, errorCheck, restart
from .exception import dllException, CanNoMsg
from .constants import CONNECT_STATES, BAUDRATES


@dll.CBFUNC
def cbFunc(cobid, data, dlc, flags, handle):
    """Example callback function for incoming CAN messages.

    The arguments are passed as python build-in data types.
    """
    print('Calling callback function with the following arguments:')
    print(f'    COBID: {cobid:03X}; Data: {data[:dlc].hex()}; DLC: {dlc}; '
          f'Flags: {flags}; Handle: {handle}')


def check_type(value, name, valtype=int):
    if not isinstance(value, valtype):
        raise TypeError(f'{name} should be of type "{valtype}", and not '
                        f'"{type(value)}"')


class Channel(object):

    def __init__(self, ipAddress='192.168.1.254', port=0, confirm=True,
                 ind=True, timeout=10000, baudrate=125000, operatingMode=0,
                 termination=True, highSpeedMode=False, timeStampOn=False,
                 maxSizePerQueue=1000):
        """Open a connection to an Anagate CAN channel.

        Args:
            ipAddress (str, optional): Network address of the AnaGate partner.
                Defaults to '192.168.1.254' which is the factory default.
            port (int, optional): CAN port number.
                Allowed values are:
                    * 0 for port 1/A (all AnaGate CAN models)
                    * 1 for port 2/B (AnaGate CAN duo, AnaGate CAN quattro,
                        AnaGate CAN X2/X4/X8)
                    * 2 for port 3/C (AnaGate CAN quattro, AnaGate CAN X4/X8)
                    * 3 for port 4/D (AnaGate CAN quattro, AnaGate CAN X4/X8)
                    * 4 for port 5/E (AnaGate CAN X8)
                    * 5 for port 6/F (AnaGate CAN X8)
                    * 6 for port 7/G (AnaGate CAN X8)
                    * 7 for port 8/H (AnaGate CAN X8)
                Defaults to 0.
            confirm (bool, optional): If set to True, all incoming and outgoing
                data requests are confirmed by the internal message protocol.
                Without confirmations a better transmission performance is
                reached. Defaults to True.
            ind (bool, optional): If set to False, all incoming telegrams are
                discarded. Defaults to True.
            timeout (int, optional): Default timeout for accessing the AnaGate
                in milliseconds.
                A timeout is reported if the AnaGate partner does not respond
                within the defined timeout period. This global timeout value is
                valid on the current network connection for all commands and
                functions which do not offer a specific timeout value.
                Defaults to 10 s.
            baudrate (int, optional): The baud rate to be used.
                The following values are supported:
                    * 10000 für 10kBit
                    * 20000 für 20kBit
                    * 50000 für 50kBit
                    * 62500 für 62.5kBit
                    * 100000 für 100kBit
                    * 125000 für 125kBit
                    * 250000 für 250kBit
                    * 500000 für 500kBit
                    * 800000 für 800kBit (not AnaGate CAN)
                    * 1000000 für 1MBit
            operatingMode (int, optional): The operating mode to be used.
                The following values are allowed:
                    * 0 = default mode.
                    * 1 = loop back mode: No telegrams are sent via CAN bus.
                        Instead they are received as if they had been
                        transmitted over CAN by a different CAN device.
                    * 2 = listen mode: Device operates as a passive bus
                        partner, meaning no telegrams are sent to the CAN bus
                        (nor ACKs for incoming telegrams).
                    * 3 = offline mode: No telegrams are sent or received on
                        the CAN bus. Thus no error frames are generated on the
                        bus if other connected CAN devices send telegrams with
                        a different baud rate.
            termination (bool, optional): Use integrated CAN bus termination
                (True=yes, False=no). This setting is not supported by all
                AnaGate CAN models.
            highSpeedMode (bool, optional): Use high speed mode (True=yes,
                False=no). This setting is not supported by all AnaGate CAN
                models.
                The high speed mode was created for large baud rates with
                continuously high bus load. In this mode telegrams are not
                confirmed on the protocol layer and the software filters
                defined via CANSetFilter are ignored.
            timeStampOn (bool, optional): Use time stamp mode (True=yes,
                False=no). This setting is not supported by all AnaGate CAN
                models.
                In activated time stamp mode an additional timestamp is sent
                with the CAN telegram. This timestamp indicates when the
                incoming message was received by the CAN controller or when the
                outgoing message was confirmed by the CAN controller.
            maxSizePerQueue (int, optional): Maximum size of the receive
                buffer. Defaults to 42.
        """

        # Value checks
        if baudrate not in BAUDRATES:
            raise ValueError(f'Baudrate value {baudrate} is not allowed!')
        if operatingMode not in range(4):
            raise ValueError(f'Operating mode must be 0, 1, 2 or 3, but is '
                             f'{operatingMode}')
        # Raises ValueError if ipAddress is invalid
        ipaddress.ip_address(ipAddress)

        # Initialize private attributes containing ctypes variables
        self.__deviceOpen = False
        self.__handle = ct.c_int32()
        self.__port = ct.c_int32()
        self.__sendDataConfirm = ct.c_int32()
        self.__sendDataInd = ct.c_int32()
        self.__ipAddress = ct.create_string_buffer(bytes(ipAddress, 'utf-8'))
        self.__baudrate = ct.c_uint32(baudrate)
        self.__operatingMode = ct.c_uint8(operatingMode)
        self.__termination = ct.c_int32(int(termination))
        self.__highSpeedMode = ct.c_int32(int(highSpeedMode))
        self.__timeStampOn = ct.c_int32(int(timeStampOn))
        self.__maxSizePerQueue = ct.c_uint32(maxSizePerQueue)

        # Establish connection with Anagate partner and set configuration
        self._openDevice(ipAddress, port, confirm, ind, timeout)
        self.setGlobals()
        self.setTime()
        self._setMaxSizePerQueue(maxSizePerQueue)
        # self.setCallback(cbFunc)

    def __str__(self):
        return (f'Anagate CAN channel: IP address: {self.ipAddress}; '
                f'CAN port: {self.port}')

    __repr__ = __str__

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        logging.exception(exception_value)
        return True

    def __del__(self):
        self.close()

    @property
    def handle(self):
        """int: Access handle"""
        return self.__handle.value

    @property
    def port(self):
        """int: CAN port number"""
        return self.__port.value

    @property
    def sendDataConfirm(self):
        """bool: If True, all incoming and outgoing data requests are confirmed
            by the internal message protocol. Without confirmations a better
            transmission performance is reached.
        """
        return bool(self.__sendDataConfirm.value)

    @property
    def sendDataInd(self):
        """bool : If set to False, all incoming telegrams are discarded."""
        return bool(self.__sendDataInd.value)

    @property
    def ipAddress(self):
        """str : Network address of the AnaGate partner."""
        return self.__ipAddress.value.decode()

    @property
    def baudrate(self):
        """int : The baud rate to be used.

        The following values are supported:

        * 10000 für 10kBit
        * 20000 für 20kBit
        * 50000 für 50kBit
        * 62500 für 62.5kBit
        * 100000 für 100kBit
        * 125000 für 125kBit
        * 250000 für 250kBit
        * 500000 für 500kBit
        * 800000 für 800kBit (not AnaGate CAN)
        * 1000000 für 1MBit

        """
        self.getGlobals()
        return self.__baudrate.value

    @baudrate.setter
    def baudrate(self, value):
        check_type(value, 'baudrate')
        if value not in BAUDRATES:
            raise ValueError(f'Baudrate value {value} is not allowed!')
        self.__baudrate.value = value
        self.setGlobals()

    @property
    def operatingMode(self):
        """int: The operating mode to be used.

        The following values are allowed:
            * 0 = default mode.
            * 1 = loop back mode: No telegrams are sent via CAN bus.
                Instead they are received as if they had been
                transmitted over CAN by a different CAN device.
            * 2 = listen mode: Device operates as a passive bus
                partner, meaning no telegrams are sent to the CAN bus
                (nor ACKs for incoming telegrams).
            * 3 = offline mode: No telegrams are sent or received on
                the CAN bus. Thus no error frames are generated on the
                bus if other connected CAN devices send telegrams with
                a different baud rate.
        """
        self.getGlobals()
        return self.__operatingMode.value

    @operatingMode.setter
    def operatingMode(self, value):
        check_type(value, 'operatingMode')
        if value not in range(4):
            raise ValueError(f'Operating mode must be 0, 1, 2 or 3, but is '
                             f'{value}')
        self.__operatingMode.value = value
        self.setGlobals()

    @property
    def termination(self):
        """bool: Use high speed mode (True=yes, False=no).

        This setting is not supported by all AnaGate CAN models.
        """
        self.getGlobals()
        return bool(self.__termination.value)

    @termination.setter
    def termination(self, value):
        check_type(value, 'termination', bool)
        self.__termination.value = int(value)
        self.setGlobals()

    @property
    def highSpeedMode(self):
        """bool: Use high speed mode (True=yes, False=no).

        This setting is not supported by all AnaGate CAN models.

        The high speed mode was created for large baud rates with continuously
        high bus load. In this mode telegrams are not confirmed on the protocol
        layer and the software filters defined via CANSetFilter are ignored.
        """
        self.getGlobals()
        return bool(self.__highSpeedMode.value)

    @highSpeedMode.setter
    def highSpeedMode(self, value):
        check_type(value, 'highSpeedMode', bool)
        self.__highSpeedMode.value = int(value)
        self.setGlobals()

    @property
    def timeStampOn(self):
        """bool: Use time stamp mode (True=yes, False=no).

        This setting is not supported by all AnaGate CAN models.

        In activated time stamp mode an additional timestamp is sent with the
        CAN telegram. This timestamp indicates when the incoming message was
        received by the CAN controller or when the outgoing message was
        confirmed by the CAN controller.
        """
        self.getGlobals()
        return bool(self.__timeStampOn.value)

    @timeStampOn.setter
    def timeStampOn(self, value):
        check_type(value, 'timeStampOn', bool)
        self.__timeStampOn.value = int(value)
        self.setGlobals()

    @property
    def state(self):
        """str: Parses the integer connection state to a meaningful string.

        Possible values are:
            * 'DISCONNECTED'
            * 'CONNECTING'
            * 'CONNECTED',
            * 'DISCONNECTING'
            * 'NOT_INITIALIZED'
        """
        if self.__deviceOpen:
            return CONNECT_STATES[self._deviceConnectState()]
        return 'DISCONNECTED'

    @property
    def maxSizePerQueue(self):
        """int: Maximum size of the receive buffer."""
        return self.__maxSizePerQueue.value

    @maxSizePerQueue.setter
    def maxSizePerQueue(self, value):
        check_type(value, 'maxSizePerQueue')
        if value < 0:
            raise ValueError(f'Value {value} of maxSizePerQueue is < 0.')
        self._setMaxSizePerQueue(value)
        self.__maxSizePerQueue.value = value

    @property
    def deviceOpen(self):
        """bool: If the Access handle is valid"""
        return self.__deviceOpen

    def _openDevice(self, ipAddress='192.168.1.254', port=0, confirm=True,
                    ind=True, timeout=10000):
        """Opens an network connection (TCP or UDP) to an AnaGate CAN device.

        Opens a TCP/IP connection to an CAN interface of an AnaGate CAN device.
        If the connection is established, CAN telegrams can be sent and
        received.

        The connection should be closed with the function _closeDevice if not
        longer needed.

        Args:
            ipAddress (str, optional): Network address of the AnaGate partner.
                Defaults to '192.168.1.254' which is the factory default.
            port (int, optional): CAN port number.
                Allowed values are:
                    * 0 for port 1/A (all AnaGate CAN models)
                    * 1 for port 2/B (AnaGate CAN duo, AnaGate CAN quattro,
                        AnaGate CAN X2/X4/X8)
                    * 2 for port 3/C (AnaGate CAN quattro, AnaGate CAN X4/X8)
                    * 3 for port 4/D (AnaGate CAN quattro, AnaGate CAN X4/X8)
                    * 4 for port 5/E (AnaGate CAN X8)
                    * 5 for port 6/F (AnaGate CAN X8)
                    * 6 for port 7/G (AnaGate CAN X8)
                    * 7 for port 8/H (AnaGate CAN X8)
                Defaults to 0.
            confirm (bool, optional): If set to True, all incoming and outgoing
                data requests are confirmed by the internal message protocol.
                Without confirmations a better transmission performance is
                reached. Defaults to True.
            ind (bool, optional): If set to False, all incoming telegrams are
                discarded. Defaults to True.
            timeout (int, optional): Default timeout for accessing the AnaGate
                in milliseconds.
                A timeout is reported if the AnaGate partner does not respond
                within the defined timeout period. This global timeout value is
                valid on the current network connection for all commands and
                functions which do not offer a specific timeout value.
                Defaults to 10 s.
        """

        bSendDataConfirm = ct.c_int32(int(confirm))
        bSendDataInd = ct.c_int32(int(ind))
        nCANPort = ct.c_int32(port)
        pcIPAddress = ct.create_string_buffer(bytes(ipAddress, 'utf-8'))
        nTimeout = ct.c_int32(timeout)
        ret = ct.c_int32()

        ret = dll.CANOpenDevice(ct.byref(self.__handle), bSendDataConfirm,
                                bSendDataInd, nCANPort, pcIPAddress, nTimeout)

        errorCheck(ret)
        self.__port = nCANPort
        self.__sendDataConfirm = bSendDataConfirm
        self.__sendDataInd = bSendDataInd
        self.__ipAddress = pcIPAddress
        self.__deviceOpen = True
        return True

    def _closeDevice(self):
        """Closes an open network connection to an AnaGate CAN device."""
        ret = dll.CANCloseDevice(self.__handle)
        errorCheck(ret)
        self.__deviceOpen = False

    def close(self):
        try:
            self._closeDevice()
        except dllException:
            pass

    def openChannel(self):
        if not self.__deviceOpen:
            return self._openDevice(self.ipAddress, self.port,
                                    self.sendDataConfirm, self.sendDataInd)

    def restart(self):
        restart(self.ipAddress)

    def setGlobals(self, baudrate=None, operatingMode=None, termination=None,
                   highSpeedMode=None, timeStampOn=None):
        """Sets the global settings which are to be used on the CAN bus.

        Sets the global settings of the used CAN interface. These settings are
        effective for all concurrent connections to the CAN interface. The
        settings are not saved permanently on the device and are reset after
        every device restart.

        Args:
            baudrate (int, optional): The baud rate to be used.
                The following values are supported:
                    * 10000 für 10kBit
                    * 20000 für 20kBit
                    * 50000 für 50kBit
                    * 62500 für 62.5kBit
                    * 100000 für 100kBit
                    * 125000 für 125kBit
                    * 250000 für 250kBit
                    * 500000 für 500kBit
                    * 800000 für 800kBit (not AnaGate CAN)
                    * 1000000 für 1MBit
            operatingMode (int, optional): The operating mode to be used.
                The following values are allowed:
                    * 0 = default mode.
                    * 1 = loop back mode: No telegrams are sent via CAN bus.
                        Instead they are received as if they had been
                        transmitted over CAN by a different CAN device.
                    * 2 = listen mode: Device operates as a passive bus
                        partner, meaning no telegrams are sent to the CAN bus
                        (nor ACKs for incoming telegrams).
                    * 3 = offline mode: No telegrams are sent or received on
                        the CAN bus. Thus no error frames are generated on the
                        bus if other connected CAN devices send telegrams with
                        a different baud rate.
            termination (bool, optional): Use integrated CAN bus termination
                (True=yes, False=no). This setting is not supported by all
                AnaGate CAN models.
            highSpeedMode (bool, optional): Use high speed mode (True=yes,
                False=no). This setting is not supported by all AnaGate CAN
                models.
                The high speed mode was created for large baud rates with
                continuously high bus load. In this mode telegrams are not
                confirmed on the protocol layer and the software filters
                defined via CANSetFilter are ignored.
            timeStampOn (bool, optional): Use time stamp mode (True=yes,
                False=no). This setting is not supported by all AnaGate CAN
                models.
                In activated time stamp mode an additional timestamp is sent
                with the CAN telegram. This timestamp indicates when the
                incoming message was received by the CAN controller or when the
                outgoing message was confirmed by the CAN controller.
        """
        baudrate = self.__baudrate if baudrate is None \
            else ct.c_uint32(baudrate)
        operatingMode = self.__operatingMode if operatingMode is None \
            else ct.c_uint8(operatingMode)
        termination = self.__termination if termination is None \
            else ct.c_int32(int(termination))
        highSpeedMode = self.__highSpeedMode if highSpeedMode is None \
            else ct.c_int32(int(highSpeedMode))
        timeStampOn = self.__timeStampOn if timeStampOn is None \
            else ct.c_int32(timeStampOn)

        ret = dll.CANSetGlobals(self.__handle, baudrate, operatingMode,
                                termination, highSpeedMode, timeStampOn)
        errorCheck(ret)
        self.__baudrate = baudrate
        self.__operatingMode = operatingMode
        self.__termination = termination
        self.__highSpeedMode = highSpeedMode
        self.__timeStampOn = timeStampOn

    def getGlobals(self):
        """Gets the currently used global settings on the CAN bus.

        Returns the global settings of the used CAN interface. These settings
        are effective for all concurrent connections to the CAN interface.

        Saves the received values in the corresponding private attributes.
        """
        ret = dll.CANGetGlobals(self.__handle, ct.byref(self.__baudrate),
                                ct.byref(self.__operatingMode),
                                ct.byref(self.__termination),
                                ct.byref(self.__highSpeedMode),
                                ct.byref(self.__timeStampOn))
        errorCheck(ret)

    def setTime(self, seconds=None, microseconds=0):
        """Sets the current system time on the AnaGate device.

        The CANSetTime function sets the system time on the AnaGate hardware.
        If the time stamp mode is switched on by the setGlobals function, the
        AnaGate hardware adds a time stamp to each incoming CAN telegram and a
        time stamp to the confirmation of a telegram sent via the API (only if
        confirmations are switched on for data requests).

        Args:
            seconds (float): Time in seconds from 01.01.1970. Defaults to None.
                In that case the current system time is used.
            microseconds (int, optional): Micro seconds. Defaults to 0.
        """
        if seconds is None:
            seconds = time.time()
            microseconds = int((seconds - int(seconds)) * 1000000)
            seconds = int(seconds)
        seconds = ct.c_uint32(seconds)
        microseconds = ct.c_uint32(microseconds)

        ret = dll.CANSetTime(self.__handle, seconds, microseconds)
        errorCheck(ret)

    def getTime(self):
        """Gets the current system time from the AnaGate CAN device.

        If the time stamp mode is switched on by the CANSetGlobals function,
        the AnaGate hardware adds a time stamp to each incoming CAN telegram
        and a time stamp to the confirmation of a telegram sent via the API
        (only if confirmations are switched on for data requests).

        Returns:
            int: Time in seconds from 01.01.1970.
            int: Micro seconds.
        """
        seconds = ct.c_uint32()
        microseconds = ct.c_uint32()
        timeWasSet = ct.c_int32()
        ret = dll.CANGetTime(self.__handle, ct.byref(timeWasSet),
                             ct.byref(seconds), ct.byref(microseconds))
        errorCheck(ret)
        return seconds.value, microseconds.value

    def write(self, identifier, data, flags=0):
        """Sends a CAN telegram to the CAN bus via the AnaGate device.

        Args:
            identifier (int): CAN identifier of the sender. Parameter flags
                defines whether the address is in extended format (29-bit) or
                standard format (11-bit).
            data (list(int)): Data content given as a list of integers. Data
                length is computed from this list.
            flags (int, optional): The format flags are defined as follows:
                    * Bit 0: If set, the CAN identifier is in extended format
                        (29 bit), otherwise not (11 bit).
                    * Bit 1: If set, the telegram is marked as remote frame.
                    * Bit 2: If set, the telegram has a valid timestamp. This
                        bit is only set for incoming data telegrams and doesn't
                        need to be set for the CANWrite and CANWriteEx
                        functions.
        """
        buffer = ct.create_string_buffer(bytes(data))
        bufferLen = ct.c_int32(len(data))
        flags = ct.c_int32(flags)
        identifier = ct.c_int32(identifier)

        ret = dll.CANWrite(self.__handle, identifier, buffer, bufferLen, flags)
        errorCheck(ret)

    def _setMaxSizePerQueue(self, maxSize):
        """Sets the maximum size of the queue that buffers received CAN
        telegrams.

        Sets the maximum size of the queue that buffers received CAN telegrams.
        No telegrams are buffered before this function is called. Once received
        telegrams have been added to the buffer they can be read with
        getMessage. If the queue is full while a new telegram is received
        then it gets discarded.

        If the queue size is set to 0 then all previously queued telegrams are
        deleted. However, if the queue size is reduced to a value different
        from 0 then excess telegrams are not discarded. Instead newly received
        telegrams don't get queued until the queue has been freed enough via
        getMessage calls, or until the queue size has been increased again.

        Remarks:
            Received telegrams are only buffered if no callback function was
            registered via setCallback. Once a callback function has been
            enabled, previously buffered telegrams can still be read via
            getMessage. Newly received telegrams are not added to the queue
            though.

        Args:
            maxSize (int): Maximum size of the receive buffer.
        """
        maxSize = ct.c_uint32(maxSize)
        ret = dll.CANSetMaxSizePerQueue(self.__handle, maxSize)
        errorCheck(ret)

    def getMessage(self):
        """
        Returns a received CAN telegram from the receive queue. The caller
        needs to supply memory buffers for the telegram parameters he is
        interested in. Parameters for unneeded values can be NULL pointers.

        The function returns the number of telegrams that are still in the
        queue after the function call via the pnAvailMsgs parameter. This
        variable is set to -1 if no telegram was available in the queue. In
        that case all telegram parameters are invalid.

        Returns:
            int: 11 bit CAN ID of the telegram
            bytes: Data bytes of the telegram
            int: Number of data bytes in the telegram
            int: Flags of the telegram
            float: Timestamp in seconds since 1.1.1970

        Raises:
            CanNoMsg: If there no available CAN messages in the buffer
        """
        availMsgs = ct.c_uint32()
        identifier = ct.c_int32()
        data = ct.create_string_buffer(8)
        dataLen = ct.c_uint8()
        flags = ct.c_int32()
        seconds = ct.c_int32()
        microseconds = ct.c_int32()

        ret = dll.CANGetMessage(self.__handle, ct.byref(availMsgs),
                                ct.byref(identifier), data, ct.byref(dataLen),
                                ct.byref(flags), ct.byref(seconds),
                                ct.byref(microseconds))
        errorCheck(ret)
        if availMsgs.value == ct.c_uint32(-1).value:
            raise CanNoMsg
        return identifier.value, data.raw[:dataLen.value], dataLen.value, \
            flags.value, seconds.value + microseconds.value / 1000000

    def _deviceConnectState(self):
        """Retrieves the current network connection state of the current
        AnaGate connection.

        This function can be used to check if an already connected device is
        disconnected.

        The detection period of a state change depends on the use of the
        internal AnaGateALIVE mechanism. This ALIVE mechanism has to be
        switched on explicitly via the startAlive function. Once activated
        the connection state is periodically checked by the ALIVE mechanism.

        Returns:
            int: The current network connection state. The following values are
                possible:
                    * 1 = DISCONNECTED: The connection to the AnaGate is
                        disconnected.
                    * 2 = CONNECTING: The connection is connecting.
                    * 3 = CONNECTED : The connection is established.
                    * 4 = DISCONNECTING: The connection is disonnecting.
                    * 5 = NOT_INITIALIZED: The network protocol is not
                        successfully initialized.
        """
        return dll.CANDeviceConnectState(self.__handle)

    def startAlive(self, aliveTime=1):
        """Starts the ALIVE mechanism, which checks periodically the state of
        the network connection to the AnaGate hardware.

        The AnaGate communication protocol (see [TCP-2010]) supports an
        application specific connection control which allows faster detection
        of broken connection lines.

        The CANStartAlive function starts a concurrent thread in the DLL in
        order to send defined alive telegrams (ALIVE_REQ) peridically (approx.
        every half of the given time out) to the Anagate device via the current
        network connection. If the alive telegram is not confirmed within the
        alive time the connection is marked as disconnected and the socket is
        closed if not already closed.

        Use the _deviceConnectState function to check the current network
        connection state.

        Args:
            aliveTime (int): Time out interval in seconds for the ALIVE
                mechanism. Defaults to 1 s.
        """

        ret = dll.CANStartAlive(self.__handle, ct.c_int32(aliveTime))
        errorCheck(ret)

    def setCallback(self, callbackFunction):
        """Defines an asynchronous callback function which is called for each
        incoming CAN telegram.

        Incoming CAN telegrams can bei received via a callback function which
        can be set by a simple API call. If a callback function is set it will
        be called by the API asynchronously.

        Args:
            callbackFunction: Function pointer to the private callback
                function. Set this parameter to NULL to deactivate the callback
                function. The parameters of the callback function are described
                in the documentation of the CANWrite function.
        """
        ret = dll.CANSetCallback(self.__handle, callbackFunction)
        errorCheck(ret)

      