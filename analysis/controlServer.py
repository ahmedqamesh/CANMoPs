
from __future__ import annotations
from typing import *
import time
import sys
import os
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from pathlib import Path
from analysis import logger
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread, Event, Lock
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from graphics_Utils import dataMonitoring , menuWindow , childWindow ,logWindow, mainWindow
from analysis import analysis_utils , controlServer
from analysis import CANopenConstants as coc
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
rootdir = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root Directory [ALTERNATIVE root = analysis_utils.get_project_root()]
log = logger.setup_derived_logger('Control Server')
class ControlServer(object):
    
    def __init__(self, parent=None, 
                 config=None, interface= None,
                 bitrate =None, logdir = None,
                 console_loglevel=logging.NOTICE,
                 file_loglevel=logging.INFO,
                 channel =None,ipAddress =None, GUI = True,
                 logformat='%(asctime)s %(levelname)-8s %(message)s'):
        #super(ControlServer, self).__init__(parent)
        
        # Initialize logger
        logger.extend_logging()
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        """:obj:`~logging.Logger`: Main logger for this class"""
        self.logger.setLevel(logging.DEBUG)
        
        #log
        if logdir is None:
            logdir = os.path.join(rootdir, 'log')
            if not os.path.exists(logdir):
                    os.makedirs(logdir)
            
        ts = os.path.join(logdir,
                          time.strftime('%Y-%m-%d_%H-%M-%S_MoPs_daq.'))
        self.__fh = RotatingFileHandler(ts + 'log', backupCount=10,
                                        maxBytes=10 * 1024 * 1024)
        fmt = logging.Formatter(logformat)
        fmt.default_msec_format = '%s.%03d'
        self.__fh.setFormatter(fmt)
        cl.install(fmt=logformat, level=console_loglevel, isatty=True,
                   milliseconds=True)
        self.__fh.setLevel(file_loglevel)
           
        # Read configurations from a file
        self.logger.notice('Read configuration file ...')
        if config is None:
            conf = analysis_utils.open_yaml_file(file ="MoPS_daq_cfg.yml",directory =rootdir[:-8])
        
        # Interface
        if interface is None:
            interface = conf['CAN_Interface']['AnaGate']['name']           
        elif interface not in ['Kvaser', 'AnaGate']:
            raise ValueError(f'Possible CAN interfaces are "Kvaser" or '
                             f'"AnaGate" and not "{interface}".')
        self.__interface = interface
        
        #bitrate
        if bitrate is None:
            bitrate = conf['CAN_Interface']['AnaGate']['bitrate']
        bitrate = self._parseBitRate(bitrate)
        
        if ipAddress is None:
            ipAddress = conf['CAN_Interface']['AnaGate']['ipAddress']

        self.logger.success('... Done!')
       
        self.__busOn = False         
        """:obj:`int` : Internal attribute for the channel index"""
        if channel is None:
            channel = conf['CAN_Interface']['AnaGate']['channel']
        self.__channel = channel
        
        
        """:obj:`int` : Internal attribute for the bit rate""" 
        self.__bitrate = bitrate
       
        """Internal attribute for the |CAN| channel"""
        self.__ch = None
       
        if interface == 'Kvaser':
            self.__ch = canlib.openChannel(channel,
                                           canlib.canOPEN_ACCEPT_VIRTUAL)
            self.__ch.setBusParams(self.__bitrate)
            self.logger.notice('Going in \'Bus On\' state ...')
            self.__ch.busOn()
            self.__canMsgThread = Thread(target=self.readCanMessages)
        else:
            pass
            #self.__ch = analib.Channel(ipAddress, channel, baudrate=bitrate)
            #self.__cbFunc = analib.wrapper.dll.CBFUNC(self._anagateCbFunc())
            #self.__ch.setCallback(self.__cbFunc)
        self.logger.success(str(__name__))
        self.__busOn = True
        #self.__canMsgQueue = deque([], 10)
        #self.__pill2kill = Event()
        #self.__lock = Lock()
        #self.__kvaserLock = Lock()
        
        #if GUI is not None:
        self.logger.notice('Opening a graphical user Interface')
        self.start_graphicalInterface()
    
        # Scan nodes
        self.__nodeIds = []
        """:obj:`list` of :obj:`int` : Contains all |CAN| nodeIds currently
        present on the bus."""
        self.__myDCs = {}
        """:obj:`list` : |OPCUA| Object representation of all |DCS| Controllers
        that are currently on the |CAN| bus"""
        self.__mypyDCs = {}
        """:obj:`dict` : List of :class:`MyDCSController` instances which
        mirrors |OPCUA| adress space. Key is the node id."""
        self.__ADCTRIM = {}
        """:obj.`dict` : List of ADC trimming bits for each node id."""
        self.__MODTEMPCONN = {}
        """:obj:`dict` : List of module nummbers where the temperature is 
        connected for each node id"""
        self.__MODVOLTCONN = {}
        """:obj:`dict` : List of module nummbers where the voltage is connected
        for each node id"""
    

    def start_graphicalInterface(self):
        #qapp = QtWidgets.QApplication(sys.argv)
        app = mainWindow.MainWindow()
        #app.Ui_ApplicationWindow()
        #qapp.exec_()

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
    
    
    #Setter and getter functions
    def set_interface(self, x):
        print("set_interface",x)
        self.__interface = x
        self.get_interface()
        
    def get_interface(self):
        print("get_interface", self.__interface)
        return self.__interface
        
    @property
    def ipAddress(self):
        """:obj:`str` : Network address of the AnaGate partner. Only used for
        AnaGate CAN interfaces."""
        if self.__interface == 'Kvaser':
            raise AttributeError('You are using a Kvaser CAN interface!')
        return self.__ch.ipAddress        
    
    @property
    def interface(self):
        """:obj:`str` : Vendor of the CAN interface. Possible values are
        ``'Kvaser'`` and ``'AnaGate'``."""
        return self.__interface
    
    @property
    def lock(self):
        """:class:`~threading.Lock` : Lock object for accessing the incoming
        message queue :attr:`canMsgQueue`"""
        return self.__lock

    @property
    def channel(self):
        """Currently used |CAN| channel. The actual class depends on the used
        |CAN| interface."""
        return self.__ch

    @property
    def channelNumber(self):
        """:obj:`int` : Number of the rurrently used |CAN| channel."""
        return self.__channel

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

if __name__ == "__main__":
    pass