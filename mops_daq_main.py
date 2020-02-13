
import os
import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from graphics_Utils import dataMonitoring , menuWindow , childWindow ,logWindow , mainWindow
from analysis import analysis_utils , controlServer

rootdir = os.path.dirname(os.path.abspath(__file__))   
if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = mainWindow.MainWindow()
    app.Ui_ApplicationWindow()
    qapp.exec_()