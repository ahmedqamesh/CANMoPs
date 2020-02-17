import sys
import logging
loglevel = logging.getLogger('Analysis').getEffectiveLevel()
from analysis import logger
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from graphics_Utils import dataMonitoring , childWindow ,logWindow

class MenuBar(QWidget):  
    def __init__(self,parent = None):
        super(MenuBar,self).__init__(parent)
        self.MainWindow = QMainWindow()
        
    def _createMenu(self,mainwindow):
        menuBar = mainwindow.menuBar()
        menuBar.setNativeMenuBar(False) #only for MacOS
        self._fileMenu(menuBar,mainwindow)
        self._viewMenu(menuBar, mainwindow)
        self._settingsMenu(menuBar, mainwindow)
        self._helpMenu(menuBar, mainwindow)
        self.ui = childWindow.ChildWindow()
    
    def _createtoolbar(self,mainwindow):
        toolbar = mainwindow.addToolBar("tools")
        self._toolBar(toolbar,mainwindow)
        
    # 1. File menu
    def _fileMenu(self,menuBar,mainwindow):
               
        fileMenu = menuBar.addMenu('&File')

        new_action = QAction(QIcon('graphics_Utils/icons/icon_new.png'), '&New', mainwindow)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New start')
        new_action.triggered.connect(self.clicked)
        
        open_action = QAction(QIcon('graphics_Utils/icons/icon_open.png'), '&Open', mainwindow)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('open session') # show when move mouse to the icon
        open_action.triggered.connect(self.clicked)
        
        save_action = QAction(QIcon('graphics_Utils/icons/icon_save.png'), '&Save', mainwindow)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save program') # show when move mouse to the icon
        save_action.triggered.connect(self.clicked)
        
        close_action = QAction('&Close', mainwindow)
        close_action.setStatusTip('close session') # show when move mouse to the icon
        close_action.triggered.connect(qApp.quit)
                        

        
        exit_action = QAction(QIcon('graphics_Utils/icons/icon_exit.png'), '&Exit', mainwindow)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit program')
        exit_action.triggered.connect(qApp.quit)
        
        fileMenu.addAction(new_action)
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)
        fileMenu.addAction(close_action)
        fileMenu.addSeparator()
        fileMenu.addAction(exit_action)
        
    # 2. View menu
    def _viewMenu(self,menuBar,mainwindow):
        viewMenu = menuBar.addMenu("&View")
        canSettings_action = QAction('&CAN Settings', mainwindow, checkable=True)
        canSettings_action.setStatusTip('CAN Settings')
        canSettings_action.setChecked(False)
        canSettings_action.triggered.connect(self.canSettingsChildWindow)

        
        canMessage_action = QAction('&CAN Message', mainwindow, checkable=True)
        canMessage_action.setStatusTip('CAN Message')
        canMessage_action.setChecked(False)
        canMessage_action.triggered.connect(self.canMessageChildWindow)

        outWindow_action = QAction('&Output Window', mainwindow, checkable=True)
        outWindow_action.setStatusTip('Output Window')
        outWindow_action.setChecked(False)
        outWindow_action.triggered.connect(self.outputChildWindow)
                
        trend_action = QAction('&Data Trending', mainwindow, checkable=True)
        trend_action.setStatusTip('Data Trending')
        trend_action.setChecked(False)
        trend_action.triggered.connect(self.trendChildWindow)
        
        viewMenu.addAction(canSettings_action)
        viewMenu.addAction(canMessage_action)
        viewMenu.addAction(outWindow_action)
        viewMenu.addAction(trend_action)
    
     # 3. Settings menu
    def _settingsMenu(self,menuBar,mainwindow): 
        settings_menu = menuBar.addMenu("&Settings")
        
        settings_action = QAction(QIcon('graphics_Utils/icons/icon_settings.png'), '&Settings', mainwindow)        
        settings_action.setStatusTip('settings action')
        settings_action.setChecked(True)
        settings_action.triggered.connect(self.openWindow)
        settings_menu.addAction(settings_action)             
        
    # 4. Help menu
    def _helpMenu(self,menuBar,mainwindow):
        helpmenu = menuBar.addMenu("&Help")
 
        contents_action = QAction('&Contents', mainwindow)
        contents_action.setStatusTip("Contents")
        contents_action.triggered.connect(self.clicked)
              
        about_action = QAction('&About', mainwindow)
        about_action.setStatusTip("About")
        about_action.triggered.connect(self.about)
        
        helpmenu.addAction(contents_action)
        helpmenu.addAction(about_action)
    
    #make a toolbar         
    def _toolBar(self,toolbar, mainwindow):
        
        new_action = QAction(QIcon('graphics_Utils/icons/icon_new.png'), '&New', mainwindow)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New start')
        new_action.triggered.connect(self.clicked)
        
        open_action = QAction(QIcon('graphics_Utils/icons/icon_open.png'), '&Open', mainwindow)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('open session') # show when move mouse to the icon
        open_action.triggered.connect(self.clicked)
        
        save_action = QAction(QIcon('graphics_Utils/icons/icon_save.png'), '&Save', mainwindow)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save program') # show when move mouse to the icon
        save_action.triggered.connect(self.clicked)

        start_action = QAction(QIcon('graphics_Utils/icons/icon_start.png'), '&Start', mainwindow)
        start_action.setStatusTip('Start session') # show when move mouse to the icon
        start_action.triggered.connect(self.clicked)

        pause_action = QAction(QIcon('graphics_Utils/icons/icon_pause.png'), '&Pause', mainwindow)
        pause_action.setStatusTip('Pause program') # show when move mouse to the icon
        pause_action.triggered.connect(self.clicked)
                
        stop_action = QAction(QIcon('graphics_Utils/icons/icon_stop.png'), '&Stop', mainwindow)
        stop_action.setStatusTip('Stop program') # show when move mouse to the icon
        stop_action.triggered.connect(self.clicked)
   
        toolbar.addAction(new_action)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(start_action)
        toolbar.addAction(pause_action)
        toolbar.addAction(stop_action)
                     
    def _createStatusBar(self,mainwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        mainwindow.setStatusBar(status)

    # Functions to run
    def canMessageChildWindow(self, state):
        if state:
            self.ui.canMessageChildWindow(self.MainWindow)
            self.MainWindow.show()
        else:
            pass
    
    def canSettingsChildWindow(self,state):
        if state:
            self.ui.canSettingsChildWindow(self.MainWindow)
            self.MainWindow.show()
        else:
            pass
   
    def outputChildWindow(self,state):
        if state:
            self.ui.outputChildWindow(self.MainWindow)
            self.MainWindow.show()
        else:
            pass
    
    def trendChildWindow(self,state):
        if state:
            self.ui.trendChildWindow(self.MainWindow)
            self.MainWindow.show()
        else:
            pass

    def about(self):
        QMessageBox.about(self,"About",
        """embedding_in_qt5.py example
        Copyright 2015 BoxControL
        This program is a simple example of a Qt5 application embedding matplotlib
        canvases. It is base on example from matplolib documentation, and initially was
        developed from Florent Rougon and Darren Dale.
        http://matplotlib.org/examples/user_interfaces/embedding_in_qt4.html
        It may be used and modified with no restriction; raw copies as well as
        modified versions may be distributed without limitation.""")

    def openWindow(self):
        self.ui.settingChannel(self.MainWindow)
        self.mainwindow.show()
        
    def clicked(self,q):
        print("is clicked")
        
if __name__ == "__main__":
    pass
    
                