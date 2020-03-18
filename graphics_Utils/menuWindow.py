import sys
import logging
loglevel = logging.getLogger('Analysis').getEffectiveLevel()
#from analysis import logger
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from graphics_Utils import mainWindow
import yaml
cs = False
wwo = False
class MenuBar(mainWindow.MainWindow):  
    
    def __init__(self,parent=mainWindow):
        super(MenuBar,self).__init__(parent)
        self.MainWindow = QMainWindow()
        self.main = mainWindow.MainWindow()
        self.textBox = self.main.textBox
        
    def _createMenu(self,mainwindow):
        menuBar = mainwindow.menuBar()
        menuBar.setNativeMenuBar(False) #only for MacOS
        self._fileMenu(menuBar,mainwindow)
        self._helpMenu(menuBar, mainwindow)

    # 1. File menu
    def _fileMenu(self,menuBar,mainwindow):
               
        fileMenu = menuBar.addMenu('&File')
        exit_action = QAction(QIcon('graphics_Utils/icons/icon_exit.png'), '&Exit', mainwindow)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit program')
        exit_action.triggered.connect(qApp.quit)

        #fileMenu.addSeparator()
        fileMenu.addAction(exit_action)
           
    # 4. Help menu
    def _helpMenu(self,menuBar,mainwindow):
        helpmenu = menuBar.addMenu("&Help")

        about_action = QAction('&About', mainwindow)
        about_action.setStatusTip("About")
        about_action.triggered.connect(self.about)
        helpmenu.addAction(about_action)
    
    # 4. Help menu
             
    def _createStatusBar(self,mainwindow, msg ="Ready"):
        status = QStatusBar()
        status.showMessage(msg)
        mainwindow.setStatusBar(status)

        
    def about(self):
        QMessageBox.about(self,"About",
        """CANMoPS is a graphical user interface GUI to read the channels of MOPS chip. The package can communicate with a CAN interface and talks CANopen with the connected Controllers. Currently only CAN interfaces from AnaGate (Ethernet) and Kvaser (USB) are supported.""")
if __name__ == "__main__":
    pass
    
                