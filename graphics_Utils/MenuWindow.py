import sys
import logging
loglevel = logging.getLogger('Analysis').getEffectiveLevel()
from analysis import logger
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from graphics_Utils import DataMonitoring , MenuWindow , ChildWindow ,LogWindow

class MenuBar(QWidget):  
    def __init__(self,parent = None):
        super(MenuBar,self).__init__(parent)

    def _createMenu(self,mainwindow):
        menuBar = mainwindow.menuBar()
        menuBar.setNativeMenuBar(False) #only for MacOS
        self._fileMenu(menuBar,mainwindow)
        self._viewMenu(menuBar, mainwindow)
        self._settingsMenu(menuBar, mainwindow)
        self._helpMenu(menuBar, mainwindow)
    
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
        trend_action = QAction('&Open trending plot', mainwindow, checkable=True)
        trend_action.setStatusTip('Open trending plot')
        trend_action.setChecked(True)
        trend_action.triggered.connect(self.toggleMenu)
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
    def toggleMenu(self, state):
        if state:
            self.openWindow()
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
        self.mainwindow = QMainWindow()
        self.ui = ChildWindow.Ui_ChildWindow()
        self.ui.settingChannel(self.mainwindow)
        self.mainwindow.show()
        
    def clicked(self,q):
        print("is clicked")
        
if __name__ == "__main__":
    pass
    
                