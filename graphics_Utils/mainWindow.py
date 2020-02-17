
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
from graphics_Utils import dataMonitoring , menuWindow ,logWindow
from analysis import logger, analysis_utils ,controlServer
from analysis import CANopenConstants as coc
import binascii
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
rootdir = os.path.dirname(os.path.abspath(__file__)) 
class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        #Load the configuration file
        conf = analysis_utils.open_yaml_file(file ="MoPS_daq_cfg.yml",directory =rootdir[:-14])
        #get info about the application
        self.__appName = conf['Application']['app_name']
        self.__version = conf['Application']['version']
        self.__interface= conf['CAN_Interface']['AnaGate']['name']
        self.__interfaceItems = conf['Application']["interface_items"][1:]
        self.__channel = conf['CAN_Interface']['AnaGate']['channel']
        self.__ipAddress = conf['CAN_Interface']['AnaGate']['ipAddress']
        self.__bitrate =conf['CAN_Interface']['AnaGate']['bitrate']
        self.__nodeIds = conf["CAN_settings"]["nodeIds"]
        self.server = controlServer.ControlServer()
        
    def Ui_ApplicationWindow(self):
        self.menu= menuWindow.MenuBar()
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
        # Creat a frame in the main menu for the gridlayout
        mainFrame = QFrame(self)
        mainFrame.setLineWidth(0.6)
        self.setCentralWidget(mainFrame)
        # SetLayout
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.interfaceComboBox,0,0)
        mainLayout.addWidget(self.connectButton,0,1)
        mainLayout.addLayout(self.GridLayout,1,0)
        mainLayout.addWidget(self.startButton,1,1)
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
        indexLabel.setText("        Index")
        indextextbox = QLineEdit("0x2201", self)
        indextextbox.textChanged.connect(self.set_index)
        
        subIndexLabel = QLabel("    SubIndex", self)
        subIndexLabel.setText("SubIndex")
        subIndextextbox = QLineEdit("1", self)
        subIndextextbox.textChanged.connect(self.set_subIndex)
                        
        self.GridLayout.addWidget(nodeLabel,0,0)
        self.GridLayout.addWidget(nodeComboBox,1,0)
        
        self.GridLayout.addWidget(indexLabel,0,1)
        self.GridLayout.addWidget(indextextbox,1,1)
        
        self.GridLayout.addWidget(subIndexLabel,0,2)
        self.GridLayout.addWidget(subIndextextbox,1,2)       

        self.startButton = QPushButton("")
        self.startButton.setIcon(QIcon('graphics_Utils/icons/icon_start.png'))
        self.startButton.clicked.connect(self.send_sdo_can) 
        
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
        
    def get_interface(self): 
        return self.__interface
        
    def get_index(self):
        return self.__index

    def get_nodeId(self):
        return self.__nodeId
    
    def get_subIndex(self):
        return self.__subIndex
        
    def send_sdo_can(self):
        index = int(self.get_index(),16)
        subIndex = int(self.get_subIndex())
        nodeId = self.__nodeIds[0]
        msg = self.server.sdoRead(nodeId, index, subIndex,3000)
        self.print_can_message(msg)
        
    def print_can_message(self,msg):
        print(f'VendorId: {msg:03X}')
      
if __name__ == "__main__":
    pass


