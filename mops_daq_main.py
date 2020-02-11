
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
from graphics_Utils import DataMonitoring , MenuWindow , ChildWindow ,LogWindow
from analysis import analysis_utils
from analysis import CANopenConstants as coc
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
rootdir = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root Directory [ALTERNATIVE root = analysis_utils.get_project_root()]
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, 
                 config=None, interface= None,
                 bitrate =None, logdir = None,
                 console_loglevel=logging.NOTICE,
                 file_loglevel=logging.INFO,
                 channel =None,ipAddress =None,
                 logformat='%(asctime)s %(levelname)-8s %(message)s'):
        super(ApplicationWindow, self).__init__(parent)
        
        # Initialize logger
        logger.extend_logging()
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        """:obj:`~logging.Logger`: Main logger for this class"""
        self.logger.setLevel(logging.DEBUG)
        
        #log
        if logdir is None:
            logdir = os.path.join(rootdir, 'log')
            
        ts = os.path.join(logdir,
                          time.strftime('%Y-%m-%d_%H-%M-%S_OPCUA_Server.'))
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
            conf = analysis_utils.open_yaml_file(file ="MoPS_daq_cfg.yml",directory =rootdir)
        
        # Initialize default arguments
        self.app_name = conf['Application']['name']
        
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
        self.logger.success(str(self))
        self.__busOn = True
        #self.__canMsgQueue = deque([], 10)
        #self.__pill2kill = Event()
        #self.__lock = Lock()
        #self.__kvaserLock = Lock()
        
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
    
    def Ui_ApplicationWindow(self):
        self.menu= MenuWindow.MenuBar()
        self.menu._createMenu(self)
        self.menu._createtoolbar(self)
        self.menu._createStatusBar(self)
        app_name = 'Online Monitor'
        # 1. Window settings
        self.setWindowTitle(self.app_name)
        #self.setGeometry(300, 300, 800, 400)
        self.resize(800, 600)
        
        # call widgets
        self.createTopLeftTabGroupBox()
        self.createTopRightGroupBox()
        self.createBottomRightGroupBox()
        self.createBottomLeftGroupBox()
        self.createProgressBar()

        # Creat a frame in the main menu for the gridlayout
        mainFrame = QFrame(self)
        mainFrame.setStyleSheet("QWidget { background-color: #eeeeec; }")
        mainFrame.setLineWidth(0.6)
        self.setCentralWidget(mainFrame)
        
        # SetLayout
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.topLeftTabGroupBox, 1, 0)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftGroupBox, 2, 0)
        mainLayout.addWidget(self.bottomRightGroupBox , 2, 1)
        mainLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        
        mainFrame.setLayout(mainLayout)
        # 3. Show
        self.show()
        return

    def createTopLeftTabGroupBox(self):
        # Define a group for the whole wedgit
        self.topLeftTabGroupBox = QGroupBox("Controller interface")
        # Define a frame for the figure
        plotframe = QFrame(self)
        plotframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        plotframe.setLineWidth(0.6)
        # Define a layout
        vLayout = QVBoxLayout()
        #comboBox and label for channel
        chLabel = QLabel("Channel", self)
        chLabel.setText("Controller")

        controllerLayout = QHBoxLayout()
        items = ["AnaGate","Kvaser","Others"]
        chComboBox = QComboBox(self)
        for item in items: chComboBox.addItem(item)
        chComboBox.activated[str].connect(self.set_interface)
        
        h , w = 50 , 25
        connectButton = QPushButton("")
        connectButton.clicked.connect(self.get_interface)  
        connectButton.setFixedWidth(w)
        connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        connectButton.setIcon(icon)
        connectButton.setCheckable(True)

        #connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        
        controllerLayout.addWidget(chComboBox)
        controllerLayout.addWidget(connectButton)
        
        vLayout.addStretch(1)
        vLayout.addWidget(chLabel)
        vLayout.addLayout(controllerLayout)
        self.setCentralWidget(plotframe)
        plotframe.setLayout(vLayout)
        self.topLeftTabGroupBox.setLayout(vLayout)
    
    def set_interface(self, x):
        self.__interface = x
        
    def get_interface(self):
        print(self.__interface)
        return self.__interface

    def createTopRightGroupBox(self):
        # Define a group for the whole wedgit
        self.topRightGroupBox = QGroupBox("Data Monitoring")
        # Define a frame for the figure
        plotframe = QFrame(self)
        plotframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        plotframe.setLineWidth(0.6)
        # Define a layout
        plotLayout = QVBoxLayout()
        # add the figure to the layout
        Fig = DataMonitoring.LiveMonitoringData()
        plotLayout.addStretch(1)
        plotLayout.addWidget(Fig)
        self.setCentralWidget(plotframe)
        plotframe.setLayout(plotLayout)
        self.topRightGroupBox.setLayout(plotLayout)

    def createBottomRightGroupBox(self):
        self.bottomRightGroupBox = QGroupBox("Log Viewer")
        logframe = QFrame(self)
        logframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        logframe.setLineWidth(0.6)
        logEdit= LogWindow.LoggerDialog()
        logLayout = QVBoxLayout()
        logLayout.addWidget(logEdit)
        self.setCentralWidget(logframe)
        #self.setLayout(logLayout)
        self.bottomRightGroupBox.setLayout(logLayout)    

    def createBottomLeftGroupBox(self):
        self.bottomLeftGroupBox = QGroupBox("Group 3")
        self.bottomLeftGroupBox.setCheckable(True)
        self.bottomLeftGroupBox.setChecked(True)

        lineEdit = QLineEdit('s3cRe7')
        lineEdit.setEchoMode(QLineEdit.Password)

        spinBox = QSpinBox(self.bottomLeftGroupBox)
        spinBox.setValue(50)

        dateTimeEdit = QDateTimeEdit(self.bottomLeftGroupBox)
        dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Horizontal, self.bottomLeftGroupBox)
        slider.setValue(40)

        scrollBar = QScrollBar(Qt.Horizontal, self.bottomLeftGroupBox)
        scrollBar.setValue(60)

        dial = QDial(self.bottomLeftGroupBox)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(lineEdit, 0, 0, 1, 2)
        layout.addWidget(spinBox, 1, 0, 1, 2)
        layout.addWidget(dateTimeEdit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scrollBar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottomLeftGroupBox.setLayout(layout)

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)
        
    def joystick_in(self):
        print("In")
    def joystick_out(self):
        print("Out")
    def joystick_right(self):
        print("Right")
    def joystick_left(self):
        print("Left")
    def joystick_middle(self):
        print("middle")
    def joystick_up(self):
        print("Up")
    def joystick_down(self):
        print("Down")
     
    def openWindow(self):
        self.window = QMainWindow()
        self.ui = ChildWindow.Ui_ChildWindow()
        self.ui.settingChannel(self.window)
        self.window.show()


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
if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.Ui_ApplicationWindow()
    qapp.exec_()
