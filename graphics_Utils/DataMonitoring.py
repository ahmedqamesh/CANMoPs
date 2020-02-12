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
from pyqtgraph import PlotWidget, plot
import time
from IPython import display
import matplotlib as mpl
from matplotlib.figure import Figure
from analysis import analysis_utils

class LiveMonitoringData(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(LiveMonitoringData, self).__init__(parent)
        self.scan = analysis_utils.BeamSpotScan()
        self.compute_initial_figure()
        self.plot_style()
        self.initiate_timer()
    
    def compute_initial_figure(self):                   
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points
        

    def plot_style(self):
        self.graphWidget.setBackground('w')
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pg.mkPen(color=(255, 0, 0)))

        #Add Title
        #self.graphWidget.setTitle("Running channels", color='blue', size=30)
        #Add Axis Labels
        self.graphWidget.setLabel('left', 'data', color='red', size=30)
        self.graphWidget.setLabel('bottom', 'Time [s]', color='red', size=30)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        #self.graphWidget.setXRange(0, 10, padding=0)
        #self.graphWidget.setYRange(20, 55, padding=0)
    
    def initiate_timer(self,period=50):    
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(period)
             
    def update_figure(self):
        #self.data = self.scan.get_data()
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append(randint(0,100))  # Add a new random value.
        self.data_line.setData(self.x, self.y)  # Update the data.

    
class MapMonitoringDynamicCanvas(FigureCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, parent=None, width=5, height=4, dpi=100 ,period=None, depth = None, z=None, x=None, z_Delay= None, x_Delay=None,size_x =None, size_z = None, directory=None):
        self.directory = directory
        self.size_x=size_x
        self.z=z
        self.x_Delay=x_Delay
        self. z_Delay = z_Delay
        self.x=x
        self.size_z=size_z
        self.depth = depth
        self.period = period
        im , cmap = self.compute_initial_figure(height = height,width=width,dpi=dpi, z=self.z, x=self.x)
        self.plot_style(im=im , cmap=cmap, z=self.z, x=self.x)
        self.initiate_timer(period=self.period)

    def compute_initial_figure(self,height = None,width=None,dpi=None, z=None, x=None, directory= None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding),FigureCanvas.updateGeometry(self)
        
        cmap = plt.cm.get_cmap('tab20c')
        beamspot = np.zeros(shape=(z, x), dtype=np.float64)
        analysis_utils.save_to_h5(data=beamspot, outname='beamspot_Live.h5', directory=self.directory)
        im = self.axes.imshow(beamspot, aspect='auto', origin='upper', cmap=cmap)  
        return im , cmap
       
                   
    def plot_style(self, z=None, x=None, depth=None, im=None, cmap=plt.cm.get_cmap('viridis', 5)):
        mid_z = z / 2
        mid_x = x / 2
        r = 3
        self.axes.set_title("Beam profile", fontsize=12, y=1.7, x=-0.6)
        #self.axes.set_xlabel('x [mm]')
        #self.axes.set_ylabel('z[mm]')
        circle = plt.Circle((mid_z, mid_x), r, color='red', fill=False)
        self.axes.add_artist(circle)
        self.axes.axhline(y=mid_z, linewidth=0.6, color='#d62728', linestyle='dashed')
        self.axes.axvline(x=mid_x, linewidth=0.6, color='#d62728', linestyle='dashed')
               
    def initiate_timer(self,period=None):    
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(period)
        
    def update_figure(self): 
        try:    
            beamspot = analysis_utils.open_h5_file(outname='beamspot_Live.h5', directory=self.directory)
            cmap = plt.cm.get_cmap('tab20c')
            im = self.axes.imshow(beamspot, aspect='auto', origin='upper', cmap=cmap)
            self.draw()
        except IndexError:  #open file failure
                pass
    

        


if __name__ == '__main__':
    pass
