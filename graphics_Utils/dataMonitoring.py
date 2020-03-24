from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.animation as animation
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, Qt, QTimer, pyqtSlot
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from random import randint
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph import *
import time
from IPython import display
import matplotlib as mpl
from matplotlib.figure import Figure
from analysis import analysis_utils
from graphics_Utils import mainWindow

#plt.style.use('ggplot')
class LiveMonitoringData(QtWidgets.QMainWindow):
    
    def __init__(self, parent=None):
        super(LiveMonitoringData, self).__init__(parent)
        self.compute_initial_figure()
        self.plot_style()
        self.main = mainWindow.MainWindow()
        
    def compute_initial_figure(self):                   
        self.graphWidget = pg.PlotWidget(background ="w")
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points
        
    def plot_style(self):
        #self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0)))
        #Add Title
        self.graphWidget.setTitle("Online data monitoring")
        #Add Axis Labels
        self.graphWidget.setLabel( 'left', "<span style=\"color:black; font-size:15px\">CAN Data</span>")
        self.graphWidget.setLabel( 'bottom', "<span style=\"color:black; font-size:15px\">Time [s]</span>")

        #Add legend
        #self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.getAxis("bottom").setStyle(tickTextOffset = 10)
        #Set Range
        #self.graphWidget.setXRange(0, 100, padding=0)
        #self.graphWidget.setYRange(00, 55, padding=0)
        return self.graphWidget
    
    def initiate_timer(self,period=None):    
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(period)
    
    def stop_timer(self):
        self.timer.stop()      
    
    def update_figure(self):
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0)))
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
        self.main.send_sdo_data() # to be replaced with send_sdo_can
        data = self.main.get_data_point()
        self.y = self.y[1:]  # Remove the first 
        self.y.append(data)  # Add a new random value.
        self.data_line.setData(self.x, self.y)  # Update the data.
 
class LiveMonitoringDistribution(FigureCanvas):
    
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, parent=None,period=200):
        self.compute_initial_figure()
        self.main = mainWindow.MainWindow()
        #self.initiate_timer(period=period)
        
    def compute_initial_figure(self):
        fig = Figure(edgecolor = "black",linewidth ="2.5")#, facecolor="#e1ddbf")
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding),FigureCanvas.updateGeometry(self)
        self.data = list(range(100))  # 100 time points
        self.axes.set_xlabel(r'CAN Data', size = 10)
        self.axes.set_ylabel(r'Counts', size = 10)
        
        self.axes.grid(True)

        plt.tight_layout()
    
    def initiate_timer(self,period=None):    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(period)
    
    def stop_timer(self):
        self.timer.stop() 
                
    def update_figure(self):
        self.main.send_sdo_data() # to be replaced with send_sdo_can
        y = self.main.get_data_point()
        self.data.append(y)
        print(len(self.data))
        hist_data, edges = np.histogram(self.data, bins=np.arange(0, 100, 1))  #
        x, y = edges[:-1], hist_data
        self.axes.fill_between(x, y, color='#F5A9BC', label="Data")
        self.draw()
        
if __name__ == '__main__':
    pass
