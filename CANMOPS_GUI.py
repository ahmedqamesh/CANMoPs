# -*- coding: utf-8 -*-
import sys
import os
import analib
import time
import logging
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from analysis import controlServer, analysis_utils
from graphics_Utils import  mainWindow
rootdir = os.path.dirname(os.path.abspath(__file__))
if __name__=='__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    app = mainWindow.MainWindow()
    app.Ui_ApplicationWindow()
    qapp.exec_()