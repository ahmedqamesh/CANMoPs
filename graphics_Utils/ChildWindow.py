from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from graphics_Utils import DataMonitoring , MenuWindow
import numpy as np
class Ui_ChildWindow(QWidget):  
    def __init__(self):
       super().__init__() 

    def settingChannel(self, ChildWindow):
        ChildWindow.setObjectName("ChildWindow")
        #ChildWindow.resize(568, 109) 
        ChildWindow.setGeometry(300, 300, 300, 200)            
        
        self.mainGroupBox = QGroupBox("Set channel")
        mainLayout = QGridLayout()
        
        plotframe = QFrame(ChildWindow)
        plotframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        #comboBox and label for channel
        chLabel = QLabel("Channel", ChildWindow)
        chLabel.setText("Select Channel Number")

        items = ["---","ch01","ch02","ch03"]
        chComboBox = QComboBox(ChildWindow)
        for item in items: chComboBox.addItem(item)
        chComboBox.activated[str].connect(self.set_channel)

#         chComboBox.currentTextChanged.connect(self.on_combobox_changed)
#         listwidgetLayout = QHBoxLayout()
#         chlistwidget = QListWidget()
#         chlistwidget.insertItem(0, "Ch1")
#         chlistwidget.insertItem(1, "Ch2")
#         chlistwidget.insertItem(2, "Ch3")
#         chlistwidget.clicked.connect(self.setaddress(ChildWindow))
#         chlistwidget.clicked.connect(self.setaddress(ChildWindow))
#         listwidgetLayout.addWidget(chlistwidget)
                  
         #comboBox  and label  for coordinates
        dimLabel = QLabel("Coordinate", ChildWindow)
        dimLabel.setText("Choose coordinate")
        
        items = ["---","x","y","z"]
        dimComboBox = QComboBox(ChildWindow)
        for item in items: dimComboBox.addItem(item)
        dimComboBox.activated[str].connect(self.set_dimention)
#         dimlistwidget = QListWidget()
#         dimlistwidget.insertItem(0, "x")
#         dimlistwidget.insertItem(1, "y")
#         dimlistwidget.insertItem(2, "z")
#         dimlistwidget.clicked.connect(self.setaddress)
#         listwidgetLayout.addWidget(dimlistwidget)
#         
#         Set_button = QPushButton("Set")
#         listwidgetLayout.addWidget(Set_button)
#         Set_button.clicked.connect(self.setaddress) 
#         childLayout.addLayout(listwidgetLayout)
          
        self.outLabel = QLabel("channel settings",ChildWindow)
        self.outLabel.setStyleSheet("background-color: white; border: 2px inset black;")# min-height: 200px;")
        
        set_button = QPushButton("Set")
        set_button.clicked.connect(self.set_click)
        
        close_button = QPushButton("close")
        close_button.clicked.connect(ChildWindow.close)

        gridLayout = QGridLayout()
        gridLayout.addWidget(chLabel,0,0)
        gridLayout.addWidget(chComboBox,1,0)
        
        gridLayout.addWidget(dimLabel,2,0)
        gridLayout.addWidget(dimComboBox,3,0)
        
        
        gridLayout.addWidget(self.outLabel,4,0)
        gridLayout.addWidget(set_button,4,1)    
        self.mainGroupBox.setLayout(gridLayout) 
        
        
        mainLayout.addWidget(self.mainGroupBox, 0, 0)
        mainLayout.addWidget(close_button,1,0) 
        
        plotframe.setLayout(mainLayout) 
        
        self.statusbar = QtWidgets.QStatusBar(ChildWindow)
        self.statusbar.setObjectName("statusbar")
        ChildWindow.setStatusBar(self.statusbar)
        ChildWindow.setWindowTitle("Motor stage settings")
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def set_label(self, text):
        self.outLabel.setText(text)

    def set_click(self):
        dim = self.get_dimention()
        ch = self.get_channel()
        text = "%s will be set to  %s direction"%(ch,dim)
        print(text)
        
    # setter method 
    def set_channel(self, x): 
        self._channel = x 
    
    def set_dimention(self, x): 
        self._dim = x
        dim = self.get_dimention()
        ch = self.get_channel()
        text = "%s will be set to  %s direction"%(ch,dim)
        self.outLabel.setText(text)
        self.outLabel.adjustSize()
        
    # getter methods
    def get_channel(self): 
        return self._channel 
    
    def get_dimention(self): 
        return self._dim
        

        

if __name__ == "__main__":
    pass

