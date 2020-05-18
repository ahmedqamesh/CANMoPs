
from __future__ import annotations
import signal
from typing import *
import sched, time
import sys
import os
from os import chdir
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
import pyqtgraph as pg
from PyQt5 import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread, Event, Lock
import matplotlib as mpl
import numpy as np
from random import randint
from matplotlib.figure import Figure
from graphics_Utils import dataMonitoring , menuWindow , logWindow, childWindow
from analysis import analysis_utils , controlServer
from analysis import CANopenConstants as coc
import binascii
# Third party modules
import coloredlogs as cl
import verboselogs
rootdir = os.path.dirname(os.path.abspath(__file__)) 


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None,
                 device_config=["PSPP_cfg.yml"],
                 main_config=["main_cfg.yml"]):
        super(MainWindow, self).__init__(parent)
        self.__device_config = device_config            
        self.logger = logging.getLogger(__name__)
        self.child = childWindow.ChildWindow() 
        # Start with default settings
        self.config_dir = "config/"
        
        # Read configurations from a file    
        conf = analysis_utils.open_yaml_file(file=self.config_dir + "main_cfg.yml", directory=rootdir[:-14])
        self.__appName = conf["Application"]["app_name"] 
        self.__appVersion = conf['Application']['app_version']
        self.__appIconDir = conf["Application"]["app_icon_dir"]        
        self._index_items = conf["default_values"]["index_items"]
        self.__interfaceItems = conf['default_values']["interface_items"]        
        self.__bitrate_items = conf['default_values']['bitrate_items']
        self.__bytes = conf["default_values"]["bytes"]
        self.__subIndex = conf["default_values"]["subIndex"]
        self.__cobid = conf["default_values"]["cobid"]
        self.__dlc = conf["default_values"]["dlc"]
        self.__nodeIds = conf["CAN_settings"]["nodeIds"]
        self.__devices = conf["Devices"]
        self.__interface =  None
        self.__channel = None
        self.__ipAddress =  None
        self.__bitrate = None
        self.configureDeviceBox(None)
        self.index_description_items = None
        self.subIndex_description_items = None
        self.__response = None
        self.n_channels = np.arange(3, 35)
        self.server = None
         
        # Show a textBox
        self.textBoxWindow()
        
        self.MainWindow = QMainWindow()
        
    def devices_configuration(self, dev):
        self.__appName = dev["Application"]["device_name"] 
        self.__version = dev['Application']['device_version']
        self.__icon_dir = dev["Application"]["icon_dir"]
        self.__nodeIds = dev["Application"]["nodeIds"]
        self.__dictionary_items = dev["Application"]["index_items"]
        self.__index_items = list(self.__dictionary_items.keys())
        self.__adc_channels_reg = dev["adc_channels_reg"]["adc_channels"]
        self.__adc_index = dev["adc_channels_reg"]["adc_index"]
        return  self.__appName, self.__version, self.__icon_dir, self.__nodeIds, self.__dictionary_items, self.__adc_channels_reg, self.__adc_index
    
    def Ui_ApplicationWindow(self):
        # self.trendWindow()
        self.menu = menuWindow.MenuBar(self)
        self.menu._createMenu(self)
        self._createtoolbar(self)
        self.menu._createStatusBar(self)
        # 1. Window settings
        self.setWindowTitle(self.__appName + "_" + self.__appVersion)
        self.setWindowIcon(QtGui.QIcon(self.__appIconDir))
        self.adjustSize()
        # call widgets
        self.createProgressBar()
        self.defaultWindow()
        # Create a frame in the main menu for the gridlayout
        mainFrame = QFrame(self)
        mainFrame.setLineWidth(0.6)
        self.setCentralWidget(mainFrame)
    
        line = QFrame()
        line.setGeometry(QRect(320, 150, 118, 3))
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        
        # SetLayout
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.interfaceComboBox, 0, 0)
        self.mainLayout.addWidget(self.connectButton, 0, 1)
        self.mainLayout.addLayout(self.GridLayout, 1, 0)
        self.mainLayout.addWidget(self.textBox, 2, 0)
        self.mainLayout.addWidget(line, 3, 0)
        self.mainLayout.addLayout(self.HLayout, 4, 0)
        # mainLayout.addWidget(self.progressBar,2,0)
        mainFrame.setLayout(self.mainLayout)
        # 3. Show
        self.show()
        return
            
    def textBoxWindow(self):
        self.textBox = QTextEdit()
        self.textBox.setTabStopWidth(12) 
        self.textBox.setReadOnly(True)
        
    def defaultWindow(self):
        __interfaceItems = self.__interfaceItems
        self.interfaceComboBox = QComboBox(self)
        def get_interface_combo():
            interface = self.interfaceComboBox.currentText()
            self.set_interface(interface)
            return interface
        for item in __interfaceItems[1:]: self.interfaceComboBox.addItem(item)
        self.interfaceComboBox.activated[str].connect(self.set_interface)
        
        self.interfaceComboBox.setStatusTip('Select the connected interface')
        self.connectButton = QPushButton("")
        self.connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal, QIcon.On)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'), QIcon.Normal, QIcon.Off)
        self.connectButton.setIcon(icon)
        self.connectButton.setStatusTip('Connect the interface and set the channel')
        self.connectButton.setCheckable(True)
        
        self.connectButton.clicked.connect(get_interface_combo)
        self.connectButton.clicked.connect(self.set_connect)
        
        self.GridLayout = QGridLayout()
        nodeLabel = QLabel("NodeId", self)
        nodeLabel.setText("NodeId ")
        nodeitems = list(map(str, self.__nodeIds))
        nodeComboBox = QComboBox(self)
        for item in nodeitems: nodeComboBox.addItem(item)
        nodeComboBox.activated[str].connect(self.set_nodeId)
        nodeComboBox.setStatusTip('NodeIds as defined in the main_cfg.yml file')
        indexLabel = QLabel("Index", self)
        indexLabel.setText("   Index   ")
        self.mainIndexTextBox = QLineEdit("0x1000", self)
        # self.indexTextBox.textChanged.connect(self.set_index)
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        self.mainSubIndextextbox = QLineEdit(self.__subIndex, self)
        # self.subIndextextbox.textChanged.connect(self.set_subIndex)
                
        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.setStatusTip('Send CAN message')
        self.startButton.clicked.connect(self.applyLineEditChanges) 
        self.startButton.clicked.connect(self.send_sdo_can)                 
                   
        self.GridLayout.addWidget(nodeLabel, 0, 0)
        self.GridLayout.addWidget(nodeComboBox, 1, 0)   
        self.GridLayout.addWidget(indexLabel, 0, 1)
        self.GridLayout.addWidget(self.mainIndexTextBox, 1, 1)
        self.GridLayout.addWidget(subIndexLabel, 0, 2)
        self.GridLayout.addWidget(self.mainSubIndextextbox, 1, 2)       
        self.GridLayout.addWidget(self.startButton, 1, 3)

    def applyLineEditChanges(self):
        self.set_index(self.mainIndexTextBox.text())
        self.set_subIndex(self.mainSubIndextextbox.text())

    def configureDeviceBox(self, conf):
        self.HLayout = QHBoxLayout()
        deviceLabel = QLabel("Configure Device", self)
        self.deviceButton = QPushButton("")
        self.deviceButton.setStatusTip('Choose the configuration yaml file')
        if self.__devices is None:
            deviceLabel.setText("Configure Device")
            self.deviceButton.setIcon(QIcon('graphics_Utils/icons/icon_question.png'))
            self.deviceButton.clicked.connect(self.update_device_menu)
        else:
            deviceLabel.setText("Configured Device [" + self.__devices[0] + "]")
            self.update_device_menu()
        self.HLayout.addWidget(deviceLabel)
        self.HLayout.addWidget(self.deviceButton)

    def update_device_menu(self):
        if self.__devices is None:
            conf = self.child.open()
        else:
            conf = analysis_utils.open_yaml_file(file=self.config_dir + self.__devices[0] + "_cfg.yml", directory=rootdir[:-14])
        self.__devices.append(conf["Application"]["device_name"])
        self.deviceButton.deleteLater()
        self.HLayout.removeWidget(self.deviceButton)
        self.deviceButton = QPushButton("")
        appName, version, icon_dir, nodeIds, dictionary_items, adc_channels_reg, adc_index = self.devices_configuration(conf)
        self.set_adc_channels_reg(adc_channels_reg)
        self.set_adc_index(adc_index)
        self.set_appName(appName)
        self.set_version(version)
        self.set_icon_dir(icon_dir)
        self.set_nodeIds(nodeIds)
        self.set_dictionary_items(dictionary_items)                
        self.deviceButton.setIcon(QIcon(self.get_icon_dir()))
        self.deviceButton.clicked.connect(self.deviceWindow)
        self.HLayout.addWidget(self.deviceButton)

    def trendChildWindow(self, childWindow =  None, index =  None):
        childWindow.setObjectName("TrendingWindow")
        childWindow.setWindowTitle("Trending Window")
        childWindow.resize(900, 500)  # w*h
        logframe = QFrame(self)
        logframe.setLineWidth(0.6)
        childWindow.setCentralWidget(logframe)
        trendLayout = QHBoxLayout()
        self.WindowGroupBox = QGroupBox("")
        self.Fig = self.compute_initial_figure(index =int(str(index)))
        self.initiate_trend_timer(index =int(str(index)))
        self.Fig.setStyleSheet("background-color: black;"
                                        "color: black;"
                                        "border-width: 1.5px;"
                                        "border-color: black;"
                                        "margin:0.0px;"
                                        # "border: 1px "
                                        "solid black;")

        self.distribution = dataMonitoring.LiveMonitoringDistribution()
        #trendLayout.addWidget(self.distribution)
        trendLayout.addWidget(self.Fig)
        
        self.WindowGroupBox.setLayout(trendLayout)
        logframe.setLayout(trendLayout) 

    def compute_initial_figure(self, index =  None):                   
        self.graphWidget = pg.PlotWidget(background="w")
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(2))  # 100 time points
        self.y = [0 for _ in range(2)]  # 100 data points
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0), width=3), name= "channel%i"%index)
        # Add Title
        self.graphWidget.setTitle("Online data monitoring")
        # Add Axis Labels
        self.graphWidget.setLabel('left', "<span style=\"color:black; font-size:15px\">CAN Data</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:black; font-size:15px\">Time [s]</span>")

        # Add legend
        self.graphWidget.addLegend()
        
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.getAxis("bottom").setStyle(tickTextOffset=10)
        # Set Range
        # self.graphWidget.setXRange(0, 100, padding=0)
        # self.graphWidget.setYRange(00, 55, padding=0)
        return self.graphWidget
    
    def update_trending_figure(self,index =None):
        print("Ch",self.n_channels[index],"is",self.adc_converted[index])
        data_line = self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0), width=3))
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        data = self.adc_converted[index] #np.random.randint(1000,2500)
        self.y = self.y[1:]  # Remove the first 
        self.y.append(data)  # Add a new random value.
        data_line.setData(self.x, self.y)  # Update the data.

    # Functions to run
    def showAdcChannelWindow(self):
        self.adcWindow = QMainWindow()
        #dataMonitoring.ADCMonitoringData(self.adcWindow, interface=self.get_interface())
        self.adcMonitoringData(self.adcWindow)
        self.adcWindow.show()
        
    def canMessageWindow(self):
        self.MessageWindow = QMainWindow()
        self.canMessageChildWindow(self.MessageWindow)
        self.MessageWindow.show()

    def canDumpMessageWindow(self):
        self.MessageDumpWindow = QMainWindow()
        self.canDumpMessageChildWindow(self.MessageDumpWindow)
        self.MessageDumpWindow.show()
        
    def canSettingsWindow(self):
        MainWindow = QMainWindow()
        self.canSettingsChildWindow(MainWindow)
        MainWindow.show()

    def trendWindow(self):
        trend = QMainWindow(self)
        sending_button = self.sender()
        self.trendChildWindow(childWindow = trend, index = sending_button.objectName())
        trend.show()
            
    def deviceWindow(self):
        self.deviceWindow = QMainWindow()
        self.deviceChildWindow(self.deviceWindow)
        self.deviceWindow.show()
        
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

    def set_connect(self):
        if self.connectButton.isChecked():
            interface = self.get_interface()
            self.server = controlServer.ControlServer(interface =interface, set_channel =True)
            #self.server.set_channelConnection(interface=interface)
        else:
           self.server.stop()

    def set_all(self):   
        bitrate = self.get_bitrate()
        interface = self.get_interface()
        if interface != "Kvaser":
            ipAddress = self.get_ipAddress()
            self.server.set_ipAddress(ipAddress)
        self.server.set_bitrate(bitrate)
        self.server.set_interface(interface)
        self.server.set_channelConnection(interface=interface)
        
    '''
    Define can communication messages
    '''
               
    def send_sdo_can(self, trending=False, print_sdo=True):
        index = int(self.get_index(), 16)
        subIndex = int(self.get_subIndex(), 16)
        nodeId = self.__nodeIds[0]
        try:
            if self.server == None: 
                self.server = controlServer.ControlServer()
                interface = self.get_interface()
                self.server.set_interface(interface)
                self.server.set_channelConnection(interface=interface)
            self.__response = self.server.sdoRead(nodeId, index, subIndex, 3000)
            self.set_data_point(self.__response)
            if print_sdo == True:
                self.print_sdo_can(nodeId=nodeId, index=index, subIndex=subIndex, response_from_node=self.__response)
        except Exception:
            pass
        
    def error_message(self, text=False, checknode =False):
        if checknode:
            self.server.confirmNodes()
        if text: 
            QMessageBox.about(self, "Error Message", text)
     
    def print_sdo_can(self, nodeId=None , index=None, subIndex=None, response_from_node="response_from_node"):
        # printing the read message with cobid = SDO_RX + nodeId
        MAX_DATABYTES = 8
        msg = [0 for i in range(MAX_DATABYTES)]
        msg[1], msg[2] = index.to_bytes(2, 'little')
        msg[3] = subIndex
        msg[0] = 0x40
        self.set_textBox_message(comunication_object="SDO_RX", msg=str(msg))
        # printing response 
        self.set_textBox_message(comunication_object="SDO_TX", msg=str(response_from_node))
        # print decoded response
        decoded_response = f'{response_from_node:03X}\n-----------------------------------------------'
        self.set_textBox_message(comunication_object="Decoded", msg=decoded_response)
            
    def send_can(self):
        try:
            textboxValue = [self.ByteTextbox[i] for i in np.arange(len(self.ByteTextbox))]
            for i in np.arange(len(self.ByteTextbox)):
                textboxValue[i] = self.ByteTextbox[i].text()
            cobid = int(self.cobidtextbox.text(), 16)
            bytes = list(map(int, textboxValue))
            # Send the can Message
            self.set_textBox_message(comunication_object="SDO_RX", msg=str(bytes))
            self.server.writeCanMessage(cobid, bytes, flag=0, timeout=1000)
            # receive the message
            self.read_can()
        except Exception:
            self.error_message(text="Make sure that the CAN interface is connected")

    def read_can(self):
        cobid, data, dlc, flag, t = self.server.readCanMessages()
        self.set_textBox_message(comunication_object="SDO_TX", msg=str(data.hex()))
 
    def _createStatusBar(self, childwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        childwindow.setStatusBar(status)

    '''
    Define all child windows
    '''

    def canSettingsChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("CANSettings")
        ChildWindow.setWindowTitle("CAN Settings")
        ChildWindow.resize(310, 600)  # w*h
        MainLayout = QGridLayout()
        
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        # Define First Group
        FirstGroupBox = QGroupBox("Bus Statistics")
        FirstGridLayout = QGridLayout()
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)
        
        FirstGridLayout.addWidget(clear_button, 0, 0)
        FirstGroupBox.setLayout(FirstGridLayout)
        
        # Define the second group
        SecondGroupBox = QGroupBox("Bus Configuration")
        SecondGridLayout = QGridLayout()        
        # comboBox and label for channel
        chLabel = QLabel("CAN Channel:", ChildWindow)
        chLabel.setText("CAN Channel:")
        controllerLayout = QHBoxLayout()
        __interfaceItems = self.__interfaceItems
        interfaceComboBox = QComboBox(ChildWindow)
        for item in __interfaceItems: interfaceComboBox.addItem(item)
        interfaceComboBox.activated[str].connect(self.set_interface)
        controllerLayout.addWidget(interfaceComboBox)
        
        # Another group will be here for Bus parameters
        self.BusParametersGroupBox()
        modeLabel = QLabel("CAN Mode:", ChildWindow)
        modeLabel.setText("CAN Mode:")
        modeitems = ["CAN"]
        modeComboBox = QComboBox(ChildWindow)
        for item in modeitems: modeComboBox.addItem(item)
        # modeComboBox.activated[str].connect(self.clicked)

        # FirstButton
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)

        HGridLayout = QGridLayout()  
        set_button = QPushButton("Set in all")
        set_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        set_button.clicked.connect(self.set_all)

        setLabel = QLabel("Set same bit rate in all CAN controllers", ChildWindow)
        setLabel.setText("Set same bit rate in all CAN controllers")
        
        HGridLayout.addWidget(set_button, 0, 0)
        HGridLayout.addWidget(setLabel, 0, 1)
        
        SecondGroupBox.setLayout(SecondGridLayout)
        SecondGridLayout.addWidget(chLabel, 0, 0)
        SecondGridLayout.addLayout(controllerLayout, 1, 0)
        SecondGridLayout.addWidget(modeLabel, 2, 0)
        SecondGridLayout.addWidget(modeComboBox, 3, 0)
        
        def _interfaceParameters():
            SecondGridLayout.removeWidget(self.SubSecondGroupBox)
            self.SubSecondGroupBox.deleteLater()
            self.SubSecondGroupBox = None
            interface = self.get_interface()
            self.BusParametersGroupBox(ChildWindow=ChildWindow , interface=interface)
            SecondGridLayout.addWidget(self.SubSecondGroupBox, 4, 0)        

        SecondGridLayout.addLayout(HGridLayout, 5, 0)
        interfaceComboBox.activated[str].connect(_interfaceParameters)
        # Define Third Group
        ThirdGroupBox = QGroupBox("Bus Status")
        ThirdGridLayout = QGridLayout()
        
        go_button = QPushButton("Go On Bus")
        go_button.setIcon(QIcon('graphics_Utils/icons/icon_reset.png'))
        go_button.clicked.connect(ChildWindow.close)
        
        ThirdGridLayout.addWidget(go_button, 0, 0)
        ThirdGroupBox.setLayout(ThirdGridLayout)
        MainLayout.addWidget(FirstGroupBox, 0, 0)
        MainLayout.addWidget(SecondGroupBox, 1, 0)
        MainLayout.addWidget(ThirdGroupBox, 2, 0)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)        

    def BusParametersGroupBox(self, ChildWindow=None, interface="Others"):
        # Define subGroup
        self.SubSecondGroupBox = QGroupBox("Bus Parameters")
        SubSecondGridLayout = QGridLayout()
        firstLabel = QLabel("firstLabel", ChildWindow)
        secondLabel = QLabel("secondLabel", ChildWindow)
        thirdLabel = QLabel("thirdLabel", ChildWindow)
        firstComboBox = QComboBox(ChildWindow)
        if (interface == "Kvaser"):
            firstLabel.setText("")
            firstItems = self.get_bitrate_items() 
            for item in firstItems: firstComboBox.addItem(item)

            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            secondItems = ["1", "2", "3", "4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = self.get_bitrate_items()
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            
        if (interface == "AnaGate"):
            firstLabel.setText("IP address")
            ipAddress = self.get_ipAddress()
            self.firsttextbox = QLineEdit(ipAddress, ChildWindow)
            self.firsttextboxvalue = self.firsttextbox.text()

            secondLabel.setText("SJW:")
            secondItems = ["1", "2", "3", "4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            
            thirdLabel.setText("Bit Timing:")
            thirdItems = self.get_bitrate_items()
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            SubSecondGridLayout.addWidget(self.firsttextbox, 0, 1)
            
        if (interface == "Others"):        
            firstLabel.setText("Speed:")
            firstItems = [""]
            firstComboBox = QComboBox(ChildWindow)
            for item in firstItems: firstComboBox.addItem(item)
            # firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("")
            seconditems = [""]
            secondComboBox = QComboBox(ChildWindow)
            for item in seconditems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("")
            thirdItems = [""]
            thirdComboBox = QComboBox(ChildWindow)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            for item in thirdItems: thirdComboBox.addItem(item)
            SubSecondGridLayout.addWidget(firstComboBox, 0, 1)
        else:
            pass   
        SubSecondGridLayout.addWidget(firstLabel, 0, 0)
        SubSecondGridLayout.addWidget(secondLabel, 1, 0)
        SubSecondGridLayout.addWidget(secondComboBox, 1, 1)
        SubSecondGridLayout.addWidget(thirdLabel, 2, 0)
        SubSecondGridLayout.addWidget(thirdComboBox, 2, 1)
        self.SubSecondGroupBox.setLayout(SubSecondGridLayout)
        
    def canMessageChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("CANMessage")
        ChildWindow.setWindowTitle("CAN Message")
        ChildWindow.resize(310, 600)  # w*h
        MainLayout = QGridLayout()
        
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        # Define First Group
        FirstGroupBox = QGroupBox("")
        # comboBox and label for channel
        FirstGridLayout = QGridLayout() 
        cobidLabel = QLabel("CAN Identifier", ChildWindow)
        cobidLabel.setText("CAN Identifier:")
        self.cobidtextbox = QLineEdit(self.__cobid, ChildWindow)

        channelLabel = QLabel("Channel        :", ChildWindow)
        channelLabel.setText("Channel         :")
        canitems = ["CAN1"]
        canComboBox = QComboBox(ChildWindow)
        for item in canitems: canComboBox.addItem(item)
        canComboBox.activated[str].connect(self.clicked)
        dlcLabel = QLabel("DLC            :", ChildWindow)
        dlcLabel.setText("DLC            :")
        dlctextbox = QLineEdit(self.__dlc, ChildWindow)
        dlctextboxValue = dlctextbox.text()
        self.set_dlc(dlctextboxValue)
        
        FirstGridLayout.addWidget(cobidLabel, 0, 0)
        FirstGridLayout.addWidget(self.cobidtextbox, 0, 1)
                
        FirstGridLayout.addWidget(channelLabel, 1, 0)
        FirstGridLayout.addWidget(canComboBox, 1, 1)        
        
        FirstGridLayout.addWidget(dlcLabel, 2, 0)
        FirstGridLayout.addWidget(dlctextbox, 2, 1)  
             
        FirstGroupBox.setLayout(FirstGridLayout) 
        
        SecondGroupBox = QGroupBox("Message Data")
        # comboBox and label for channel
        SecondGridLayout = QGridLayout()
        ByteList = ["Byte0 :", "Byte1 :", "Byte2 :", "Byte3 :", "Byte4 :", "Byte5 :", "Byte6 :", "Byte7 :"] 
        LabelByte = [ByteList[i] for i in np.arange(len(ByteList))]
        self.ByteTextbox= [ByteList[i] for i in np.arange(len(ByteList))]        
        for i in np.arange(len(ByteList)):
            LabelByte[i] = QLabel(ByteList[i], ChildWindow)
            LabelByte[i].setText(ByteList[i])
            self.ByteTextbox[i] = QLineEdit(self.__bytes[i], ChildWindow)
            if i <= 3:
                SecondGridLayout.addWidget(LabelByte[i], i, 0)
                SecondGridLayout.addWidget(self.ByteTextbox[i], i, 1)
            else:
                SecondGridLayout.addWidget(LabelByte[i], i - 4, 4)
                SecondGridLayout.addWidget(self.ByteTextbox[i], i - 4, 5)
        
        SecondGroupBox.setLayout(SecondGridLayout) 
        
        HBox = QHBoxLayout()
        send_button = QPushButton("Send")
        send_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        send_button.clicked.connect(self.send_can)
        
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_Utils/icons/icon_close.jpg'))
        close_button.clicked.connect(ChildWindow.close)

        HBox.addWidget(send_button)
        HBox.addWidget(close_button)
                 
        MainLayout.addWidget(FirstGroupBox , 0, 0)
        MainLayout.addWidget(SecondGroupBox , 1, 0)
        MainLayout.addLayout(HBox , 2, 0)

        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def canDumpMessageChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("CANDump")
        ChildWindow.setWindowTitle("CAN output window")
        ChildWindow.resize(700, 600)  # w*h        
        MainLayout = QGridLayout()
        
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        # Define First Group
        FirstGroupBox = QGroupBox("")
        # comboBox and label for channel
        FirstGridLayout = QGridLayout() 
        run_label = QLabel("StartRun", ChildWindow)
        run_label.setText(" Start Run")
        run_button = QPushButton()
        run_button.setIcon(QIcon('graphics_Utils/icons/icon_right.jpg'))
        
    
             
        stop_label = QLabel("Stop", ChildWindow)
        stop_label.setText(" Stop")
        stop_button = QPushButton()
        stop_button.setIcon(QIcon('graphics_Utils/icons/icon_stop.png'))
        

        random_label = QLabel("Randomize", ChildWindow)
        random_label.setText("Randomize")
        random_button = QPushButton()
        random_button.setIcon(QIcon('graphics_Utils/icons/icon_random.png'))
        
        FirstGridLayout.addWidget(run_label, 1, 0)
        FirstGridLayout.addWidget(stop_label, 1, 1)
        FirstGridLayout.addWidget(random_label, 1, 2)
                
        FirstGridLayout.addWidget(run_button, 0, 0)
        FirstGridLayout.addWidget(stop_button, 0, 1)        
        FirstGridLayout.addWidget(random_button, 0, 2)
        
        FirstGroupBox.setLayout(FirstGridLayout) 
        
        SecondGroupBox = QGroupBox("")
        SecondGridLayout = QGridLayout()
        ByteList = [" Chn", "  Id", " Flg", " DLC", "D0--D1--D2--D3--D4--D5--D6--D7", " Time"]
        self.textOutputBox= [ByteList[i] for i in np.arange(len(ByteList))] 
        textOutputLabel= [ByteList[i] for i in np.arange(len(ByteList))]        
        for i in np.arange(len(ByteList)):
            self.textOutputBox[i]= QTextEdit("")
            textOutputLabel[i]= QLabel(ByteList[i])
            if i == 0 or i ==1  or i ==2:
                self.textOutputBox[i].setFixedWidth(10) 
            if i == 3:
                self.textOutputBox[i].setFixedWidth(20) 
            if i == 4:
                self.textOutputBox[i].setFixedWidth(210)
            else:
                self.textOutputBox[i].setFixedWidth(60)
            self.textOutputBox[i].setTabStopWidth(12) 
            self.textOutputBox[i].setReadOnly(True)
            SecondGridLayout.addWidget(textOutputLabel[i], 0,i)
            SecondGridLayout.addWidget(self.textOutputBox[i], 1,i)
        SecondGroupBox.setLayout(SecondGridLayout) 
        SecondGroupBox.setStyleSheet("background-color: white ; border-color: white; border-style: outset;border-width: 1px ")
 
        run_button.clicked.connect(self.start_dumptimer)
        stop_button.clicked.connect(self.stop_dumptimer)    
        random_button.clicked.connect(self.dump_can) 
        
        HBox = QHBoxLayout()
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_Utils/icons/icon_close.jpg'))
        close_button.clicked.connect(self.stop_dumptimer)
        close_button.clicked.connect(ChildWindow.close)
        HBox.addWidget(close_button)
        
        #MainLayout.addWidget(FirstGroupBox , 0, 0)
        MainLayout.addWidget(SecondGroupBox , 1, 0)
        MainLayout.addLayout(HBox , 2, 0)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def updateCanDump(self,TIMEOUT = 2):
        ByteList = [" Chn", "Id", "Flg", "DLC", "D0--D1--D2--D3--D4--D5--D6--D7", "Time"]
        def timeout_handler(signum, frame):
            try:
                raise TimeoutException
            except Exception:
                pass
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT)    
        try:
            cobid, data, dlc, flag, t = self.server.readCanMessages()
            channel = self.server.get_channelNumber()
            data = int.from_bytes(data, byteorder=sys.byteorder)
            b1,b2,b3,b4,b5,b6,b7, b8 = data.to_bytes(8, 'little') 
            for i in np.arange(len(ByteList)):
                result = [channel, cobid,str(flag),dlc, f'{b1:02x}   {b2:02x}   {b3:02x}   {b4:02x}   {b5:02x}  {b6:02x}   {b7:02x}   {b8:02x}',t]
                self.textOutputBox[i].append(str(result[i]))
                self.textOutputBox[i].append("  ")    
        except Exception:
            pass
    
    def start_dumptimer(self, period=1000):
        self.outtimer = QtCore.QTimer(self)
        self.outtimer.start(period)
        self.outtimer.timeout.connect(self.updateCanDump)     
    
    
    def stop_dumptimer(self):
        try:
            self.outtimer.stop()
        except Exception:
            pass
            
    def dump_can(self,  TIMEOUT = 5):
        def timeout_handler(signum, frame):
            try:
                raise TimeoutException
            except Exception:
                pass
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT)    
        try:
            self.server.readCanMessages()
        except Exception:
            self.error_message(text ="Make sure that the controller is connected")
        
    def random_can(self): 
        SDO_RX = 0x600
        Byte0= cmd = 0x40 #Defines a read (reads data only from the node) dictionary object in CANOPN standard
        index = np.random.randint(1000,2500)
        Byte1, Byte2 = index.to_bytes(2, 'little')
        Byte3 = subindex = np.random.randint(0,8)
        try:
            self.server.set_channelConnection(interface =self.get_interface())
            NodeIds = self.server.get_nodeIds()
            self.server.writeCanMessage(SDO_RX + NodeIds[0], [Byte0,Byte1,Byte2,Byte3,0,0,0,0], flag=0, timeout=3000)
            self.server.readCanMessages()
        except:
            self.error_message(text ="Make sure that the controller is connected")
            
    def adcMonitoringData(self, ChildWindow):
        ChildWindow.setObjectName("ADCChannels")
        ChildWindow.setWindowTitle("ADC Channels")
        ChildWindow.resize(350, 600)  # w*h
        MainLayout = QGridLayout()
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        SecondGroupBox = QGroupBox("ADC channels")      
        SecondGridLayout = QGridLayout()
        LabelChannel = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.ChannelBox = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.trendingBox = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.trendingBotton = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        adc_channels_reg = self.get_adc_channels_reg()
        dictionary = self.__dictionary_items
        adc_index = self.get_adc_index()
        self.subIndexItems = list(analysis_utils.get_subindex_yaml(dictionary=dictionary, index=adc_index))
        self.Figure = self.compute_initial_figure(index =int(str(1)))
        for i in np.arange(len(self.n_channels)):
            LabelChannel[i] = QLabel("Channel", self)
            LabelChannel[i].setText("Ch" + str(self.n_channels[i]) + ":")
            self.ChannelBox[i] = QLineEdit("", self)
            self.ChannelBox[i].setStyleSheet("background-color: white; border: 1px inset black;")
            self.ChannelBox[i].setReadOnly(True)
            LabelChannel[i].setStatusTip('ADC channel %s [index = %s & subIndex = %s]' % (str(self.n_channels[i]), adc_index, self.subIndexItems[i + 1]))  # show when move mouse to the icon
            self.icon = QLabel(self)
            if adc_channels_reg[str(i + 3)] == "V":       
                icon_dir = 'graphics_Utils/icons/icon_voltage.png'
            else:
                icon_dir = 'graphics_Utils/icons/icon_thermometer.png'
            pixmap = QPixmap(icon_dir)
            self.icon.setPixmap(pixmap.scaled(20, 20))
            self.trendingBotton[i] = QPushButton("")
            self.trendingBotton[i].setObjectName(str(i))
            self.trendingBotton[i].setIcon(QIcon('graphics_Utils/icons/icon_trend.jpg'))
            self.trendingBotton[i].setStatusTip('Data Trending')
            #self.trendingBotton[i].clicked.connect(self.trendWindow)
            
            self.trendingBox[i] = QCheckBox("")
            self.trendingBox[i].setStatusTip('Data Trending') 
            #self.trendingBox[i].stateChanged.connect(self.stateBox)
            if i < 16:
                SecondGridLayout.addWidget(self.icon, i, 0)
                SecondGridLayout.addWidget(self.trendingBox[i], i, 1)
                #SecondGridLayout.addWidget(self.trendingBotton[i], i, 2)
                SecondGridLayout.addWidget(LabelChannel[i], i, 3)
                SecondGridLayout.addWidget(self.ChannelBox[i], i, 4)
            else:
                SecondGridLayout.addWidget(self.icon, i - 16, 5)
                SecondGridLayout.addWidget(self.trendingBox[i], i-16, 6)
                #SecondGridLayout.addWidget(self.trendingBotton[i], i-16, 7)
                SecondGridLayout.addWidget(LabelChannel[i], i - 16, 8)
                SecondGridLayout.addWidget(self.ChannelBox[i], i - 16 , 9)
        SecondGroupBox.setLayout(SecondGridLayout) 
        
        HBox = QHBoxLayout()
        send_button = QPushButton("run")
        send_button.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        send_button.clicked.connect(self.initiate_timer)
        
        trend_button = QPushButton("Trend")
        trend_button.setIcon(QIcon('graphics_Utils/icons/icon_trend.jpg'))
        trend_button.clicked.connect(self.trendWindow)
        
        stop_button = QPushButton("stop")
        stop_button.setIcon(QIcon('graphics_Utils/icons/icon_stop.png'))
        stop_button.clicked.connect(self.stop_timer)
                
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_Utils/icons/icon_close.jpg'))
        close_button.clicked.connect(ChildWindow.close)

        HBox.addWidget(send_button)
        #HBox.addWidget(trend_button)
        HBox.addWidget(stop_button)
        HBox.addWidget(close_button)
        MainLayout.addWidget(SecondGroupBox , 1, 0)
        #MainLayout.addWidget(self.Figure , 1,1)
        MainLayout.addLayout(HBox , 2, 0)
        self._createStatusBar(self)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)

    def stateBox(self, state):
        if state == QtCore.Qt.Checked:
            print('Checked', )
        else:
            print('Unchecked')
    def initiate_timer(self, period=10000):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_adc_channels)
        self.timer.start(period)

    def initiate_trend_timer(self,index =None, period=10000):
        def update_trending_figure(index =None):
            self.update_trending_figure(index =None)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(update_trending_figure)
        self.timer.start(period)
            
    def stop_timer(self):
        try:
            self.timer.stop() 
        except Exception:
            pass
               
    def update_adc_channels(self):
        adc_index = self.get_adc_index()
        adc_channels_reg = self.get_adc_channels_reg()
        adc_updated = []
        self.adc_converted = []
        for i in np.arange(len(self.n_channels)):
            self.set_index(adc_index)
            self.set_subIndex(self.subIndexItems[i + 1])
            self.send_sdo_can()
            data_point = self.get_data_point()
            adc_updated = np.append(adc_updated, data_point)
            self.adc_converted = np.append(self.adc_converted,self.adc_conversion(adc_channels_reg[str(i + 3)], adc_updated[i]))
            if self.adc_converted[i] is not None:
                self.ChannelBox[i].setText(str(round(self.adc_converted[i], 3)))
            else:
                self.ChannelBox[i].setText(str(self.adc_converted[i]))  
        return self.adc_converted
    
    def adc_conversion(self, adc_channels_reg="V", value=None):
        if value is not None:
            if adc_channels_reg == "V":
                value = value * 207 * 10e-6 * 40
            else:
                value = value * 207 * 10e-6
        return value
                           
                
    def deviceChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("DeviceWindow")
        ChildWindow.setWindowTitle("Device Window [ " + self.__appName + "]")
        ChildWindow.adjustSize()
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        self.GridLayout = QGridLayout()
        firstVLayout = QVBoxLayout()
        nodeLabel = QLabel("NodeId", self)
        nodeLabel.setText("NodeId ")
        nodeItems = list(map(str, self.get_nodeIds()))
        nodeComboBox = QComboBox(self)
        for item in nodeItems: nodeComboBox.addItem(item)
        nodeComboBox.activated[str].connect(self.set_nodeId)
        icon = QLabel(self)
        pixmap = QPixmap(self.get_icon_dir())
        icon.setPixmap(pixmap.scaled(100, 100))
        
        device_title = QLabel("    device", self)
        newfont = QFont("Times", 12, QtGui.QFont.Bold)
        device_title.setFont(newfont)
        device_title.setText("        " + self.get_appName())

        adcButton = QPushButton("ADC channels")
        adcButton.setIcon(QIcon('graphics_Utils/icons/icon_reset.png'))
        adcButton.setStatusTip('Show ADC channels')  # show when move mouse to the icon
        adcButton.clicked.connect(self.showAdcChannelWindow)
                
        firstVLayout.addWidget(nodeComboBox)
        firstVLayout.addWidget(icon)
        firstVLayout.addWidget(device_title)
        firstVLayout.addWidget(adcButton)

        VLayout = QVBoxLayout()
        self.indexTextBox = QTextEdit("", self)
        self.indexTextBox.setStyleSheet("background-color: white; border: 2px inset black; min-height: 150px; min-width: 400px;")
        self.indexTextBox.LineWrapMode(1)
        self.indexTextBox.setReadOnly(True)       
        
        startButton = QPushButton("")
        startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        startButton.clicked.connect(self.send_sdo_can)
        
        trendingButton = QPushButton("")
        trendingButton.setIcon(QIcon('graphics_Utils/icons/icon_trend.jpg'))
        trendingButton.setStatusTip('Data Trending')  # show when move mouse to the icon
        trendingButton.clicked.connect(self.trendWindow)
        # trendingButton.clicked.connect(self.clicked)
        HLayout = QHBoxLayout()
        HLayout.addWidget(startButton)
        HLayout.addWidget(trendingButton)
        
        VLayout.addWidget(self.indexTextBox)
        VLayout.addLayout(HLayout)
        
        indexLabel = QLabel("Index", self)
        indexLabel.setText("   Index   ")
        self.IndexListBox = QListWidget(self)
        indexItems = self.__index_items
        for item in indexItems: self.IndexListBox.addItem(item)
        self.IndexListBox.currentItemChanged.connect(self.set_index_value) 
        self.IndexListBox.currentItemChanged.connect(self.get_subIndex_items)
        self.IndexListBox.currentItemChanged.connect(self.get_index_description)  
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        self.subIndexListBox = QListWidget(self)
        self.subIndexListBox.currentItemChanged.connect(self.set_subIndex_value)  
        self.subIndexListBox.currentItemChanged.connect(self.get_subIndex_description)  
        
        self.GridLayout.addWidget(nodeLabel, 0, 0)
        self.GridLayout.addLayout(firstVLayout, 1, 0)
        
        self.GridLayout.addWidget(indexLabel, 0, 1)
        self.GridLayout.addWidget(self.IndexListBox, 1, 1)
        
        self.GridLayout.addWidget(subIndexLabel, 0, 2)
        self.GridLayout.addWidget(self.subIndexListBox, 1, 2)
        self.GridLayout.addLayout(VLayout, 1, 3)
        
        self.WindowGroupBox.setLayout(self.GridLayout)
        logframe.setLayout(self.GridLayout)
        
    '''
    Create toolbar
    '''

    def _createtoolbar(self, mainwindow):
        toolbar = mainwindow.addToolBar("tools")
        self._toolBar(toolbar, mainwindow)
        
    def _toolBar(self, toolbar, mainwindow):        
        canMessage_action = QAction(QIcon('graphics_Utils/icons/icon_msg.jpg'), '&CAN Message', mainwindow)
        canMessage_action.setShortcut('Ctrl+M')
        canMessage_action.setStatusTip('CAN Message')
        canMessage_action.triggered.connect(self.canMessageWindow)

        settings_action = QAction(QIcon('graphics_Utils/icons/icon_settings.jpeg'), '&CAN Settings', mainwindow)
        settings_action.setShortcut('Ctrl+L')
        settings_action.setStatusTip('CAN Settings')
        settings_action.triggered.connect(self.canSettingsWindow)

        canDumpMessage_action = QAction(QIcon('graphics_Utils/icons/icon_dump.png'), '&CAN Dump', mainwindow)
        canDumpMessage_action.setShortcut('Ctrl+D')
        canDumpMessage_action.setStatusTip('Dump CAN messages from the bus')
        canDumpMessage_action.triggered.connect(self.dump_can)

        runDumpMessage_action = QAction(QIcon('graphics_Utils/icons/icon_right.jpg'), '&CAN Run', mainwindow)
        runDumpMessage_action.setShortcut('Ctrl+R')
        runDumpMessage_action.setStatusTip('start reading CAN messages')
        runDumpMessage_action.triggered.connect(self.canDumpMessageWindow)
        
        
        stopDumpMessage_action = QAction(QIcon('graphics_Utils/icons/icon_stop.png'), '&CAN Stop', mainwindow)
        stopDumpMessage_action.setShortcut('Ctrl+C')
        stopDumpMessage_action.setStatusTip('Stop reading CAN messages')
        stopDumpMessage_action.triggered.connect(self.stop_dumptimer)
        

        RandomDumpMessage_action = QAction(QIcon('graphics_Utils/icons/icon_random.png'), '&CAN Random', mainwindow)
        RandomDumpMessage_action.setShortcut('Ctrl+G')
        RandomDumpMessage_action.setStatusTip('Send Random Messages to the bus')
        RandomDumpMessage_action.triggered.connect(self.random_can)
                
        toolbar.addAction(canMessage_action)
        #toolbar.addAction(settings_action)
        toolbar.addSeparator()
        toolbar.addAction(canDumpMessage_action)
        #toolbar.addAction(runDumpMessage_action)
        #toolbar.addAction(stopDumpMessage_action)
        toolbar.addAction(RandomDumpMessage_action)
        
       
        
    def clicked(self, q):
        print("is clicked")                             

    '''
    Define set/get functions
    '''

    def set_textBox_message(self, comunication_object=None, msg="This is a message"):
       
        if comunication_object == "SDO_RX"  :   
            color = QColor("green")
            mode = "W    :"
        if comunication_object == "SDO_TX"  :   
            color = QColor("red") 
            mode = "R    :"
        if comunication_object == "Decoded" :   
            color = QColor("blue")
            mode = "D    :"
        
        self.textBox.setTextColor(color)
        self.textBox.append(mode + msg)
            
    def set_index_value(self):
        index = self.IndexListBox.currentItem().text()
        self.set_index(index)
    
    def set_subIndex_value(self):
        if self.subIndexListBox.currentItem() is not None:
            subindex = self.subIndexListBox.currentItem().text()
            self.set_subIndex(subindex)

    def set_appName(self, x):
        self.__appName = x
    
    def set_adc_channels_reg(self, x):
        self.__adc_channels_reg = x
    
    def set_adc_index(self, x):
        self.set_adc_index = x
    
    def set_version(self, x):
        self.__version = x
        
    def set_icon_dir(self, x):
        self.__icon_dir = x
    
    def set_dictionary_items(self, x):
        self.__dictionary_items = x

    def set_nodeIds(self, x):
        self.__nodeId = x
                        
    def set_interfaceItems(self, x):
        self.__interfaceItems = x  
           
    def set_interface(self, x): 
        self.__interface = x 
                          
    def set_nodeId(self, x):
        self.__nodeId = x
        
    def set_index(self, x):
        self.__index = x
    
    def set_bitrate(self, x):
        self.__bitrate = int(x)       

    def set_ipAddress(self, x):
        self.__ipAddress = x
               
    def set_subIndex(self, x):
        self.__subIndex = x
                
    def set_cobid(self, x):
        self.__cobid = x
    
    def set_dlc(self, x):
        self.__dlc = x
    
    def set_bytes(self, x):
        self.__bytes = x
    
    def set_data_point(self, data):
        self.__response = data
    
    def get_data_point(self):
        return self.__response
        
    def get_index_items(self):
        return self.__index_items
               
    def get_nodeId(self):
        return self.__nodeId
    
    def get_index(self):
        return self.__index
          
    def get_dictionary_items(self):
        return self.__dictionary_items  

    def get_icon_dir(self):
        return self.__icon_dir
    
    def get_appName(self):
        return self.__appName

    def get_adc_channels_reg(self):
        return self.__adc_channels_reg
    
    def get_adc_index(self):
        return self.set_adc_index
        
    def get_nodeIds(self):
        return self.__nodeIds

    def get_subIndex(self):
        return self.__subIndex
    
    def get_cobid(self):
        return  self.__cobid
    
    def get_dlc(self):
        return self.__dlc

    def get_bytes(self):
        return self.__bytes 
        
    def get_bitrate(self):
        return self.__bitrate

    def get_ipAddress(self):
        if self.__interface == 'Kvaser':
            raise AttributeError('You are using a Kvaser CAN interface!')
        return self.__ipAddress    

    def get_interfaceItems(self):
        return self.__interfaceItems
    
    def get_bitrate_items(self):
        return self.__bitrate_items
    
    def get_interface(self):
        """:obj:`str` : Vendor of the CAN interface. Possible values are
        ``'Kvaser'`` and ``'AnaGate'``."""
        return self.__interface

    def get_channel(self):
        return self.__channel    

    def get_channelNumber(self):
        """:obj:`int` : Number of the crurrently used |CAN| channel."""
        return self.__channel

    def get_subIndex_items(self):
        index = self.get_index()
        dictionary = self.__dictionary_items
        subIndexItems = list(analysis_utils.get_subindex_yaml(dictionary=dictionary, index=index))
        self.subIndexListBox.clear()
        for item in subIndexItems: self.subIndexListBox.addItem(item)
    
    def get_index_description(self):
        dictionary = self.__dictionary_items
        if self.IndexListBox.currentItem() is not None:
            index = self.IndexListBox.currentItem().text()
            self.index_description_items = analysis_utils.get_index_description_yaml(dictionary=dictionary , index=index)
            self.indexTextBox.setText(self.index_description_items)
        
    def get_subIndex_description(self):
        dictionary = self.__dictionary_items
        index = self.IndexListBox.currentItem().text()
        if self.subIndexListBox.currentItem() is not None:
            subindex = self.subIndexListBox.currentItem().text()
            self.subindex_description_items = analysis_utils.get_subindex_description_yaml(dictionary=dictionary, index=index, subindex=subindex)
            description_text = self.index_description_items + "<br>" + self.subindex_description_items
            self.indexTextBox.setText(description_text)    
        
    
if __name__ == "__main__":
    pass

