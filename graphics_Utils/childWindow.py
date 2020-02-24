from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from graphics_Utils import mainWindow, dataMonitoring , logWindow 
from analysis import logger, analysis_utils, controlServer
import numpy as np
import os
import binascii
from analysis import logger
import logging
rootdir = os.path.dirname(os.path.abspath(__file__)) 


class ChildWindow(QWidget):  

    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent)
       self.main = mainWindow.MainWindow()
       self.__interfaceItems = self.main.get_interfaceItems()
       self.__icon_dir = self.main.get_icon_dir()
       self.__dictionary_items = self.main.get_dictionary_items()
       self.__index_items = self.main.get_index_items()

       self.server = controlServer.ControlServer()
       self.__nodeIds = self.server.get_nodeIds()       
       self.__cobid = self.server.get_cobid()
       self.__dlc = self.server.get_dlc()
       self.__Bytes = self.server.get_bytes()
       self.index_description_items = None
       self.subIndex_description_items = None
       
       
    def canSettingsChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("CANSettings")
        ChildWindow.setWindowTitle("CAN Settings")
        ChildWindow.resize(310, 600)  # w*h
        MainLayout = QGridLayout()
        
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        
        # Define First Group
        FirstGroupBox = QGroupBox("Bus Statistics")
        FirstGridLayout = QGridLayout()
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)
        
        FirstGridLayout.addWidget(clear_button, 0, 0)
        FirstGroupBox.setLayout(FirstGridLayout)
        
        # Define the second group
        SecondGroupBox = QGroupBox("Bus Configuration")
        SecondGridLayout = QGridLayout()        
        # comboBox and label for channel
        chLabel = QLabel("CAN Channel:", ChildWindow)
        chLabel.setText("CAN Channel:")
        controllerLayout = QHBoxLayout()
        __interfaceItems = self.__interfaceItems
        interfaceComboBox = QComboBox(ChildWindow)
        for item in __interfaceItems: interfaceComboBox.addItem(item)
        #interfaceComboBox.activated[str].connect(self.main.set_interface)
        interfaceComboBox.activated[str].connect(self.main.applyInterfaceChildComboBoxChanges)
        
        controllerLayout.addWidget(interfaceComboBox)
        
        # Another group will be here for Bus parameters
        self.BusParametersGroupBox()
        modeLabel = QLabel("CAN Mode:", ChildWindow)
        modeLabel.setText("CAN Mode:")
        modeitems = ["CAN"]
        modeComboBox = QComboBox(ChildWindow)
        for item in modeitems: modeComboBox.addItem(item)
        #modeComboBox.activated[str].connect(self.clicked)

        # FirstButton
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(ChildWindow.close)

        HGridLayout = QGridLayout()  
        set_button = QPushButton("Set in all")
        set_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        set_button.clicked.connect(self.applyLineEditChanges)
        set_button.clicked.connect(self.main.set_all)
        
        h , w = 50 , 25
        connectButton = QPushButton("")
        connectButton.setFixedWidth(w)
        connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal, QIcon.On)
        connectButton.setIcon(icon)
        connectButton.setCheckable(True)
        connectButton.clicked.connect(self.main.set_connect) 
        
        setLabel = QLabel("Set same bit rate in all CAN controllers", ChildWindow)
        setLabel.setText("Set same bit rate in all CAN controllers")
        
        HGridLayout.addWidget(set_button, 0, 0)
        HGridLayout.addWidget(connectButton, 0, 1) 
        HGridLayout.addWidget(setLabel, 0, 2)
        
        SecondGroupBox.setLayout(SecondGridLayout)
        SecondGridLayout.addWidget(chLabel, 0, 0)
        SecondGridLayout.addLayout(controllerLayout, 1, 0)
        SecondGridLayout.addWidget(modeLabel, 2, 0)
        SecondGridLayout.addWidget(modeComboBox, 3, 0)
        
        def _interfaceParameters():
            SecondGridLayout.removeWidget(self.SubSecondGroupBox)
            self.SubSecondGroupBox.deleteLater()
            self.SubSecondGroupBox = None
            interface = self.main.get_interface()
            self.BusParametersGroupBox(ChildWindow=ChildWindow , interface=interface)
            SecondGridLayout.addWidget(self.SubSecondGroupBox, 4, 0)        

        SecondGridLayout.addLayout(HGridLayout, 5, 0)
        interfaceComboBox.activated[str].connect(_interfaceParameters)
        # Define Third Group
        ThirdGroupBox = QGroupBox("Bus Status")
        ThirdGridLayout = QGridLayout()
        
        go_button = QPushButton("Go On Bus")
        go_button.setIcon(QIcon('graphics_Utils/icons/icon_reset.png'))
        go_button.clicked.connect(ChildWindow.close)
        
        ThirdGridLayout.addWidget(go_button, 0, 0)
        ThirdGroupBox.setLayout(ThirdGridLayout)
        MainLayout.addWidget(FirstGroupBox, 0, 0)
        MainLayout.addWidget(SecondGroupBox, 1, 0)
        MainLayout.addWidget(ThirdGroupBox, 2, 0)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)        

    def BusParametersGroupBox(self, ChildWindow=None, interface="Others"):
        # Define subGroup
        self.SubSecondGroupBox = QGroupBox("Bus Parameters")
        SubSecondGridLayout = QGridLayout()
        firstLabel = QLabel("firstLabel", ChildWindow)
        secondLabel = QLabel("secondLabel", ChildWindow)
        thirdLabel = QLabel("thirdLabel", ChildWindow)
        firstComboBox = QComboBox(ChildWindow)
        if (interface == "Kvaser"):
            firstLabel.setText("Bus Speed:")
            firstItems = ["1000 kbit/s, 75.0%", "500 kbit/s, 75.0%", "250 kbit/s, 75.0%", " 125 kbit/s, 75.0%", "100 kbit/s, 75.0%", "83.333 kbit/s, 75.0%", "62.500 kbit/s, 75.0%", "50 kbit/s, 75.0%", "33.333 kbit/s, 75.0%" ]
            for item in firstItems: firstComboBox.addItem(item)
            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            secondItems = ["1", "2", "3", "4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = self.server.get_bitrate_items()
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.main.set_bitrate)
            SubSecondGridLayout.addWidget(firstComboBox, 0, 1)
            
        if (interface == "AnaGate"):
            firstLabel.setText("IP address")
            ipAddress = self.server.get_ipAddress()
            self.firsttextbox = QLineEdit(ipAddress, ChildWindow)
            #self.firsttextbox.textChanged.connect(self.main.set_ipAddress)
            secondLabel.setText("SJW:")
            secondItems = ["1", "2", "3", "4"]
            secondComboBox = QComboBox(ChildWindow)
            for item in secondItems: secondComboBox.addItem(item)
            #secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            thirdItems = self.server.get_bitrate_items()
            thirdComboBox = QComboBox(ChildWindow)
            for item in thirdItems: thirdComboBox.addItem(item)
            thirdComboBox.activated[str].connect(self.main.set_bitrate)
            SubSecondGridLayout.addWidget(self.firsttextbox, 0, 1)
            
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
            thirdComboBox.activated[str].connect(self.main.set_bitrate)
            for item in thirdItems: thirdComboBox.addItem(item)
            SubSecondGridLayout.addWidget(firstComboBox, 0, 1)
        else:
            pass   
        SubSecondGridLayout.addWidget(firstLabel, 0, 0)
        SubSecondGridLayout.addWidget(secondLabel, 1, 0)
        SubSecondGridLayout.addWidget(secondComboBox, 1, 1)
        SubSecondGridLayout.addWidget(thirdLabel, 2, 0)
        SubSecondGridLayout.addWidget(thirdComboBox, 2, 1)
        self.SubSecondGroupBox.setLayout(SubSecondGridLayout)
               
    def canMessageChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("canMessageChildWindow")
        ChildWindow.setWindowTitle("CAN Message")
        ChildWindow.resize(310, 600)  # w*h
        # Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        MainLayout = QGridLayout()
        
        FirstGroupBox = QGroupBox("")
        # comboBox and label for channel
        FirstGridLayout = QGridLayout() 
        cobidLabel = QLabel("CAN Identifier", ChildWindow)
        cobidLabel.setText("CAN Identifier:")
        cobidtextbox = QLineEdit(self.__cobid, ChildWindow)
        cobidtextboxValue = cobidtextbox.text()
        self.main.set_cobid(cobidtextboxValue)
          
        
        #self.main.set_bytes(textboxValue[i])
        channelLabel = QLabel("Channel        :", ChildWindow)
        channelLabel.setText("Channel         :")
        canitems = ["CAN1"]
        canComboBox = QComboBox(ChildWindow)
        for item in canitems: canComboBox.addItem(item)
        canComboBox.activated[str].connect(self.clicked)
        dlcLabel = QLabel("DLC            :", ChildWindow)
        dlcLabel.setText("DLC            :")
        dlctextbox = QLineEdit(self.__dlc, ChildWindow)
        dlctextboxValue = dlctextbox.text()
        self.main.set_dlc(dlctextboxValue)
        
        
        FirstGridLayout.addWidget(cobidLabel, 0, 0)
        FirstGridLayout.addWidget(cobidtextbox, 0, 1)
                
        FirstGridLayout.addWidget(channelLabel, 1, 0)
        FirstGridLayout.addWidget(canComboBox, 1, 1)        
        
        FirstGridLayout.addWidget(dlcLabel, 2, 0)
        FirstGridLayout.addWidget(dlctextbox, 2, 1)  
             
        FirstGroupBox.setLayout(FirstGridLayout) 
        
        SecondGroupBox = QGroupBox("Message Data")
        # comboBox and label for channel
        SecondGridLayout = QGridLayout()
        ByteList = ["Byte0 :", "Byte1 :", "Byte2 :", "Byte3 :", "Byte4 :", "Byte5 :", "Byte6 :", "Byte7 :"] 
        LabelByte = [ByteList[i] for i in np.arange(len(ByteList))]
        textbox = [ByteList[i] for i in np.arange(len(ByteList))]
        textboxValue = [ByteList[i] for i in np.arange(len(ByteList))]
        for i in np.arange(len(ByteList)):
            LabelByte[i] = QLabel(ByteList[i], ChildWindow)
            LabelByte[i].setText(ByteList[i])
            textbox[i] = QLineEdit(self.__Bytes[i], ChildWindow)
            textboxValue[i] = textbox[i].text()
            if i <= 3:
                SecondGridLayout.addWidget(LabelByte[i], i, 0)
                SecondGridLayout.addWidget(textbox[i], i, 1)
            else:
                SecondGridLayout.addWidget(LabelByte[i], i - 4, 4)
                SecondGridLayout.addWidget(textbox[i], i - 4, 5)
        self.main.set_bytes(textboxValue)
        SecondGroupBox.setLayout(SecondGridLayout) 
        
        HBox = QHBoxLayout()
        send_button = QPushButton("Send")
        send_button.setIcon(QIcon('graphics_Utils/icons/icon_true.png'))
        send_button.clicked.connect(self.main.send_can)
        
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_Utils/icons/icon_close.jpg'))
        close_button.clicked.connect(ChildWindow.close)

        HBox.addWidget(send_button)
        HBox.addWidget(close_button)
                 
        MainLayout.addWidget(FirstGroupBox , 0, 0)
        MainLayout.addWidget(SecondGroupBox , 1, 0)
        MainLayout.addLayout(HBox , 2, 0)
        
        ChildWindow.setCentralWidget(plotframe)
        plotframe.setLayout(MainLayout) 
        self._createStatusBar(ChildWindow)
        QtCore.QMetaObject.connectSlotsByName(ChildWindow)
    
    def outputChildWindow(self, ChildWindow, comunication_object="Normal"):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(600, 600)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        logTextBox = logWindow.QTextEditLogger(ChildWindow, comunication_object=comunication_object)
        logLayout = QVBoxLayout()
        logLayout.addWidget(logTextBox.text_edit_widget)
        self.WindowGroupBox.setLayout(logLayout)
        logframe.setLayout(logLayout) 
        
    def trendChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(500, 500)  # w*h
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
        
 

    def restoreInterfaceSettings(self):
        self.__interface = self.server.get_interface() 
        self.server.set_interface(self.__interface)
        
    def applyLineEditChanges(self):
        self.main.set_ipAddress(self.firsttextbox.text())
               
    def _createStatusBar(self, childwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        childwindow.setStatusBar(status)
 
        
    def clicked(self, q):
        print("is clicked")
        
    # setter method
    def set_clicked(self, x):
        print(x)

    # Get functions    
    def get_corresponding_description_item(self, i):
        return notes_items[i]

        
if __name__ == "__main__":
    pass

