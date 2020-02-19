
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
    def __init__(self,parent=None, device_config = ["MoPS_daq_cfg.yml"]):
        super(MainWindow, self).__init__(parent)
        #Start with default settings
        config_dir = "config/"
        self.server = controlServer.ControlServer(interface = "AnaGate")
        self.__interfaceItems = self.server.get_interfaceItems()
        self.__ipAddress = self.server.get_ipAddress()     
        self.__interface= self.server.get_interface() 
        self.__bitrate =self.server.get_bitrate()  
        self.__channel = self.server.get_channelNumber()   
        #Load the configuration file
        conf = analysis_utils.open_yaml_file(file =config_dir+"main_cfg.yml",directory =rootdir[:-14])
        if device_config is not None: 
            for device in device_config: 
                dev = analysis_utils.open_yaml_file(file =config_dir+device,directory =rootdir[:-14])
            self.__appName          = dev["Application"]["device_name"] 
            self.__version          = dev['Application']['device_version']
            self.__icon_dir          = dev["Application"]["icon_dir"]
            self.__nodeIds          = dev["Application"]["nodeIds"]
            self.__index_items      = dev["Application"]["index_items"]
            self.__subindex_items   = dev["Application"]["subindex_items"]
            self.__description_items      = dev["Application"]["description_items"]
        #Show a textBox
        self.textBoxWindow()

    def textBoxWindow(self):
        self.textBox = QTextEdit()
        self.textBox.setTabStopWidth(12) 
        self.textBox.setReadOnly(True)
    
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
        
        #mainLayout.addWidget(self.progressBar,2,0)
        mainFrame.setLayout(mainLayout)
        # 3. Show
        self.show()
        return

    def defaultWindow(self):
        __interfaceItems = self.__interfaceItems
        self.interfaceComboBox = QComboBox(self)
        for item in __interfaceItems: self.interfaceComboBox.addItem(item)
        self.interfaceComboBox.activated[str].connect(self.set_interface)
        self.connectButton = QPushButton("")
        self.connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        
        self.connectButton.setIcon(icon)
        self.connectButton.setCheckable(True)
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
        indexTextBox = QLineEdit(self.__index_items[0], self)
        indexTextBox.textChanged.connect(self.set_index)
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        subIndextextbox = QLineEdit("1", self)
        subIndextextbox.textChanged.connect(self.set_subIndex)
                
        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.clicked.connect(self.send_sdo_can)                 
                
        self.GridLayout.addWidget(nodeLabel,0,0)
        self.GridLayout.addWidget(nodeComboBox,1,0)
        
        self.GridLayout.addWidget(indexLabel,0,1)
        self.GridLayout.addWidget(indexTextBox,1,1)
        
        self.GridLayout.addWidget(subIndexLabel,0,2)
        self.GridLayout.addWidget(subIndextextbox,1,2)       
        self.GridLayout.addWidget(self.startButton,1,3)
    
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
           
    def set_nodeId(self,x):
        self.__nodeId =x
        
    def set_index(self,x):
        self.__index = x

    def set_subIndex(self,x):
        self.__subIndex = x
                
    def set_interface(self, x): 
        self.__interface = x 

    def set_connect(self):
        interface = self.get_interface()
        self.server.start_channelConnection(interface = interface, ipAddress = self.__ipAddress, channel = self.__channel, baudrate = self.__bitrate)
    
    def get_index_items(self):
        return self.__index_items

    def get_subindex_items(self):
        return self.__subindex_items
        
    def get_interface(self): 
        return self.__interface
        
    def get_index(self):
        return self.__index

    def get_nodeId(self):
        return self.__nodeId
    
    def get_subIndex(self):
        return self.__subIndex
    
    def get_description_items(self):
        return self.__description_items   
      
    def get_icon_dir(self):
        return self__icon_dir
    def send_sdo_can(self):
        index = int(self.get_index(),16)
        subIndex = int(self.get_subIndex())
        nodeId = self.__nodeIds[0]
        
        response = self.server.sdoRead(nodeId, index, subIndex,3000)
        self.print_sdo_can(nodeId =nodeId, index = index,    subIndex = subIndex,
                           response_from_node = response )

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
        decoded_response = f'{response_from_node:03X}'
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
    
    
if __name__ == "__main__":
    pass


