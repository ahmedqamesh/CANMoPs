
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
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread, Event, Lock
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
from graphics_Utils import dataMonitoring , menuWindow , childWindow ,logWindow
from analysis import logger, analysis_utils 
from analysis import CANopenConstants as coc
# Third party modules
import coloredlogs as cl
import verboselogs
import analib
app_name = 'CAN MoPS v1.0'
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
    def Ui_ApplicationWindow(self):
        self.menu= menuWindow.MenuBar()
        self.menu._createMenu(self)
        self.menu._createtoolbar(self)
        self.menu._createStatusBar(self)
        
        # 1. Window settings
        self.setWindowTitle(app_name)
        #self.setGeometry(300, 300, 800, 400)
        #self.resize(800, 600)
        
        # call widgets
        self.createProgressBar()

        # Creat a frame in the main menu for the gridlayout
        mainFrame = QFrame(self)
        mainFrame.setLineWidth(0.6)
        self.setCentralWidget(mainFrame)
        
        # SetLayout
        mainLayout = QGridLayout()
        #mainLayout.addWidget(self.topLeftTabGroupBox, 1, 0)
        mainLayout.addWidget(self.progressBar,0,0)
        
        mainFrame.setLayout(mainLayout)
        # 3. Show
        self.show()
        return

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
     
    def openWindow(self):
        self.window = QMainWindow()
        self.ui = ChildWindow.Ui_ChildWindow()
        self.ui.settingChannel(self.window)
        self.window.show()

    #Setter and getter functions
    def set_interface(self, x):
        self.__interface = x
        self.get_interface()
        
    def get_interface(self):
        print("_interface is set to ", self.__interface)
        return self.__interface
    
if __name__ == "__main__":
    pass


