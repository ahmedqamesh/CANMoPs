
from __future__ import annotations
from typing import *
import time
import sys
import os
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
from matplotlib.figure import Figure
from graphics_Utils import dataMonitoring , menuWindow ,logWindow, childWindow
from analysis import logger, analysis_utils ,controlServer
from analysis import CANopenConstants as coc
import binascii
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
rootdir = os.path.dirname(os.path.abspath(__file__)) 
class MainWindow(QMainWindow):
    def __init__(self,parent=None, device_config = ["PSPP_cfg.yml"], interfaces = None):
        super(MainWindow, self).__init__(parent)
        #Start with default settings
        config_dir = "config/"
        self.server = controlServer.ControlServer()
        self.__interfaceItems = self.server.get_interfaceItems() 
        self.__channel = self.server.get_channelNumber()
        self.__interface =interfaces 
        #Load the configuration file
        if device_config is not None: 
            for device in device_config: 
                dev = analysis_utils.open_yaml_file(file =config_dir+device,directory =rootdir[:-14])
            self.__appName          = dev["Application"]["device_name"] 
            self.__version          = dev['Application']['device_version']
            self.__icon_dir          = dev["Application"]["icon_dir"]
            self.__nodeIds          = dev["Application"]["nodeIds"]
            self.__dictionary_items = dev["Application"]["index_items"]
            self.__index_items = list(self.__dictionary_items.keys())
            
        #set default settings
        self.__Bytes =  ["40","0","34","1","0","0","0","0"] 
        self.__subIndex = "0"
        self.__cobid = "608"
        self.__dlc = "8"
        #Show a textBox
        self.textBoxWindow()
        self.configureDeviceBox()
        self.logger = logging.getLogger(__name__)

        self.index_description_items = None
        self.subIndex_description_items = None
    
    def Ui_ApplicationWindow(self):
        self.menu= menuWindow.MenuBar(self)
        self.menu._createMenu(self)
        self.menu._createtoolbar(self)
        self.menu._createStatusBar(self)
        
        # 1. Window settings
        self.setWindowTitle(self.__appName +"_"+ self.__version)
        self.setWindowIcon(QtGui.QIcon('graphics_Utils/icons/icon_mops.png'))
        self.adjustSize()
        # call widgets
        self.createProgressBar()
        self.defaultWindow()

        # Create a frame in the main menu for the gridlayout
        mainFrame = QFrame(self)
        mainFrame.setLineWidth(0.6)
        self.setCentralWidget(mainFrame)
    
        # SetLayout
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.interfaceComboBox,0,0)
        mainLayout.addWidget(self.connectButton,0,1)
        mainLayout.addLayout(self.GridLayout,1,0)
        mainLayout.addWidget(self.textBox,2,0)
        mainLayout.addLayout(self.HLayout,3,0)
        #mainLayout.addWidget(self.progressBar,2,0)
        mainFrame.setLayout(mainLayout)
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
        
        #self.interfaceComboBox.activated[str].connect(self.set_interface)
        
        self.connectButton = QPushButton("")
        self.connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        
        self.connectButton.setIcon(icon)
        self.connectButton.setCheckable(True)
        self.connectButton.clicked.connect(self.applyInterfaceComboBoxChanges)
        self.connectButton.clicked.connect(self.set_connect)
        
        
        self.GridLayout =QGridLayout()
        nodeLabel = QLabel("NodeId", self)
        nodeLabel.setText("NodeId ")
        nodeitems =list(map(str, self.__nodeIds))
        nodeComboBox = QComboBox(self)
        for item in nodeitems: nodeComboBox.addItem(item)
        nodeComboBox.activated[str].connect(self.set_nodeId)
        
        
        indexLabel = QLabel("Index", self)
        indexLabel.setText("   Index   ")
        self.indexTextBox = QLineEdit(self.__index_items[1], self)
        #self.indexTextBox.textChanged.connect(self.set_index)
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        self.subIndextextbox = QLineEdit(self.__subIndex, self)
        #self.subIndextextbox.textChanged.connect(self.set_subIndex)
                
        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.clicked.connect(self.applyLineEditChanges) 
        self.startButton.clicked.connect(self.send_sdo_can)                 
                
        self.GridLayout.addWidget(nodeLabel,0,0)
        self.GridLayout.addWidget(nodeComboBox,1,0)
        
        self.GridLayout.addWidget(indexLabel,0,1)
        self.GridLayout.addWidget(self.indexTextBox,1,1)
        
        self.GridLayout.addWidget(subIndexLabel,0,2)
        self.GridLayout.addWidget(self.subIndextextbox,1,2)       
        self.GridLayout.addWidget(self.startButton,1,3)
    
    def applyInterfaceComboBoxChanges(self):
        self.__interface = (str(self.interfaceComboBox.currentText()))
        
    def applyInterfaceChildComboBoxChanges(self, x):
        self.__interface = x
    
    def applyLineEditChanges(self):
        self.set_index(self.indexTextBox.text())
        self.set_subIndex(self.subIndextextbox.text())

    def set_connect(self):
        interface = self.get_interface()
        self.server.start_channelConnection(interface = interface)
               
    def configureDeviceBox(self):
        self.HLayout =QHBoxLayout()
        deviceLabel = QLabel("Configure Device", self)
        deviceLabel.setText("Configure Device")
        deviceButton = QPushButton("")
        deviceButton.setIcon(QIcon('graphics_Utils/icons/icon_question.png'))
        self.HLayout.addWidget(deviceLabel)
        self.HLayout.addWidget(deviceButton)
        deviceButton.clicked.connect(self.deviceWindow)   

    def deviceWindow(self):
        self.Mainwindow = QMainWindow()
        self.deviceChildWindow(self.Mainwindow)
        self.Mainwindow.show()
        
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
       
    def send_sdo_can(self):
        index = int(self.get_index(),16)
        subIndex = int(self.get_subIndex(),16)
        nodeId = self.__nodeIds[0]
        interface = self.__interface
        print(nodeId, index, subIndex,interface)
        response = self.server.sdoRead(nodeId, index, subIndex,interface,3000)
        self.print_sdo_can(nodeId =nodeId, index = index,subIndex = subIndex, response_from_node = response )

    def send_can(self):
        cobid = int(self.get_cobid())
        bytes =list(map(int, self.get_Bytes()))
        #Send the can Message
        print(str(bytes), cobid)
        self.set_textBox_message(comunication_object = "SDO_RX", msg =str(bytes))
        self.server.writeCanMessage(cobid, bytes, flag=0, timeout=1000)
        # receive the message
        self.read_can()
        
    def read_can(self):
        cobid, data, dlc, flag, t = self.server.readCanMessages()
        self.set_textBox_message(comunication_object = "SDO_TX", msg =str(data))
    
    
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
        decoded_response = f'{response_from_node:03X}\n-------------------------------------------'
        self.set_textBox_message(comunication_object = "Decoded", msg =decoded_response)

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
    
                    
    def set_all(self):
        self.logger.success('========Setting CAN configurations=======')
        ipAddress = self.get_ipAddress()
        bitrate = self.get_bitrate()
        interface = self.get_interface()
        self.server.set_interface(interface)
        self.server.set_bitrate(bitrate)
        self.server.set_ipAddress(ipAddress)
        
            
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
    
    def set_Bytes(self,x):
        self.__Bytes = x
        
    def get_index_items(self):
        return self.__index_items
               
    def get_nodeId(self):
        return self.__nodeId
    
    def get_index(self):
        return self.__index

    def get_subIndex(self):
        return self.__subIndex
          
    def get_dictionary_items(self):
        return self.__dictionary_items  
    
    def get_interface(self): 
        return self.__interface

    def get_icon_dir(self):
        return self.__icon_dir
    
    def get_appName(self):
        return self.__appName
    def get_DllVersion(self):
        ret = analib.wrapper.dllInfo()
        return ret
    
    def get_nodeIds(self):
        return self.__nodeIds

    def get_cobid(self):
        return  self.__cobid
    
    def get_dlc(self):
        return self.__dlc

    def get_Bytes(self):
        return self.__Bytes 
        
    def get_bitrate(self):
        return self.__bitrate

    def get_ipAddress(self):
        """:obj:`str` : Network address of the AnaGate partner. Only used for
        AnaGate CAN interfaces."""
        if self.__interface == 'Kvaser':
            raise AttributeError('You are using a Kvaser CAN interface!')
        return self.__ipAddress    

    def get_interfaceItems(self):
        return self.__interfaceItems
    
    def get_interface(self):
        """:obj:`str` : Vendor of the CAN interface. Possible values are
        ``'Kvaser'`` and ``'AnaGate'``."""
        return self.__interface

    def get_channel(self):
        return self.__channel    

    def get_channelNumber(self):
        """:obj:`int` : Number of the crurrently used |CAN| channel."""
        return self.__channel
        
    def deviceChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.adjustSize()
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        self.GridLayout = QGridLayout()
        firstVLayout = QVBoxLayout()
        nodeLabel = QLabel("NodeId", self)
        nodeLabel.setText("NodeId ")
        nodeItems = list(map(str, self.__nodeIds))
        nodeComboBox = QComboBox(self)
        for item in nodeItems: nodeComboBox.addItem(item)
        nodeComboBox.activated[str].connect(self.set_nodeId)
        icon = QLabel(self)
        pixmap = QPixmap(self.__icon_dir)
        icon.setPixmap(pixmap.scaled(100, 100))
        
        device_title = QLabel("    device", self)
        newfont = QFont("Times", 12, QtGui.QFont.Bold)
        device_title.setFont(newfont)
        device_title.setText("         " + self.get_appName())
        
        firstVLayout.addWidget(nodeComboBox)
        firstVLayout.addWidget(icon)
        firstVLayout.addWidget(device_title)

        VLayout = QVBoxLayout()
        self.indexTextBox = QTextEdit("", self)
        # indexTextBox = QPlainTextEdit("Info", self)
        self.indexTextBox.setStyleSheet("background-color: white; border: 2px inset black; min-height: 150px; min-width: 400px;")
        self.indexTextBox.LineWrapMode(1)
        self.indexTextBox.setReadOnly(True)       
        
        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.clicked.connect(self.send_sdo_can)
        
        VLayout.addWidget(self.indexTextBox)
        VLayout.addWidget(self.startButton)
                
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
        

    def set_index_value(self):
        index = self.IndexListBox.currentItem().text()
        self.set_index(index)
    
    def set_subIndex_value(self):
        if self.subIndexListBox.currentItem() is not None:
            subindex = self.subIndexListBox.currentItem().text()
            self.set_subIndex(subindex)

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
    @property
    def interfaces(self):
        return self.__interface
    
    @interfaces.setter
    def set_interface(self, x): 
        self.__interface = x 
if __name__ == "__main__":
    pass


