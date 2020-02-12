from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from graphics_Utils import DataMonitoring , MenuWindow , LogWindow
import numpy as np
class Ui_ChildWindow(QWidget):  
    def __init__(self):
       super().__init__() 
       self.menu= MenuWindow.MenuBar()
       #self.menu._createStatusBar(self)
       
    def settingChannel(self, ChildWindow):
        ChildWindow.setObjectName("ChildWindow")
        ChildWindow.setWindowTitle("Motor stage settings")
        #ChildWindow.resize(568, 109) 
        ChildWindow.setGeometry(300, 300, 300, 200)            
        plotframe = QFrame(ChildWindow)
        plotframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        self.mainGroupBox = QGroupBox("Set channel")
        mainLayout = QGridLayout()
                
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

        plotframe.setLayout(mainLayout) 
        
        self.statusbar = QtWidgets.QStatusBar(ChildWindow)
        self.statusbar.setObjectName("statusbar")
        ChildWindow.setStatusBar(self.statusbar)
        self.menu._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def outputChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(600, 600) #w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        logEdit= LogWindow.LoggerDialog()
        logLayout = QVBoxLayout()
        logLayout.addWidget(logEdit)
        self.WindowGroupBox.setLayout(logLayout)
        logframe.setLayout(logLayout) 
        
    def trendChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(500, 500) #w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        Fig = DataMonitoring.LiveMonitoringData()
        plotLayout = QVBoxLayout()
        plotLayout.addStretch(1)
        plotLayout.addWidget(Fig)
        self.WindowGroupBox.setLayout(plotLayout)
        logframe.setLayout(plotLayout) 
        
                
                
    def canSettingsChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("CANSettings")
        ChildWindow.setWindowTitle("CAN Settings")
        ChildWindow.resize(310, 600) #w*h
        MainLayout = QGridLayout()
        
        #Define a frame for that group
        plotframe = QFrame(ChildWindow)
        #plotframe.setStyleSheet("QWidget { background-color: #eeeeec; }")
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        #Define First Group
        self.FirstGroupBox= QGroupBox("Bus Statistics")
        FirstGridLayout =  QGridLayout()
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)
        
        FirstGridLayout.addWidget(clear_button,0,0)
        self.FirstGroupBox.setLayout(FirstGridLayout)
        
        #Define the second group
        self.SecondGroupBox= QGroupBox("Bus Configuration")
        SecondGridLayout =  QGridLayout()        
        #comboBox and label for channel
        chLabel = QLabel("CAN Channel:", ChildWindow)
        chLabel.setText("CAN Channel:")
        chitems = ["Kvaser","Anagate","Others"]
        chComboBox = QComboBox(ChildWindow)
        for item in chitems: chComboBox.addItem(item)
        chComboBox.activated[str].connect(self.set_channel)
        
        modeLabel = QLabel("CAN Mode:", ChildWindow)
        modeLabel.setText("CAN Mode:")
        modeitems = ["CAN"]
        modeComboBox = QComboBox(ChildWindow)
        for item in modeitems: modeComboBox.addItem(item)
        modeComboBox.activated[str].connect(self.set_channel)

        #Another group will be here for Bus parameters
        #Define subGroup
        self.SubSecondGroupBox= QGroupBox("Bus Parameters")
        SubSecondGridLayout =  QGridLayout()
        
        speedLabel = QLabel("Bus Speed:", ChildWindow)
        speedLabel.setText("Bus Speed:")
        speeditems = ["1000 kbit/s, 75.0%","500 kbit/s, 75.0%","250 kbit/s, 75.0%"," 125 kbit/s, 75.0%","100 kbit/s, 75.0%","83.333 kbit/s, 75.0%","62.500 kbit/s, 75.0%","50 kbit/s, 75.0%","33.333 kbit/s, 75.0%" ]
        speedComboBox = QComboBox(ChildWindow)
        for item in speeditems: speedComboBox.addItem(item)
        speedComboBox.activated[str].connect(self.set_channel)
        
        SJWLabel = QLabel("SJW:", ChildWindow)
        SJWLabel.setText("SJW:")
        SJWitems = ["1","2","3","4"]
        SJWComboBox = QComboBox(ChildWindow)
        for item in SJWitems: SJWComboBox.addItem(item)
        SJWComboBox.activated[str].connect(self.set_channel)
        
        bitLabel = QLabel("Bit Timing:", ChildWindow)
        bitLabel.setText("Bit Timing:")
        
        SubSecondGridLayout.addWidget(speedLabel,0,0)
        SubSecondGridLayout.addWidget(speedComboBox,0,1)
        SubSecondGridLayout.addWidget(SJWLabel,1,0)
        SubSecondGridLayout.addWidget(SJWComboBox,1,1)
        SubSecondGridLayout.addWidget(bitLabel,2,0)               
        self.SubSecondGroupBox.setLayout(SubSecondGridLayout)
        
        #FirstButton
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)

        HGridLayout =  QGridLayout()  
        set_button = QPushButton("Set in all")
        set_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        set_button.clicked.connect(self.set_click)
        
        setLabel = QLabel("Set same bit rate in all CAN controllers", ChildWindow)
        setLabel.setText("Set same bit rate in all CAN controllers")
        HGridLayout.addWidget(set_button,0,0)
        HGridLayout.addWidget(setLabel,0,1)
        
        SecondGridLayout.addWidget(chLabel,0,0)
        SecondGridLayout.addWidget(chComboBox,1,0)
        SecondGridLayout.addWidget(modeLabel,2,0)
        SecondGridLayout.addWidget(modeComboBox,3,0)
        SecondGridLayout.addLayout(HGridLayout,4,0)
        SecondGridLayout.addWidget(self.SubSecondGroupBox,5,0)
        self.SecondGroupBox.setLayout(SecondGridLayout)
        
        #Define Third Group
        self.ThirdGridBox= QGroupBox("Bus Status")
        ThirdGridLayout =  QGridLayout()
        
        go_button = QPushButton("Go On Bus")
        go_button.setIcon(QIcon('graphics_Utils/icons/icon_reset.png'))
        go_button.clicked.connect(ChildWindow.close)
        
        ThirdGridLayout.addWidget(go_button,0,0)
        self.ThirdGridBox.setLayout(ThirdGridLayout)

        
        MainLayout.addWidget(self.FirstGroupBox, 0, 0)
        MainLayout.addWidget(self.SecondGroupBox, 1, 0)
        MainLayout.addWidget(self.ThirdGridBox, 2, 0)
        plotframe.setLayout(MainLayout) 

        self.menu._createStatusBar(ChildWindow)
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

