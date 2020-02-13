from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from graphics_Utils import mainWindow, dataMonitoring , menuWindow ,logWindow
import numpy as np
ipAddress = '192.168.1.254'  
class ChildWindow(QWidget):  
    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent) 
       self.menu= menuWindow.MenuBar()
       self.mainWindow = mainWindow.MainWindow()
       self._chComboBoxInterface = "Kvaser"
       self_ipAddress =ipAddress
       #self.menu._createStatusBar()
       
    def canMessageChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("canMessageChildWindow")
        ChildWindow.setWindowTitle("CAN Message")
        ChildWindow.resize(310, 600) #w*h
        MainLayout = QGridLayout()
        
        #Define a frame for that group
        plotframe = QFrame(ChildWindow)
        plotframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(plotframe)
        mainLayout = QGridLayout()
                
        #comboBox and label for channel
        firstHBoxLayout = QHBoxLayout(ChildWindow)
        firstLabel = QLabel("CAN Identifier", ChildWindow)
        firstLabel.setText("CAN Identifier:")
        firsttextbox = QLineEdit(ChildWindow)
        firsttextboxValue = firsttextbox.text()
        firstHBoxLayout.addWidget(firstLabel)
        firstHBoxLayout.addWidget(firsttextbox)

        secondHBoxLayout = QHBoxLayout(ChildWindow)
        seondLabel = QLabel("Channel:", ChildWindow)
        seondLabel.setText("Channel:")
        seonditems = ["CAN1"]
        seondComboBox = QComboBox(ChildWindow)
        for item in seonditems: seondComboBox.addItem(item)
        seondComboBox.activated[str].connect(self.clicked)
        secondHBoxLayout.addWidget(seondLabel)
        secondHBoxLayout.addWidget(seondComboBox)
 
        thirdHBoxLayout = QHBoxLayout(ChildWindow)
        thirdLabel = QLabel("CAN Identifier", ChildWindow)
        thirdLabel.setText("CAN Identifier:")
        thirdtextbox = QLineEdit(ChildWindow)
        thirdtextboxValue = thirdtextbox.text()
        thirdHBoxLayout.addWidget(thirdLabel)
        thirdHBoxLayout.addWidget(thirdtextbox)


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
        gridLayout.addLayout(firstHBoxLayout,0,0)
        gridLayout.addLayout(secondHBoxLayout,1,0)
        
        gridLayout.addLayout(thirdHBoxLayout,2,0)
        gridLayout.addWidget(dimComboBox,3,0)
        
        
        gridLayout.addWidget(self.outLabel,4,0)
        gridLayout.addWidget(set_button,4,1)    

        mainLayout.addLayout(gridLayout,0, 0)

        plotframe.setLayout(mainLayout) 

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
        controllerLayout = QHBoxLayout()
        interfaceitems = ["----","Kvaser","AnaGate","Others"]
        interfaceComboBox = QComboBox(ChildWindow)
        for item in interfaceitems: interfaceComboBox.addItem(item)
        interfaceComboBox.activated[str].connect(self.set_chComboBoxInterface)
        
        controllerLayout.addWidget(interfaceComboBox)
        
        #Another group will be here for Bus parameters
        self.BusParametersGroupBox(interface =self._chComboBoxInterface)
        
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
        set_button.clicked.connect(self.clicked)
        
        h , w = 50 , 25
        connectButton = QPushButton("")
        connectButton.clicked.connect(self.get_chComboBoxInterface)  
        connectButton.setFixedWidth(w)
        connectButton.setIcon(QIcon('graphics_Utils/icons/icon_disconnect.jpg'))
        icon = QIcon()
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_disconnect.jpg'),  QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('graphics_Utils/icons/icon_connect.jpg'), QIcon.Normal,  QIcon.On)
        connectButton.setIcon(icon)
        connectButton.setCheckable(True)
        
        
        setLabel = QLabel("Set same bit rate in all CAN controllers", ChildWindow)
        setLabel.setText("Set same bit rate in all CAN controllers")
        
        HGridLayout.addWidget(set_button,0,0)
        HGridLayout.addWidget(connectButton,0,1) 
        HGridLayout.addWidget(setLabel,0,2)
        
        self.SecondGroupBox.setLayout(SecondGridLayout)
        SecondGridLayout.addWidget(chLabel,0,0)
        SecondGridLayout.addLayout(controllerLayout,1,0)
        SecondGridLayout.addWidget(modeLabel,2,0)
        SecondGridLayout.addWidget(modeComboBox,3,0)
        
        def _interfaceParameters():
            interface = self._chComboBoxInterface
            
            SecondGridLayout.removeWidget(self.SubSecondGroupBox)
            self.SubSecondGroupBox.deleteLater()
            self.SubSecondGroupBox = None              
            self.BusParametersGroupBox(interface = interface)
            SecondGridLayout.addWidget(self.SubSecondGroupBox,4,0)        
        SecondGridLayout.addLayout(HGridLayout,5,0)
        interfaceComboBox.activated[str].connect(_interfaceParameters)
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
        

    def BusParametersGroupBox(self, interface ="AnaGate"):
        #Define subGroup
        self.SubSecondGroupBox= QGroupBox("Bus Parameters")
        SubSecondGridLayout =  QGridLayout()
        firstLabel= QLabel("firstLabel", self)
        secondLabel = QLabel("secondLabel", self)
        thirdLabel = QLabel("thirdLabel", self)
        firstComboBox = QComboBox(self)
        if (interface == "Kvaser"):
            firstLabel.setText("Bus Speed:")
            firstItems = ["1000 kbit/s, 75.0%","500 kbit/s, 75.0%","250 kbit/s, 75.0%"," 125 kbit/s, 75.0%","100 kbit/s, 75.0%","83.333 kbit/s, 75.0%","62.500 kbit/s, 75.0%","50 kbit/s, 75.0%","33.333 kbit/s, 75.0%" ]
            for item in firstItems: firstComboBox.addItem(item)
            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            secondItems = ["1","2","3","4"]
            secondComboBox = QComboBox(self)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            SubSecondGridLayout.addWidget(firstComboBox,0,1)
        if (interface == "AnaGate"):
            firstLabel.setText("IP address")
            self.firsttextbox = QLineEdit(ipAddress,self)
            textboxValue = self.firsttextbox.text()
            secondLabel.setText("SJW:")
            secondItems = ["1","2","3","4"]
            secondComboBox = QComboBox(self)
            for item in secondItems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            SubSecondGridLayout.addWidget(firsttextbox,0,1)
            
        if (interface == "Others"):        
            firstLabel.setText("Speed:")
            firstItems = [""]
            firstComboBox = QComboBox(self)
            for item in firstItems: firstComboBox.addItem(item)
            firstComboBox.activated[str].connect(self.clicked)
            secondLabel.setText("SJW:")
            seconditems = [""]
            secondComboBox = QComboBox(self)
            for item in seconditems: secondComboBox.addItem(item)
            secondComboBox.activated[str].connect(self.clicked)
            thirdLabel.setText("Bit Timing:")
            SubSecondGridLayout.addWidget(firstComboBox,0,1)
            
        SubSecondGridLayout.addWidget(firstLabel,0,0)
        SubSecondGridLayout.addWidget(secondLabel,1,0)
        SubSecondGridLayout.addWidget(secondComboBox,1,1)
        SubSecondGridLayout.addWidget(thirdLabel,2,0)
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
    
            
    def set_click(self):
        dim = self.get_dimention()
        ch = self.get_channel()
        text = "%s will be set to  %s direction"%(ch,dim)
        print(text)
 

                
    def set_chComboBoxInterface(self, x): 
        
        self._chComboBoxInterface = x 
    
    def set_self_ipAddress(self,x):
        # x = self.firsttextbox.text()
        self.self_ipAddress =x
        
        
    def set_dimention(self, x): 
        self._dim = x
        dim = self.get_dimention()
        ch = self.get_channel()
        text = "%s will be set to  %s direction"%(ch,dim)
        self.outLabel.setText(text)
        self.outLabel.adjustSize()
        
    # getter methods
    def get_chComboBoxInterface(self): 
        #Set the Interface in the main menu
        self.mainWindow.set_interface(self._chComboBoxInterface)
        return self._chComboBoxInterface 
    
    def get_self_ipAddress(self):
        return self_ipAddress
    
    def get_dimention(self): 
        return self._dim

if __name__ == "__main__":
    pass

