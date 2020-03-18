from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from graphics_Utils import dataMonitoring , logWindow 

import numpy as np
import os
import binascii
import yaml
import logging
rootdir = os.path.dirname(os.path.abspath(__file__)) 


class ChildWindow(QWidget):  

    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent)
    def outputChildWindow(self, ChildWindow, comunication_object="Normal"):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(600, 600)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        logTextBox = logWindow.QTextEditLogger(ChildWindow, comunication_object=comunication_object)
        logLayout = QVBoxLayout()
        logLayout.addWidget(logTextBox.text_edit_widget)
        self.WindowGroupBox.setLayout(logLayout)
        logframe.setLayout(logLayout) 
        
    def trendChildWindow(self, ChildWindow, trending):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(500, 500)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        trendLayout = QGridLayout()
        self.WindowGroupBox = QGroupBox("")
        Fig = dataMonitoring.LiveMonitoringData(period = 50, trending=trending)
        #plotLayout = QVBoxLayout()
        #plotLayout.addStretch(1)
        #plotLayout.addWidget(Fig)
        HBox = QHBoxLayout()
        timeTextBox = QLineEdit("50", self)
               
        start_button = QPushButton("")
        start_button.setIcon(QIcon('graphics_Utils/icons/icon_start.png' ))
        start_button.clicked.connect(self.clicked)
        
        pause_button = QPushButton("")
        pause_button.setIcon(QIcon('graphics_Utils/icons/icon_pause.png' ))
        pause_button.clicked.connect(self.clicked)
        
        stop_button = QPushButton("")
        stop_button.setIcon(QIcon('graphics_Utils/icons/icon_stop.png' ))
        stop_button.clicked.connect(self.clicked)        
        
        HBox.addWidget(timeTextBox) 
        HBox.addWidget(start_button)
        HBox.addWidget(pause_button)
        HBox.addWidget(stop_button)
        
        indexLabel = QLabel("Period[s]", self)
        indexLabel.setText("Period [s]")
                
        HLabelBox = QHBoxLayout()
        HLabelBox.addWidget(indexLabel)
         
        trendLayout.addWidget(Fig, 0, 0)
        trendLayout.addLayout(HLabelBox, 1,0)
        trendLayout.addLayout(HBox, 2,0)
        
        self.WindowGroupBox.setLayout(trendLayout)
        logframe.setLayout(trendLayout) 
  
    def clicked(self, q):
        print("is clicked")
        
    # setter method
    def set_clicked(self, x):
        print(x)
    
    def open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')
        with open(filename[0], 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg
                 
if __name__ == "__main__":
    pass

