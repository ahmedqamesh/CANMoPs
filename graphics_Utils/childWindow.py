from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from graphics_Utils import dataMonitoring , logWindow 
from analysis import logger
import numpy as np
import os
import binascii
import logging
rootdir = os.path.dirname(os.path.abspath(__file__)) 


class ChildWindow(QWidget):  

    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent)
       self.__y = 0
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
        
    def trendChildWindow(self, ChildWindow, data, trending):
        self.set_data_point(data)
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(500, 500)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        Fig = dataMonitoring.LiveMonitoringData(data = data , period = 50, trending=trending)
        plotLayout = QVBoxLayout()
        plotLayout.addStretch(1)
        plotLayout.addWidget(Fig)
        self.WindowGroupBox.setLayout(plotLayout)
        logframe.setLayout(plotLayout) 

    def _createStatusBar(self, childwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        childwindow.setStatusBar(status)
 
        
    def clicked(self, q):
        print("is clicked")
        
    # setter method
    def set_clicked(self, x):
        print(x)

    def set_data_point(self, data):
        self.__y = data
    
    def get_data_point(self):
        return self.__y
            
if __name__ == "__main__":
    pass

