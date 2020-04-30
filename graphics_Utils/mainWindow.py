
from __future__ import annotations
from typing import *
import sched, time
import sys
import os
from os import chdir
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
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
from graphics_Utils import dataMonitoring , menuWindow ,logWindow, childWindow
from analysis import analysis_utils ,controlServer
from analysis import CANopenConstants as coc
import binascii
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
rootdir = os.path.dirname(os.path.abspath(__file__)) 
class MainWindow(QMainWindow):
    def __init__(self,parent=None, 
                 device_config = ["PSPP_cfg.yml"],
                 main_config = ["main_cfg.yml"]):
        super(MainWindow, self).__init__(parent)
        self.__device_config = device_config            
        self.logger = logging.getLogger(__name__)
        self.child = childWindow.ChildWindow() 
        #Start with default settings
        config_dir = "config/"
        
        # Read configurations from a file    
        conf = analysis_utils.open_yaml_file(file =config_dir + "main_cfg.yml",directory =rootdir[:-14])
        self.__appName          =   conf["Application"]["app_name"] 
        self.__appVersion       =   conf['Application']['app_version']
        self.__appIconDir       =   conf["Application"]["app_icon_dir"]        
        self._index_items       =   conf["default_values"]["index_items"]
        self.__interfaceItems   =   conf['default_values']["interface_items"]        
        self.__bitrate_items    =   conf['default_values']['bitrate_items']
        self.__bytes            =   conf["default_values"]["bytes"]
        self.__subIndex         =   conf["default_values"]["subIndex"]
        self.__cobid            =   conf["default_values"]["cobid"]
        self.__dlc              =   conf["default_values"]["dlc"]

        self.__interface        =   conf['CAN_Interface']['AnaGate']['name']
        self.__channel          =   conf['CAN_Interface']['AnaGate']['channel']
        self.__ipAddress        =   conf['CAN_Interface']['AnaGate']['ipAddress']
        self.__bitrate          =   conf['CAN_Interface']['AnaGate']['bitrate']
        self.__nodeIds          =   conf["CAN_settings"]["nodeIds"]
        self.__devices          =   conf["Devices"]

        self.configureDeviceBox(None)
        self.index_description_items = None
        self.subIndex_description_items = None
        self.__response =None
        #Show a textBox
        self.textBoxWindow()
        
        self.MainWindow = QMainWindow()
        
    def devices_configuration(self,dev):
        self.__appName          = dev["Application"]["device_name"] 
        self.__version          = dev['Application']['device_version']
        self.__icon_dir         = dev["Application"]["icon_dir"]
        self.__nodeIds          = dev["Application"]["nodeIds"]
        self.__dictionary_items = dev["Application"]["index_items"]
        self.__index_items = list(self.__dictionary_items.keys())
        return  self.__appName, self.__version, self.__icon_dir, self.__nodeIds, self.__dictionary_items      
    
    def Ui_ApplicationWindow(self):
        #self.trendWindow()
        self.menu= menuWindow.MenuBar(self)
        self.menu._createMenu(self)
        self._createtoolbar(self)
        self.menu._createStatusBar(self)
        self.server = controlServer.ControlServer()
        # 1. Window settings
        self.setWindowTitle(self.__appName +"_"+ self.__appVersion)
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
        self.mainLayout.addWidget(self.interfaceComboBox,0,0)
        self.mainLayout.addWidget(self.connectButton,0,1)
        self.mainLayout.addLayout(self.GridLayout,1,0)
        self.mainLayout.addWidget(self.textBox,2,0)
        self.mainLayout.addWidget(line,3,0)
        self.mainLayout.addLayout(self.HLayout,4,0)
        #mainLayout.addWidget(self.progressBar,2,0)
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
        for item in __interfaceItems[1:]: self.interfaceComboBox.addItem(item)
        self.interfaceComboBox.activated[str].connect(self.set_interface)
        self.interfaceComboBox.setStatusTip('Select the connected interface')
        self.connectButton = QPushButton("")
        self.connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        self.connectButton.setIcon(icon)
        self.connectButton.setStatusTip('Connect the interface')
        self.connectButton.setCheckable(True)
        self.connectButton.clicked.connect(self.set_connect)

        self.GridLayout =QGridLayout()
        nodeLabel = QLabel("NodeId", self)
        nodeLabel.setText("NodeId ")
        nodeitems =list(map(str, self.__nodeIds))
        nodeComboBox = QComboBox(self)
        for item in nodeitems: nodeComboBox.addItem(item)
        nodeComboBox.activated[str].connect(self.set_nodeId)
        nodeComboBox.setStatusTip('NodeIds as defined in the main_cfg.yml file')
        indexLabel = QLabel("Index", self)
        indexLabel.setText("   Index   ")
        self.mainIndexTextBox = QLineEdit("0x1000", self)
        #self.indexTextBox.textChanged.connect(self.set_index)
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        self.mainSubIndextextbox = QLineEdit(self.__subIndex, self)
        #self.subIndextextbox.textChanged.connect(self.set_subIndex)
                
        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.setStatusTip('Send CAN message')
        self.startButton.clicked.connect(self.applyLineEditChanges) 
        self.startButton.clicked.connect(self.send_sdo_can)                 
                   
        self.GridLayout.addWidget(nodeLabel,0,0)
        self.GridLayout.addWidget(nodeComboBox,1,0)   
        self.GridLayout.addWidget(indexLabel,0,1)
        self.GridLayout.addWidget(self.mainIndexTextBox,1,1)
        self.GridLayout.addWidget(subIndexLabel,0,2)
        self.GridLayout.addWidget(self.mainSubIndextextbox,1,2)       
        self.GridLayout.addWidget(self.startButton,1,3)

    def applyLineEditChanges(self):
        self.set_index(self.mainIndexTextBox.text())
        self.set_subIndex(self.mainSubIndextextbox.text())

    def configureDeviceBox(self,conf):
        self.HLayout =QHBoxLayout()
        deviceLabel = QLabel("Configure Device", self)
        deviceLabel.setText("Configure Device")
        self.deviceButton= QPushButton("")
        self.deviceButton.setStatusTip('Choose the configuration yaml file')
        self.deviceButton.setIcon(QIcon('graphics_Utils/icons/icon_question.png'))
        self.deviceButton.clicked.connect(self.update_device_menu)
        self.HLayout.addWidget(deviceLabel)
        self.HLayout.addWidget(self.deviceButton)

    def update_device_menu(self):
        conf = self.child.open()
        #self.deviceButton = None
        self.__devices.append(conf["Application"]["device_name"])
        self.deviceButton.deleteLater()
        self.HLayout.removeWidget(self.deviceButton)
        self.deviceButton= QPushButton("")
        appName, version, icon_dir, nodeIds, dictionary_items = self.devices_configuration(conf)
        self.set_appName(appName)
        self.set_version(version)
        self.set_icon_dir(icon_dir)
        self.set_nodeIds(nodeIds)
        self.set_dictionary_items(dictionary_items)                
        self.deviceButton.setIcon(QIcon(self.get_icon_dir()))
        self.deviceButton.clicked.connect(self.deviceWindow)
        self.HLayout.addWidget(self.deviceButton)
        #self.mainLayout.addLayout(self.HLayout,3,0)
      
    # Functions to run
    def showAdcChannelWindow(self):
        self.MessageWindow = QMainWindow()
        self.adcChannelChildWindow(self.MessageWindow)
        self.MessageWindow.show()
        
    def canMessageWindow(self):
        self.MessageWindow = QMainWindow()
        self.canMessageChildWindow(self.MessageWindow)
        self.MessageWindow.show()

    def canSettingsWindow(self):
        MainWindow = QMainWindow()
        self.canSettingsChildWindow(MainWindow)
        MainWindow.show()

    def trendWindow(self):
        self.trend = QMainWindow()
        self.ui = childWindow.ChildWindow()
        self.ui.trendChildWindow(self.trend)
        self.trend.show()
            
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
            self.server.set_interface(interface)
            self.server.set_canController(interface = interface)
        else:
           self.server.stop()

    def set_all(self):   
        bitrate = self.get_bitrate()
        interface = self.get_interface()
        if interface !="Kvaser":
            ipAddress = self.get_ipAddress()
            self.server.set_ipAddress(ipAddress)
        self.server.set_bitrate(bitrate)
        self.server.set_interface(interface)
        self.server.set_canController(interface = interface)
        
    '''
    Define can communication messages
    '''
               
    def send_sdo_can(self, trending =False):
        index = int(self.get_index(),16)
        subIndex = int(self.get_subIndex(),16)
        nodeId = self.__nodeIds[0]
        try:   
            self.__response = self.server.sdoRead(nodeId, index, subIndex,3000)
            self.set_data_point(self.__response)
            self.print_sdo_can(nodeId =nodeId, index = index,subIndex = subIndex, response_from_node = self.__response )
        except Exception:
            self.error_message(text = "Make sure that the CAN interface is connected")
    
    def send_sdo_data(self):
        data = randint(0,100)
        self.set_data_point(data)
        
    def error_message(self, text=False):
        QMessageBox.about(self,"Error Message",text)
     
    def print_sdo_can(self, nodeId =None , index = None, subIndex =None, response_from_node ="response_from_node"):
        # printing the read message with cobid = SDO_RX + nodeId
        MAX_DATABYTES =8
        msg = [0 for i in range(MAX_DATABYTES)]
        msg[1], msg[2] = index.to_bytes(2, 'little')
        msg[3] = subIndex
        msg[0] = 0x40
        self.set_textBox_message(comunication_object = "SDO_RX", msg =str(msg))
        #printing response 
        self.set_textBox_message(comunication_object = "SDO_TX", msg =str(response_from_node))
        #print decoded response
        decoded_response = f'{response_from_node:03X}\n-----------------------------------'
        self.set_textBox_message(comunication_object = "Decoded", msg =decoded_response)
            
    def send_can(self):
        try:
            cobid = int(self.get_cobid(),16)
            bytes =list(map(int, self.get_bytes()))
            #Send the can Message
            self.set_textBox_message(comunication_object = "SDO_RX", msg =str(bytes))
            self.server.writeCanMessage(cobid, bytes, flag=0, timeout=1000)
            # receive the message
            self.read_can()
        except Exception:
            self.error_message(text = "Make sure that the CAN interface is connected")

    def read_can(self):
        cobid, data, dlc, flag, t = self.server.readCanMessages()
        self.set_textBox_message(comunication_object = "SDO_TX", msg =str(data))
    
    '''
    Define set/get functions
    '''
    def set_textBox_message(self, comunication_object = None, msg ="This is a message"):
       
        if comunication_object == "SDO_RX"  :   
            color = QColor("green")
            mode    =   "W    :"
        if comunication_object == "SDO_TX"  :   
            color = QColor("red") 
            mode    =   "R    :"
        if comunication_object == "Decoded" :   
            color = QColor("blue")
            mode    =   "D    :"
        
        self.textBox.setTextColor(color)
        self.textBox.append(mode+msg)
            
    def set_index_value(self):
        index = self.IndexListBox.currentItem().text()
        self.set_index(index)
    
    def set_subIndex_value(self):
        if self.subIndexListBox.currentItem() is not None:
            subindex = self.subIndexListBox.currentItem().text()
            self.set_subIndex(subindex)

    def set_appName(self,x):
        self.__appName = x
        
    def set_version(self,x):
        self.__version = x
        
    def set_icon_dir(self,x):
        self.__icon_dir = x
    
    def set_dictionary_items(self,x):
        self.__dictionary_items = x

    def set_nodeIds(self,x):
        self.__nodeId =x
                        
    def set_interfaceItems(self, x):
        self.__interfaceItems =x  
           
    def set_interface(self, x): 
        self.__interface = x 
                               
    def set_nodeId(self,x):
        self.__nodeId =x
        
    def set_index(self,x):
        self.__index = x
    
    def set_bitrate(self,x):
        self.__bitrate = int(x)       

    def set_ipAddress(self,x):
        self.__ipAddress = x
               
    def set_subIndex(self,x):
        self.__subIndex = x
                
    def set_cobid(self, x):
        self.__cobid = x
    
    def set_dlc(self,x):
        self.__dlc = x
    
    def set_bytes(self,x):
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

    def get_DllVersion(self):
        ret = analib.wrapper.dllInfo()
        return ret
    
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

    def get_adc_channels(self):
        print("dsfdsfdsfds")
        n_channels = np.arange(3,34)
        channels_values = np.random.randint(1,101,len(n_channels))
        print(channels_values)
        for i in np.arange(len(n_channel)):
            self.ChannelBox[i].setText(str(channels_values[i]))        
        return channels_values
        
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
        #modeComboBox.activated[str].connect(self.clicked)

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
            #firstComboBox.activated[str].connect(self.clicked)
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


    def adcChannelChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("ADCChannels")
        ChildWindow.setWindowTitle("ADC Channels")
        ChildWindow.resize(310, 600)  # w*h
        MainLayout = QGridLayout()
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        SecondGroupBox = QGroupBox("ADC channels")
        #self.get_adc_channels
            
        SecondGridLayout = QGridLayout()
        n_channel = np.arange(3,35)
        LabelChannel = [n_channel[i] for i in np.arange(len(n_channel))]
        self.ChannelBox = [n_channel[i] for i in np.arange(len(n_channel))]
        
        for i in np.arange(len(n_channel)):
            LabelChannel[i] = QLabel("Channel", ChildWindow)
            LabelChannel[i].setText("Ch"+str(n_channel[i])+":")
            self.ChannelBox[i] = QLineEdit("", ChildWindow)
            if i < 16:
                SecondGridLayout.addWidget(LabelChannel[i], i, 0)
                SecondGridLayout.addWidget(self.ChannelBox[i], i, 1)
            else:
                SecondGridLayout.addWidget(LabelChannel[i], i-16, 4)
                SecondGridLayout.addWidget(self.ChannelBox[i], i -16 , 5)
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
        MainLayout.addWidget(SecondGroupBox , 0, 0)
        MainLayout.addLayout(HBox , 1, 0)

        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)

                

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
        cobidtextbox = QLineEdit(self.__cobid, ChildWindow)
        cobidtextboxValue = cobidtextbox.text()
        self.set_cobid(cobidtextboxValue)
          
        #self.main.set_bytes(textboxValue[i])
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
        FirstGridLayout.addWidget(cobidtextbox, 0, 1)
                
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
        textbox = [ByteList[i] for i in np.arange(len(ByteList))]
        textboxValue = [ByteList[i] for i in np.arange(len(ByteList))]
        for i in np.arange(len(ByteList)):
            LabelByte[i] = QLabel(ByteList[i], ChildWindow)
            LabelByte[i].setText(ByteList[i])
            textbox[i] = QLineEdit(self.__bytes[i], ChildWindow)
            textboxValue[i] = textbox[i].text()
            if i <= 3:
                SecondGridLayout.addWidget(LabelByte[i], i, 0)
                SecondGridLayout.addWidget(textbox[i], i, 1)
            else:
                SecondGridLayout.addWidget(LabelByte[i], i - 4, 4)
                SecondGridLayout.addWidget(textbox[i], i - 4, 5)
        self.set_bytes(textboxValue)
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
                      
    def deviceChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("DeviceWindow")
        ChildWindow.setWindowTitle("Device Window [ "+self.__appName +"]")
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
        adcButton.setStatusTip('Show ADC channels') # show when move mouse to the icon
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
        trendingButton.setStatusTip('Data Trending') # show when move mouse to the icon
        trendingButton.clicked.connect(self.trendWindow)
        #trendingButton.clicked.connect(self.clicked)
        HLayout =QHBoxLayout()
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
    def _createtoolbar(self,mainwindow):
        toolbar = mainwindow.addToolBar("tools")
        self._toolBar(toolbar,mainwindow)
        
    def _toolBar(self,toolbar, mainwindow):
        
        canMessage_action = QAction(QIcon('graphics_Utils/icons/icon_msg.jpg'), '&CAN Message', mainwindow)
        canMessage_action.setShortcut('Ctrl+N')
        canMessage_action.setStatusTip('CAN Message')
        canMessage_action.triggered.connect(self.canMessageWindow)

        settings_action = QAction(QIcon('graphics_Utils/icons/icon_settings.jpeg'), '&CAN Settings', mainwindow)
        settings_action.setShortcut('Ctrl+L')
        settings_action.setStatusTip('CAN Settings')
        settings_action.triggered.connect(self.canSettingsWindow)
        
        start_action = QAction(QIcon('graphics_Utils/icons/icon_start.png'), '&Start', mainwindow)
        start_action.setStatusTip('Start session') # show when move mouse to the icon
        start_action.triggered.connect(self.clicked)

        pause_action = QAction(QIcon('graphics_Utils/icons/icon_pause.png'), '&Pause', mainwindow)
        pause_action.setStatusTip('Pause program') # show when move mouse to the icon
        pause_action.triggered.connect(self.clicked)
                
        stop_action = QAction(QIcon('graphics_Utils/icons/icon_stop.png'), '&Stop', mainwindow)
        stop_action.setStatusTip('Stop program') # show when move mouse to the icon
        stop_action.triggered.connect(self.clicked)

           
        toolbar.addAction(canMessage_action)
        toolbar.addAction(settings_action)
        toolbar.addSeparator()
        #toolbar.addAction(start_action)
        #toolbar.addAction(pause_action)
        #toolbar.addAction(stop_action)
        
    def clicked(self,q):
        print("is clicked")                             
if __name__ == "__main__":
    pass


