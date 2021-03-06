from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.animation as animation
from typing import *
from PyQt5 import *
from PyQt5 import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from random import randint
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph import *
import time
import matplotlib as mpl
from analysis import analysis_utils
from graphics_utils import mainWindow


class CollapsibleBox(QtWidgets.QWidget):

    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

       

        self.content_area = QtWidgets.QScrollArea(maximumHeight=0, minimumHeight=0, maximumWidth = 500, minimumWidth =0)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        lay = QtWidgets.QHBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)
        
        self.toggle_animation = QtCore.QParallelAnimationGroup(self)
#         self.toggle_animation.addAnimation(
#             QtCore.QPropertyAnimation(self, b"minimumHeight")
#         )
#         self.toggle_animation.addAnimation(
#             QtCore.QPropertyAnimation(self, b"maximumHeight")
#         )

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(QtCore.Qt.LeftArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (self.sizeHint().height() - self.content_area.maximumHeight())
        collapsed_width = (self.sizeHint().width() - 0) #self.content_area.maximumWidth())
        
        content_height = layout.sizeHint().height()
        content_width = layout.sizeHint().width()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)
            
            #animation.setStartValue(collapsed_width)
            #animation.setEndValue(collapsed_width + content_width)
                        
            #animation.setStartValue(QSize(100, 0))
            #animation.setEndValue(QSize(100, content_height))
        
        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        #content_animation.setStartValue(0)
        #content_animation.setEndValue(content_height)
        #content_animation.setStartValue(QSize(100, 0))
        #content_animation.setEndValue(QSize(100, content_height))
    
        

class ADCMonitoringData(QMainWindow):

    def __init__(self, parent=None, interface=None):
        super(ADCMonitoringData, self).__init__(parent)
        self.main = mainWindow.MainWindow()        
        self.n_channels = np.arange(3, 35)
        self.setObjectName("ADCChannels")
        self.setWindowTitle("ADC Channels")
        self.resize(350, 600)  # w*h
        MainLayout = QGridLayout()
        # Define a frame for that group
        plotframe = QFrame(self)
        plotframe.setLineWidth(0.6)
        self.setCentralWidget(plotframe)
        SecondGroupBox = QGroupBox("ADC channels")      
        SecondGridLayout = QGridLayout()
        LabelChannel = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.ChannelBox = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.trendingButton = [self.n_channels[i] for i in np.arange(len(self.n_channels))]
        self.adc_channels_reg = self.main.get_adc_channels_reg()
        dictionary = self.main.get_dictionary_items()
        self.adc_index = self.main.get_adc_index()
        self.subIndexItems = list(analysis_utils.get_subindex_yaml(dictionary=dictionary, index=self.adc_index))   
        for i in np.arange(len(self.n_channels)):
            LabelChannel[i] = QLabel("Channel", self)
            LabelChannel[i].setText("Ch" + str(self.n_channels[i]) + ":")
            self.ChannelBox[i] = QLineEdit("", self)
            self.ChannelBox[i].setStyleSheet("background-color: white; border: 1px inset black;")
            self.ChannelBox[i].setReadOnly(True)
            LabelChannel[i].setStatusTip('ADC channel %s [index = %s & subIndex = %s]' % (str(self.n_channels[i]), self.adc_index, self.subIndexItems[i + 1]))  # show when move mouse to the icon
            self.icon = QLabel(self)
            if self.adc_channels_reg[str(i + 3)] == "V":       
                icon_dir = 'graphics_utils/icons/icon_voltage.png'
            else:
                icon_dir = 'graphics_utils/icons/icon_thermometer.png'
            pixmap = QPixmap(icon_dir)
            self.icon.setPixmap(pixmap.scaled(20, 20))
            self.trendingButton[i] = QPushButton("")
            self.trendingButton[i].setIcon(QIcon('graphics_utils/icons/icon_trend.jpg'))
            self.trendingButton[i].setStatusTip('Data Trending') 
            self.trendingButton[i].clicked.connect(self.trendWindow)
            
            if i < 16:
                SecondGridLayout.addWidget(self.icon, i, 0)
                # SecondGridLayout.addWidget(self.trendingButton[i], i, 1)
                SecondGridLayout.addWidget(LabelChannel[i], i, 2)
                SecondGridLayout.addWidget(self.ChannelBox[i], i, 3)
            else:
                SecondGridLayout.addWidget(self.icon, i - 16, 4)
                # SecondGridLayout.addWidget(self.trendingButton[i], i-16, 5)
                SecondGridLayout.addWidget(LabelChannel[i], i - 16, 6)
                SecondGridLayout.addWidget(self.ChannelBox[i], i - 16 , 7)
        SecondGroupBox.setLayout(SecondGridLayout) 
        
        HBox = QHBoxLayout()
        send_button = QPushButton("run")
        send_button.setIcon(QIcon('graphics_utils/icons/icon_start.png'))
        send_button.clicked.connect(self.initiate_timer)

        stop_button = QPushButton("stop")
        stop_button.setIcon(QIcon('graphics_utils/icons/icon_stop.png'))
        stop_button.clicked.connect(self.stop_timer)
                
        close_button = QPushButton("close")
        close_button.setIcon(QIcon('graphics_utils/icons/icon_close.jpg'))
        close_button.clicked.connect(self.close)

        HBox.addWidget(send_button)
        HBox.addWidget(stop_button)
        HBox.addWidget(close_button)
        MainLayout.addWidget(SecondGroupBox , 1, 0)
        MainLayout.addLayout(HBox , 2, 0)
        self._createStatusBar(self)
        plotframe.setLayout(MainLayout) 
        QtCore.QMetaObject.connectSlotsByName(self)
        # self.update_adc_channels()
        self.show()
        
    def initiate_timer(self, period=10000):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_adc_channels)
        self.timer.start(period)
    
    def stop_timer(self):
        self.timer.stop() 
                   
    def update_adc_channels(self):
        adc_updated = []
        for i in np.arange(len(self.n_channels)):
            self.main.set_index(self.adc_index)
            self.main.set_subIndex(self.subIndexItems[i + 1])
            self.main.send_sdo_can()
            data_point = self.main.get_data_point()
            adc_updated = np.append(adc_updated, data_point)
            adc_converted = self.adc_conversion(self.adc_channels_reg[str(i + 3)], adc_updated[i])
            if adc_converted is not None:
                self.ChannelBox[i].setText(str(round(adc_converted, 3)))
            else:
                self.ChannelBox[i].setText(str(adc_updated[i]))  

    def adc_conversion(self, adc_channels_reg="V", value=None):
        if value is not None:
            if adc_channels_reg == "V":
                value = value * 207 * 10e-6 * 40
            else:
                value = value * 207 * 10e-6
        return value
    
    def trendWindow(self):
        self.trend = QMainWindow()
        self.trendChildWindow(self.trend)
        self.trend.show()
    
    def _createStatusBar(self, childwindow):
        status = QStatusBar()
        status.showMessage("Ready")
        childwindow.setStatusBar(status)
            
    def trendChildWindow(self, childWindow):
        childWindow.setObjectName("TrendingWindow")
        childWindow.setWindowTitle("Trending Window")
        childWindow.resize(900, 500)  # w*h
        logframe = QFrame(self)
        logframe.setLineWidth(0.6)
        childWindow.setCentralWidget(logframe)
        trendLayout = QHBoxLayout()
        self.WindowGroupBox = QGroupBox("")
        self.Fig = LiveMonitoringData()
        self.Fig.setStyleSheet("background-color: black;"
                                        "color: black;"
                                        "border-width: 1.5px;"
                                        "border-color: black;"
                                        "margin:0.0px;"
                                        # "border: 1px "
                                        "solid black;")

        self.distribution = LiveMonitoringDistribution()
        trendLayout.addWidget(self.distribution)
        trendLayout.addWidget(self.Fig)
        
        self.WindowGroupBox.setLayout(trendLayout)
        logframe.setLayout(trendLayout) 

      
class LiveMonitoringData(QtWidgets.QMainWindow):
    
    def __init__(self, parent=None):
        super(LiveMonitoringData, self).__init__(parent)
        self.compute_initial_figure()
        self.initiate_timer(period=2000)
        self.plot_style()
        self.main = mainWindow.MainWindow()
        
    def compute_initial_figure(self):                   
        self.graphWidget = pg.PlotWidget(background="w")
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points
        
    def plot_style(self):
        # self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0)))
        # Add Title
        self.graphWidget.setTitle("Online data monitoring")
        # Add Axis Labels
        self.graphWidget.setLabel('left', "<span style=\"color:black; font-size:15px\">CAN Data</span>")
        self.graphWidget.setLabel('bottom', "<span style=\"color:black; font-size:15px\">Time [s]</span>")

        # Add legend
        # self.graphWidget.addLegend()
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.getAxis("bottom").setStyle(tickTextOffset=10)
        # Set Range
        # self.graphWidget.setXRange(0, 100, padding=0)
        # self.graphWidget.setYRange(00, 55, padding=0)
        return self.graphWidget
    
    def initiate_timer(self, period=None):    
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(period)
    
    def stop_timer(self):
        self.timer.stop()      
    
    def update_figure(self):
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0)))
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        self.main.send_sdo_data()  # to be replaced with send_sdo_can
        data = self.main.get_data_point()
        self.y = self.y[1:]  # Remove the first 
        self.y.append(data)  # Add a new random value.
        self.data_line.setData(self.x, self.y)  # Update the data.

 
class LiveMonitoringDistribution(FigureCanvas):
    
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, parent=None, period=200):
        self.compute_initial_figure()
        self.main = mainWindow.MainWindow()
        # self.initiate_timer(period=period)
        
    def compute_initial_figure(self):
        fig = Figure(edgecolor="black", linewidth="2.5")  # , facecolor="#e1ddbf")
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding), FigureCanvas.updateGeometry(self)
        self.data = list(range(100))  # 100 time points
        self.axes.set_xlabel(r'CAN Data', size=10)
        self.axes.set_ylabel(r'Counts', size=10) 
        self.axes.grid(True)
        plt.tight_layout()
    
    def initiate_timer(self, period=None):    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(period)
    
    def stop_timer(self):
        self.timer.stop() 
                
    def update_figure(self):
        self.main.send_sdo_data()  # to be replaced with send_sdo_can
        y = self.main.get_data_point()
        self.data.append(y)
        # print(len(self.data))
        hist_data, edges = np.histogram(self.data, bins=np.arange(0, 100, 1))  #
        x, y = edges[:-1], hist_data
        self.axes.fill_between(x, y, color='#F5A9BC', label="Data")
        self.draw()

        
if __name__ == '__main__':
    pass
