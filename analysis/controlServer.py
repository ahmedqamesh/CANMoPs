from __future__ import annotations
from typing import *
import time
import datetime
import sys
import os
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from pathlib import Path
from threading import Thread, Event, Lock
import matplotlib as mpl
import numpy as np
from analysis import analysis_utils , controlServer
from analysis import CANopenConstants as coc
# Third party modules
from collections import deque, Counter
import ctypes as ct
import logging
from logging.handlers import RotatingFileHandler
import verboselogs
import coloredlogs as cl
from canlib import canlib, Frame
from canlib.canlib.exceptions import CanGeneralError
from canlib.canlib import ChannelData
from termcolor import colored
rootdir = os.path.dirname(os.path.abspath(__file__))
try:
    import analib
except:
    print (colored("Warning: AnaGate Package is not installed.......", 'red'), colored("Please ignore the warning if you are not using any AnaGate commercial controllers.", "green"))
    analib = canlib

class BusEmptyError(Exception):
    pass


class ControlServer(object):
    def __init__(self, parent=None, 
                 config=None, interface= None,
                 bitrate =None,
                 console_loglevel=logging.INFO,
                 file_loglevel=logging.INFO,
                 channel =None,ipAddress =None,
                 set_channel = False,
                 logformat='%(asctime)s - %(levelname)s - %(message)s'):
       
        super(ControlServer, self).__init__() # super keyword to call its methods from a subclass:
        config_dir = "config/"
        self.__cnt = Counter()
        """:obj:`~logging.Logger`: Main logger for this class"""
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        cl.install(fmt=logformat, level=console_loglevel, isatty=True,milliseconds=True)
        
        # Read configurations from a file
        if config is None:
            conf = analysis_utils.open_yaml_file(file =config_dir + "main_cfg.yml",directory =rootdir[:-8])
        self._index_items       =   conf["default_values"]["index_items"]
        self.__interfaceItems   =   conf['default_values']["interface_items"]        
        self.__bitrate_items    =   conf['default_values']['bitrate_items']
        self.__bytes            =   conf["default_values"]["bytes"]
        self.__subIndex         =   conf["default_values"]["subIndex"]
        self.__cobid            =   conf["default_values"]["cobid"]
        self.__dlc              =   conf["default_values"]["dlc"]
        self.__nodeIds          =   conf["CAN_settings"]["nodeIds"]
        if interface == "Kvaser":
            self.__interface        =   conf['CAN_Interface']['Kvaser']['name']
            self.__channel          =   conf['CAN_Interface']['Kvaser']['channel']
            self.__ipAddress        =   conf['CAN_Interface']['Kvaser']['ipAddress']
            self.__bitrate          =   int(conf['CAN_Interface']['Kvaser']['bitrate'])
        
        if interface == "AnaGate":  
            self.__interface        =   conf['CAN_Interface']['AnaGate']['name']
            self.__channel          =   conf['CAN_Interface']['AnaGate']['channel']
            self.__ipAddress        =   conf['CAN_Interface']['AnaGate']['ipAddress']
            self.__bitrate          =   int(conf['CAN_Interface']['AnaGate']['bitrate'])
        else:
            interface =None            
        self.logger.notice('... Loading all the configurations!')
         # Initialize default arguments
        if bitrate is None:
            bitrate = self.__bitrate
            
        bitrate = self._parseBitRate(bitrate)   
        # Initialize library and set connection parameters
        """:obj:`bool` : If communication is established"""
        self.__busOn = False  
        """:obj:`int` : Internal attribute for the channel index"""
        if channel is None:
            channel = self.__channel
        """:obj:`int` : Internal attribute for the bit rate"""
        self.__bitrate = bitrate
       
        """Internal attribute for the |CAN| channel"""
        self.__ch = None        
        """:obj:`int` : Internal attribute for the IP Address"""  
        if ipAddress is None:
            ipAddress = self.__ipAddress

        """Internal attribute for the |CAN| channel"""
        if set_channel:
            self.set_channelConnection(interface = self.__interface)
            self.logger.success(str(self))
                        
        """Internal attribute for the |CAN| channel"""
        self.__busOn = True
        self.__canMsgQueue = deque([], 2)
        self.__pill2kill = Event()
        self.__lock = Lock()
        #self.__kvaserLock = Lock()
        self.logger.success('... Done!')
        
    def __str__(self):
        if self.__interface == 'Kvaser':
            num_channels = canlib.getNumberOfChannels()
            for ch in range(0, num_channels):
                chdata = canlib.ChannelData(ch)
                chdataname = chdata.device_name
                chdata_EAN = chdata.card_upc_no
                chdata_serial = chdata.card_serial_no
                return f'Using {chdataname}, EAN: {chdata_EAN}, Serial No.:{chdata_serial}'
        else:
            ret = analib.wrapper.dllInfo()# DLL version
            return f'{self.__ch}, Bitrate:{self.__bitrate}'
        
    def _parseBitRate(self, bitrate):
        if self.__interface == 'Kvaser':
            if bitrate not in coc.CANLIB_BITRATES:
                raise ValueError(f'Bitrate {bitrate} not in list of allowed '
                                 f'values!')
            return coc.CANLIB_BITRATES[bitrate]
        else:
            if bitrate not in analib.constants.BAUDRATES:
                raise ValueError(f'Bitrate {bitrate} not in list of allowed '
                                 f'values!')
            return bitrate
    
    def confirmNodes(self, timeout=100):
        self.logger.notice('Checking node connections ...')
        for nodeId in self.__nodeIds:
            dev_t = self.sdoRead(nodeId, 0x1000, 0, timeout)
            if dev_t is None:
                self.logger.error(f'Node {nodeId} did not answer!')
                # self.__nodeIds.remove(nodeId)
            else:
                self.logger.info(f'Connection to node {nodeId} has been '
                                 f'verified.')
        self.logger.success('... Done!')
        
    def set_channelConnection(self, interface = None):
        self.logger.notice('Setting the channel ...')
        if interface == 'Kvaser':
            self.__ch = canlib.openChannel(self.__channel, canlib.canOPEN_ACCEPT_VIRTUAL)
            print(self.__bitrate)
            self.__ch.setBusParams(self.__bitrate)
            self.logger.notice('Going in \'Bus On\' state ...')
            self.__ch.busOn()
            self.__canMsgThread = Thread(target=self.readCanMessages)
        else:
            self.__ch = analib.Channel(ipAddress=self.__ipAddress, port= self.__channel, baudrate=self.__bitrate)
             
            
    def start_channelConnection(self, interface = None):
        self.logger.notice('Starting CAN Connection ...')
        if interface == 'Kvaser':
            self.__ch = canlib.openChannel(self.__channel, canlib.canOPEN_ACCEPT_VIRTUAL)
            self.__ch.setBusOutputControl(canlib.Driver.NORMAL)# New from tutorial
            self.logger.notice('Going in \'Bus On\' state ...')
            self.__ch.busOn()
            self.__canMsgThread = Thread(target=self.readCanMessages)
            self.__canMsgThread.start()
        else:
            if not self.__ch.deviceOpen:
                self.logger.notice('Reopening AnaGate CAN interface')
                self.__ch.openChannel() 
            if self.__ch.state != 'CONNECTED':
                self.logger.notice('Restarting AnaGate CAN interface.')
                self.__ch.restart()
            self.__cbFunc = analib.wrapper.dll.CBFUNC(self._anagateCbFunc())
            self.__ch.setCallback(self.__cbFunc)
            
    def stop(self):
        """Close |CAN| channel and stop the |OPCUA| server
        Make sure that this is called so that the connection is closed in a
        correct manner. When this class is used within a :obj:`with` statement
        this method is called automatically when the statement is exited.
        """
        with self.lock:
            self.cnt['Residual CAN messages'] = len(self.__canMsgQueue)
        self.logger.notice(f'Error counters: {self.cnt}')
        self.logger.warning('Stopping helper threads. This might take a '
                            'minute')
        self.logger.warning('Closing the CAN channel.')
        self.__pill2kill.set()
        if self.__busOn:
            if self.__interface == 'Kvaser':
                try:
                    self.__canMsgThread.join()
                except RuntimeError:
                    pass
                self.logger.warning('Going in \'Bus Off\' state.')
                self.__ch.busOff()
            else:
                pass
        self.__busOn = False
        self.__ch.close()
        self.logger.warning('Stopping the server.')

        
    #Setter and getter functions
    def set_subIndex(self,x):
        self.__subIndex = x
                
    def set_cobid(self, x):
        self.__cobid = x
    
    def set_dlc(self,x):
        self.__dlc = x
    
    def set_bytes(self,x):
        self.__bytes = x
        
    def set_interface(self, x):
        self.logger.success('Setting the interface to %s' %x)
        self.__interface = x
        self.__str__()
        
                
    def set_nodeIds(self,x):
        self.__nodeIds =x
    
    def set_channelNumber(self,x):
        self.__channel = x
    
    def set_ipAddress(self,x):
        self.__ipAddress = x
        
    def set_bitrate(self,bitrate):
        if self.__interface == 'Kvaser':
            self.stop()
            self.__bitrate = bitrate
            self.start()
        else:
            self.__bitrate = bitrate 
            
    def get_DllVersion(self):
        ret = analib.wrapper.dllInfo()
        return ret
    
    def get_nodeIds(self):
        return self.__nodeIds

    
    def get_bitrate(self):
        return self.__bitrate

    def get_ipAddress(self):
        """:obj:`str` : Network address of the AnaGate partner. Only used for
        AnaGate CAN interfaces."""
        if self.__interface == 'Kvaser':
            raise AttributeError('You are using a Kvaser CAN interface!')
        return self.__ipAddress
    def get_interface(self):
        """:obj:`str` : Vendor of the CAN interface. Possible values are
        ``'Kvaser'`` and ``'AnaGate'``."""
        return self.__interface
    
    def get_channelNumber(self):
        """:obj:`int` : Number of the crurrently used |CAN| channel."""
        return self.__channel

    def get_interfaceItems(self):
        return self.__interfaceItems
    
    def get_bitrate_items(self):
            return self.__bitrate_items
           
    def get_channelState(self,channel):
        return channel.state

    def get_subIndex(self):
        return self.__subIndex
    
    def get_cobid(self):
        return  self.__cobid
    
    def get_dlc(self):
        return self.__dlc

    def get_bytes(self):
        return self.__bytes 
        
    @property
    def lock(self):
        """:class:`~threading.Lock` : Lock object for accessing the incoming
        message queue :attr:`canMsgQueue`"""
        return self.__lock


    @property
    def canMsgQueue(self):
        """:class:`collections.deque` : Queue object holding incoming |CAN|
        messages. This class supports thread-safe adding and removing of
        elements but not thread-safe iterating. Therefore the designated
        :class:`~threading.Lock` object :attr:`lock` should be acquired before
        accessing it.

        The queue is initialized with a maxmimum length of ``1000`` elements
        to avoid memory problems although it is not expected to grow at all.

        This special class is used instead of the :class:`queue.Queue` class
        because it is iterable and fast."""
        return self.__canMsgQueue
    
    @property
    def kvaserLock(self):
        """:class:`~threading.Lock` : Lock object which should be acquired for
        performing read or write operations on the Kvaser |CAN| channel. It
        turned out that bad things can happen if that is not done."""
        return self.__kvaserLock

    @property
    def cnt(self):
        """:class:`~collections.Counter` : Counter holding information about
        quality of transmitting and receiving. Its contens are logged when the
        program ends."""
        return self.__cnt

    @property
    def pill2kill(self):
        """:class:`threading.Event` : Stop event for the message collecting
        method :meth:`readCanMessages`"""
        return self.__pill2kill
    
    #@property
    def channel(self):
        """Currently used |CAN| channel. The actual class depends on the used
        |CAN| interface."""
        return self.__ch
#     
    @property
    def bitRate(self):
        """:obj:`int` : Currently used bit rate. When you try to change it
        :func:`stop` will be called before."""
        if self.__interface == 'Kvaser':
            return self.__bitrate
        else:
            return self.__ch.baudrate
     
    @bitRate.setter
    def bitRate(self, bitrate):
        if self.__interface == 'Kvaser':
            self.stop()
            self.__bitrate = bitrate
            self.start()
        else:
            self.__ch.baudrate = bitrate     

    def sdoRead(self, nodeId, index, subindex, timeout=100,MAX_DATABYTES=8):
        """Read an object via |SDO|
    
        Currently expedited and segmented transfer is supported by this method.
        The function will writing the dictionary request from the master to the node then read the response from the node to the master
        The user has to decide how to decode the data.
        
        Parameters
        ----------
        nodeId : :obj:`int`
            The id from the node to read from
        index : :obj:`int`
            The Object Dictionary index to read from
        subindex : :obj:`int`
            |OD| Subindex. Defaults to zero for single value entries.
        timeout : :obj:`int`, optional
            |SDO| timeout in milliseconds
    
        Returns
        -------
        :obj:`list` of :obj:`int`
            The data if was successfully read
        :data:`None`
            In case of errors
        """
        self.logger.notice("Reading an object via |SDO|")
        SDO_TX =0x580  
        SDO_RX = 0x600
        interface = self.get_interface()
        self.start_channelConnection(interface=interface)
        if nodeId is None or index is None or subindex is None:
            self.logger.warning('SDO read protocol cancelled before it could begin.')         
            return None
        self.cnt['SDO read total'] += 1
        self.logger.info(f'Send SDO read request to node {nodeId}.')
        cobid = SDO_RX + nodeId
        msg = [0 for i in range(MAX_DATABYTES)]
        msg[0] = 0x40
        msg[1], msg[2] = index.to_bytes(2, 'little')
        msg[3] = subindex
        try:
            self.writeCanMessage(cobid, msg, timeout=timeout)
        except CanGeneralError:
            self.cnt['SDO read request timeout'] += 1
            return None
        # Wait for response
        t0 = time.perf_counter()
        messageValid = False
        while time.perf_counter() - t0 < timeout / 1000:
            with self.__lock:
                for i, (cobid_ret, ret, dlc, flag, t) in zip(range(len(self.__canMsgQueue)), self.__canMsgQueue):
                    messageValid = (dlc == 8 
                                    and cobid_ret == SDO_TX + nodeId
                                    and ret[0] in [0x80, 0x43, 0x47, 0x4b, 0x4f, 0x42] 
                                    and int.from_bytes([ret[1], ret[2]], 'little') == index
                                    and ret[3] == subindex)
                    if messageValid:
                        del self.__canMsgQueue[i]
                        break
            if messageValid:
                break
        else:
            self.logger.info(f'SDO read response timeout (node {nodeId}, index'
                             f' {index:04X}:{subindex:02X})')
            self.cnt['SDO read response timeout'] += 1
            return None
        # Check command byte
        if ret[0] == 0x80:
            abort_code = int.from_bytes(ret[4:], 'little')
            self.logger.error(f'Received SDO abort message while reading '
                              f'object {index:04X}:{subindex:02X} of node '
                              f'{nodeId} with abort code {abort_code:08X}')
            self.cnt['SDO read abort'] += 1
            return None
        nDatabytes = 4 - ((ret[0] >> 2) & 0b11) if ret[0] != 0x42 else 4
        data = []
        for i in range(nDatabytes):
            data.append(ret[4 + i])
        self.logger.info(f'Got data: {data}')
        return int.from_bytes(data, 'little')

    def writeCanMessage(self, cobid, msg, flag=0, timeout=None):
        """Combining writing functions for different |CAN| interfaces
        Parameters
        ----------
        cobid : :obj:`int`
            |CAN| identifier
        msg : :obj:`list` of :obj:`int` or :obj:`bytes`
            Data bytes
        flag : :obj:`int`, optional
            Message flag (|RTR|, etc.). Defaults to zero.
        timeout : :obj:`int`, optional
            |SDO| write timeout in milliseconds. When :data:`None` or not
            given an infinit timeout is used.
        """
        if self.__interface == 'Kvaser':
            if timeout is None:
                timeout = 0xFFFFFFFF
            frame = Frame(id_ = cobid, data = msg)#  from tutorial
            self.__ch.writeWait(frame,timeout)
        else:
            if not self.__ch.deviceOpen:
                self.logger.notice('Reopening AnaGate CAN interface')
            self.__ch.write(cobid, msg, flag)

    def readCanMessages(self):
        """Read incoming |CAN| messages and store them in the queue
        :attr:`canMsgQueue`.

        This method runs an endless loop which can only be stopped by setting
        the :class:`~threading.Event` :attr:`pill2kill` and is therefore
        designed to be used as a :class:`~threading.Thread`.
        """
        while not self.__pill2kill.is_set():
            try:
                
                if self.__interface == 'Kvaser':
                    frame = self.__ch.read()
                    cobid, data, dlc, flag, t = (frame.id, frame.data,
                                                 frame.dlc, frame.flags,
                                                 frame.timestamp)
                    if frame is None or (cobid == 0 and dlc == 0):
                        raise canlib.CanNoMsg
                else:
                    cobid, data, dlc, flag, t = self.__ch.getMessage()
                with self.__lock:
                     self.__canMsgQueue.appendleft((cobid, data, dlc, flag, t))
                self.dumpMessage(cobid, data, dlc, flag,t)
                return cobid, data, dlc, flag, t
            except (canlib.CanNoMsg, analib.CanNoMsg):
                pass
        
    #The following functions are to read the can messages
    def _anagateCbFunc(self):
        """Wraps the callback function for AnaGate |CAN| interfaces. This is
        neccessary in order to have access to the instance attributes.

        The callback function is called asychronous but the instance attributes
        are accessed in a thread-safe way.

        Returns
        -------
        cbFunc
            Function pointer to the callback function
        """
        def cbFunc(cobid, data, dlc, flag, handle):
            """Callback function.

            Appends incoming messages to the message queue and logs them.

            Parameters
            ----------
            cobid : :obj:`int`
                |CAN| identifier
            data : :class:`~ctypes.c_char` :func:`~cytpes.POINTER`
                |CAN| data - max length 8. Is converted to :obj:`bytes` for
                internal treatment using :func:`~ctypes.string_at` function. It
                is not possible to just use :class:`~ctypes.c_char_p` instead
                because bytes containing zero would be interpreted as end of
                data.
            dlc : :obj:`int`
                Data Length Code
            flag : :obj:`int`
                Message flags
            handle : :obj:`int`
                Internal handle of the AnaGate channel. Just needed for the API
                class to work.
            """
            data = ct.string_at(data, dlc)
            t = time.time()
            with self.__lock:
                self.__canMsgQueue.appendleft((cobid, data, dlc, flag, t))
            self.dumpMessage(cobid, data, dlc, flag,t)
        
        return cbFunc
    
    def dumpMessage(self, cobid, msg, dlc, flag, t):
        """Dumps a CANopen message to the screen and log file

        Parameters
        ----------
        cobid : :obj:`int`
            |CAN| identifier
        msg : :obj:`bytes`
            |CAN| data - max length 8
        dlc : :obj:`int`
            Data Length Code
        flag : :obj:`int`
            Flags, a combination of the :const:`canMSG_xxx` and
            :const:`canMSGERR_xxx` values
        t : obj'int'
        """

        if (flag & canlib.canMSG_ERROR_FRAME != 0):
            self.logger.error("***ERROR FRAME RECEIVED***")
        else:
            msgstr = '{:3X} {:d}   '.format(cobid, dlc)
            for i in range(len(msg)):
                msgstr += '{:02x}  '.format(msg[i])
            msgstr += '    ' * (8 - len(msg))
            st = datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S')
            msgstr += str(st)
            self.logger.info(coc.MSGHEADER)
            self.logger.info(msgstr)
                                                  
if __name__ == "__main__":
    pass