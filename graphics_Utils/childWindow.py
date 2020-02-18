from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from graphics_Utils import dataMonitoring ,logWindow
from analysis import logger, analysis_utils ,controlServer
import numpy as np
import os
import binascii
rootdir = os.path.dirname(os.path.abspath(__file__)) 
class ChildWindow(QWidget):  
    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent) 
       conf = analysis_utils.open_yaml_file(file ="MoPS_daq_cfg.yml",directory =rootdir[:-14])
       self.__appName = conf['Application']['app_name']
       self.__version = conf['Application']['version']
       self.__interface= conf['CAN_Interface']['AnaGate']['name']
       self.__interfaceItems = conf['Application']["interface_items"]
       self.__channel = conf['CAN_Interface']['AnaGate']['channel']
       self.__ipAddress = conf['CAN_Interface']['AnaGate']['ipAddress']
       self.__bitrate =conf['CAN_Interface']['AnaGate']['bitrate']
       self.__Bytes =  ["40","0","34","1","0","0","0","0"] 
       self.__cobid = "608"
       self.__dlc = "8"
       self.server = controlServer.ControlServer(interface ="AnaGate")
    
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
        FirstGridLayout =  QGridLayout() 
        cobidLabel = QLabel("CAN Identifier", ChildWindow)
        cobidLabel.setText("CAN Identifier:")
        cobidtextbox = QLineEdit(self.__cobid, ChildWindow)
        cobidtextbox.textChanged.connect(self.set_cobid)
        
        channelLabel = QLabel("Channel        :", ChildWindow)
        channelLabel.setText("Channel         :")
        canitems = ["CAN1"]
        canComboBox = QComboBox(ChildWindow)
        for item in canitems: canComboBox.addItem(item)
        canComboBox.activated[str].connect(self.clicked)


        dlcLabel = QLabel("DLC            :", ChildWindow)
        dlcLabel.setText("DLC            :")
        dlctextbox = QLineEdit(self.__dlc, ChildWindow)
        dlctextbox.textChanged.connect(self.set_dlc)

        
        FirstGridLayout.addWidget(cobidLabel,0,0)
        FirstGridLayout.addWidget(cobidtextbox,0,1)
                
        FirstGridLayout.addWidget(channelLabel,1,0)
        FirstGridLayout.addWidget(canComboBox,1,1)        
        
        FirstGridLayout.addWidget(dlcLabel,2,0)
        FirstGridLayout.addWidget(dlctextbox,2,1)  
       #self.outLabel.setStyleSheet("background-color: white; border: 2px inset black;")# min-height: 200px;")        
        FirstGroupBox.setLayout(FirstGridLayout) 
        
        SecondGroupBox = QGroupBox("Message Data")
        #comboBox and label for channel
        SecondGridLayout =  QGridLayout()
        ByteList = ["Byte0 :","Byte1 :","Byte2 :","Byte3 :","Byte4 :","Byte5 :","Byte6 :","Byte7 :"] 
        LabelByte =[ByteList[i] for i in np.arange(len(ByteList))]
        textbox = [ByteList[i] for i in np.arange(len(ByteList))]
        textboxValue = [ByteList[i] for i in np.arange(len(ByteList))]
        for i in np.arange(len(ByteList)):
            LabelByte[i] = QLabel(ByteList[i], ChildWindow)
            LabelByte[i].setText(ByteList[i])
            textbox[i] = QLineEdit(self.__Bytes[i], ChildWindow)
            textboxValue[i] = textbox[i].text()
            def set_byte(text=None, i=i):
                self.__Bytes[i] = text
            textbox[i].textChanged.connect(set_byte)
            if i<=3:
                SecondGridLayout.addWidget(LabelByte[i],i,0)
                SecondGridLayout.addWidget(textbox[i],i,1)
            else:
                SecondGridLayout.addWidget(LabelByte[i],i-4,4)
                SecondGridLayout.addWidget(textbox[i],i-4,5)
                         
        SecondGroupBox.setLayout(SecondGridLayout) 
        
        HBox= QHBoxLayout()
        send_button = QPushButton("Send")
        send_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        send_button.clicked.connect(self.send_can)
        
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_Utils/icons/icon_close.jpg'))
        close_button.clicked.connect(ChildWindow.close)

        HBox.addWidget(send_button)
        HBox.addWidget(close_button)
                 
        MainLayout.addWidget(FirstGroupBox ,0,0)
        MainLayout.addWidget(SecondGroupBox ,1,0)
        MainLayout.addLayout(HBox ,2,0)
        
        ChildWindow.setCentralWidget(plotframe)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def outputChildWindow(self, ChildWindow, comunication_object ="Normal"):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(600, 600) #w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        logTextBox = logWindow.QTextEditLogger(ChildWindow,comunication_object = comunication_object)
        logLayout = QVBoxLayout()
        logLayout.addWidget(logTextBox.text_edit_widget)
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
        __interfaceItems = self.__interfaceItems
        interfaceComboBox = QComboBox(ChildWindow)
        for item in __interfaceItems: interfaceComboBox.addItem(item)
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
        self._createStatusBar(ChildWindow)
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
            SubSecondGridLayout.addWidget(firstComboBox,0,1)
            
        if (interface == "AnaGate"):
            firstLabel.setText("IP address")
            firsttextbox = QLineEdit(self.__ipAddress,ChildWindow)
            firsttextbox.textChanged.connect(self.set_ipAddress)
            #self.__ipAddress = firsttextbox.text()
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
            secondLabel.setText("")
            seconditems = [""]
            secondComboBox = QComboBox(ChildWindow)
            for item in seconditems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("")
            thirdItems = [""]
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

    def _createStatusBar(self,childwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        childwindow.setStatusBar(status)
        
    def clicked(self,q):
        print("is clicked")
        
    # setter method
    def set_clicked(self,x):
        print(x)
        
    def set_cobid(self, x):
        self.__cobid = x
    
    def set_dlc(self,x):
        self.__dlc = x
    
    def set_Bytes(self,x):
        self.__Bytes = x

    def set_interface(self, x): 
        self.__interface = x 
    
    def set_bitrate(self,x):
        self.__bitrate = x        

    def set_ipAddress(self,x):
        self.__ipAddress = x  
                    
    def set_connect(self):
        interface = self.get_interface()
        ipAddress = self.get_ipAddress()
        channel = int(self.get_channel())
        bitrate = int(self.get_bitrate())
        self.server.start_channelConnection(interface = interface, ipAddress = ipAddress, channel = channel, baudrate = bitrate)

    def set_all(self):
        self.server.set_interface(self.__interface)
        self.server.set_ipAddress(self.__ipAddress)
        self.server.set_bitrate(self.__bitrate)
    
    def send_can(self):
        cobid = int(self.get_cobid())
        bytes =list( map(int, self.get_Bytes()))
        self.server.writeCanMessage(cobid, bytes, flag=0, timeout=1000)
    #Get functions    
    def get_appName(self):
        return self.__appName 
    
    def get_version(self):
        return self.__version
    
    def get_channel(self):
        return self.__channel
    
    def get_cobid(self):
        return  self.__cobid
    def get_dlc(self):
        return self.__dlc

    def get_Bytes(self):
        return self.__Bytes    
    def get_interface(self): 
        return self.__interface 
    
    def get_bitrate(self):
        return self.__bitrate        

    def get_ipAddress(self):
        return self.__ipAddress
        
if __name__ == "__main__":
    pass

