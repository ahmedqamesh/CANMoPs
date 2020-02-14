from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from graphics_Utils import mainWindow, dataMonitoring , menuWindow ,logWindow
from analysis import controlServer
import numpy as np
ipAddress = '192.168.1.254'  
class ChildWindow(QWidget):  
    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent) 
       self.menu= menuWindow.MenuBar()
       self.mainWindow = mainWindow.MainWindow()
       
       
       self.server =controlServer.ControlServer()
       self.__interface =self.server.get_interface
       self.__ipAddress =self.server.get_ipAddress
       self.__bitrate =self.server.get_bitrate
       #self.menu._createStatusBar()
       
    def canMessageChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("canMessageChildWindow")
        ChildWindow.setWindowTitle("CAN Message")
        ChildWindow.resize(310, 600) #w*h
        #Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        MainLayout = QGridLayout()
        
        FirstGroupBox = QGroupBox("")
        #comboBox and label for channel
        HGridLayout =  QGridLayout() 
        firstLabel = QLabel("CAN Identifier", ChildWindow)
        firstLabel.setText("CAN Identifier:")
        firsttextbox = QLineEdit(ChildWindow)
        firsttextboxValue = firsttextbox.text()
        HGridLayout.addWidget(firstLabel,0,0)
        HGridLayout.addWidget(firsttextbox,0,1)
        seondLabel = QLabel("Channel        :", ChildWindow)
        seondLabel.setText("Channel         :")
        seonditems = ["CAN1"]
        seondComboBox = QComboBox(ChildWindow)
        for item in seonditems: seondComboBox.addItem(item)
        seondComboBox.activated[str].connect(self.clicked)
        HGridLayout.addWidget(seondLabel,1,0)
        HGridLayout.addWidget(seondComboBox,1,1)

        thirdLabel = QLabel("CAN Identifier:", ChildWindow)
        thirdLabel.setText("CAN Identifier:")
        thirdtextbox = QLineEdit(ChildWindow)
        thirdtextboxValue = thirdtextbox.text()
        HGridLayout.addWidget(thirdLabel,2,0)
        HGridLayout.addWidget(thirdtextbox,2,1)
       #self.outLabel.setStyleSheet("background-color: white; border: 2px inset black;")# min-height: 200px;")
        
        set_button = QPushButton("Set")
        set_button.clicked.connect(self.set_click)
        
        close_button = QPushButton("close")
        close_button.clicked.connect(ChildWindow.close) 
        FirstGroupBox.setLayout(HGridLayout) 
        
        MainLayout.addWidget(FirstGroupBox ,0,0)
        MainLayout.addWidget(set_button ,1,0)
        MainLayout.addWidget(close_button ,1,1)
        
        ChildWindow.setCentralWidget(plotframe)
        plotframe.setLayout(MainLayout) 
        
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
        logEdit= logWindow.LoggerDialog()
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
        Fig = dataMonitoring.LiveMonitoringData()
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
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        #Define First Group
        FirstGroupBox= QGroupBox("Bus Statistics")
        FirstGridLayout =  QGridLayout()
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)
        
        FirstGridLayout.addWidget(clear_button,0,0)
        FirstGroupBox.setLayout(FirstGridLayout)
        
        #Define the second group
        SecondGroupBox= QGroupBox("Bus Configuration")
        SecondGridLayout =  QGridLayout()        
        #comboBox and label for channel
        chLabel = QLabel("CAN Channel:", ChildWindow)
        chLabel.setText("CAN Channel:")
        controllerLayout = QHBoxLayout()
        interfaceitems = ["----","Kvaser","AnaGate","Others"]
        interfaceComboBox = QComboBox(ChildWindow)
        for item in interfaceitems: interfaceComboBox.addItem(item)
        interfaceComboBox.activated[str].connect(self.set_interface)
        
        controllerLayout.addWidget(interfaceComboBox)
        
        #Another group will be here for Bus parameters
        self.BusParametersGroupBox()
        
        modeLabel = QLabel("CAN Mode:", ChildWindow)
        modeLabel.setText("CAN Mode:")
        modeitems = ["CAN"]
        modeComboBox = QComboBox(ChildWindow)
        for item in modeitems: modeComboBox.addItem(item)
        modeComboBox.activated[str].connect(self.clicked)

        #FirstButton
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)

        HGridLayout =  QGridLayout()  
        set_button = QPushButton("Set in all")
        set_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        set_button.clicked.connect(self.set_all)
        
        h , w = 50 , 25
        connectButton = QPushButton("")
        connectButton.setFixedWidth(w)
        connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        connectButton.setIcon(icon)
        connectButton.setCheckable(True)
        connectButton.clicked.connect(self.set_connect) 
        
        setLabel = QLabel("Set same bit rate in all CAN controllers", ChildWindow)
        setLabel.setText("Set same bit rate in all CAN controllers")
        
        HGridLayout.addWidget(set_button,0,0)
        HGridLayout.addWidget(connectButton,0,1) 
        HGridLayout.addWidget(setLabel,0,2)
        
        SecondGroupBox.setLayout(SecondGridLayout)
        SecondGridLayout.addWidget(chLabel,0,0)
        SecondGridLayout.addLayout(controllerLayout,1,0)
        SecondGridLayout.addWidget(modeLabel,2,0)
        SecondGridLayout.addWidget(modeComboBox,3,0)
        
        def _interfaceParameters():
            SecondGridLayout.removeWidget(self.SubSecondGroupBox)
            self.SubSecondGroupBox.deleteLater()
            self.SubSecondGroupBox = None              
            self.BusParametersGroupBox(ChildWindow= ChildWindow ,interface =  self.__interface)
            SecondGridLayout.addWidget(self.SubSecondGroupBox,4,0)        
        SecondGridLayout.addLayout(HGridLayout,5,0)
        interfaceComboBox.activated[str].connect(_interfaceParameters)
        #Define Third Group
        ThirdGroupBox= QGroupBox("Bus Status")
        ThirdGridLayout =  QGridLayout()
        
        go_button = QPushButton("Go On Bus")
        go_button.setIcon(QIcon('graphics_Utils/icons/icon_reset.png'))
        go_button.clicked.connect(ChildWindow.close)
        
        ThirdGridLayout.addWidget(go_button,0,0)
        ThirdGroupBox.setLayout(ThirdGridLayout)
        MainLayout.addWidget(FirstGroupBox, 0, 0)
        MainLayout.addWidget(SecondGroupBox, 1, 0)
        MainLayout.addWidget(ThirdGroupBox, 2, 0)
        plotframe.setLayout(MainLayout) 
        self.menu._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)        
        

    def BusParametersGroupBox(self, ChildWindow = None,interface ="Others"):
        #Define subGroup
        self.SubSecondGroupBox= QGroupBox("Bus Parameters")
        SubSecondGridLayout =  QGridLayout()
        firstLabel= QLabel("firstLabel", ChildWindow)
        secondLabel = QLabel("secondLabel", ChildWindow)
        thirdLabel = QLabel("thirdLabel", ChildWindow)
        firstComboBox = QComboBox(ChildWindow)
        if (interface == "Kvaser"):
            firstLabel.setText("Bus Speed:")
            firstItems = ["1000 kbit/s, 75.0%","500 kbit/s, 75.0%","250 kbit/s, 75.0%"," 125 kbit/s, 75.0%","100 kbit/s, 75.0%","83.333 kbit/s, 75.0%","62.500 kbit/s, 75.0%","50 kbit/s, 75.0%","33.333 kbit/s, 75.0%" ]
            for item in firstItems: firstComboBox.addItem(item)
            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            secondItems = ["1","2","3","4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = ["10000", "20000", "50000", "62500", "100000", "125000", "250000", "500000","1000000"]
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            print(str)
            SubSecondGridLayout.addWidget(firstComboBox,0,1)
            
        if (interface == "AnaGate"):
            firstLabel.setText("IP address")
            firsttextbox = QLineEdit(ipAddress,ChildWindow)
            self.__ipAddress = firsttextbox.text()
            secondLabel.setText("SJW:")
            secondItems = ["1","2","3","4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = ["10000", "20000", "50000", "62500", "100000", "125000", "250000", "500000","1000000"]
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            SubSecondGridLayout.addWidget(firsttextbox,0,1)
            
        if (interface == "Others"):        
            firstLabel.setText("Speed:")
            firstItems = [""]
            firstComboBox = QComboBox(ChildWindow)
            for item in firstItems: firstComboBox.addItem(item)
            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            seconditems = [""]
            secondComboBox = QComboBox(ChildWindow)
            for item in seconditems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = ["10000", "20000", "50000", "62500", "100000", "125000", "250000", "500000","1000000"]
            thirdComboBox = QComboBox(ChildWindow)
            thirdComboBox.activated[str].connect(self.set_bitrate)
            for item in thirdItems: thirdComboBox.addItem(item)
            SubSecondGridLayout.addWidget(firstComboBox,0,1)
        else:
            pass   
        
        SubSecondGridLayout.addWidget(firstLabel,0,0)
        SubSecondGridLayout.addWidget(secondLabel,1,0)
        SubSecondGridLayout.addWidget(secondComboBox,1,1)
        SubSecondGridLayout.addWidget(thirdLabel,2,0)
        SubSecondGridLayout.addWidget(thirdComboBox,2,1)
        self.SubSecondGroupBox.setLayout(SubSecondGridLayout)
        
    def deleteGridWidget(self, index):
        item = self.sa_grid.itemAt(index)
        if item is not None:
            widget = item.widget()
            if widget is not None:
                self.sa_grid.removeWidget(widget)
                widget.deleteLater()

    def clicked(self,q):
        print("is clicked")
        
    # setter method 
    def set_label(self, text):
        self.outLabel.setText(text)
    
    def set_connect(self):
        self.server.start_channelConnection()

    def set_all(self):
        self.server.set_interface(self.__interface)
        self.server.set_ipAddress(self.__ipAddress)
        print(self.__interface , self.__ipAddress , self.__bitrate)
        self.server.set_bitrate(self.__bitrate)
    
    def set_interface(self, x): 
        self.__interface = x 
    
    def set_bitrate(self,x):
        self.__bitrate = x        

if __name__ == "__main__":
    pass

