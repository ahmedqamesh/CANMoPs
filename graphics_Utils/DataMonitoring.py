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
class DataMonitoringCanvas(FigureCanvas):
    '''
    This is the FigureCanvas in which the live plot is drawn.

    '''
    def __init__(self, x_len:int, y_range:List, interval:int) -> None:
        '''
        :param x_len:       The nr of data points shown in one plot.
        :param y_range:     Range on y-axis.
        :param interval:    Get a new datapoint every .. milliseconds.

        '''
        super().__init__(mpl.figure.Figure())
        # Range settings
        self._x_len_ = x_len
        self._y_range_ = y_range

        # Store two lists _x_ and _y_
        self._x_ = list(range(0, x_len))
        self._y_ = [0] * x_len

        # Store a figure ax
        self._ax_ = self.figure.subplots()
        self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1]) # added
        self._line_, = self._ax_.plot(self._x_, self._y_)                  # added
        self.draw()                                                        # added

        # Initiate the timer
        self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
        self._timer_.start()
        return

    def _update_canvas_(self) -> None:
        '''
        This function gets called regularly by the timer.

        '''
        self._y_.append(round(get_next_datapoint(), 2))     # Add new datapoint
        self._y_ = self._y_[-self._x_len_:]                 # Truncate list y

        # New code
        # ---------
        self._line_.set_ydata(self._y_)
        self._ax_.draw_artist(self._ax_.patch)
        self._ax_.draw_artist(self._line_)
        self.update()
        self.flush_events()
        return

# Data source
# ------------
n = np.linspace(0, 499, 500)
d = 50 + 25 * (np.sin(n / 8.3)) + 10 * (np.sin(n / 7.5)) - 5 * (np.sin(n / 1.5))
i = 0
def get_next_datapoint():
    global i
    i += 1
    if i > 499:
        i = 0
    return d[i]        


class LiveMonitoringData(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(LiveMonitoringData, self).__init__(*args, **kwargs)
        
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points
        self.plot_style()
        # ... init timer ...
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
    
    def plot_style(self):
        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        
        #Add Background colour to white
        self.graphWidget.setBackground('w')
        #Add Title
        #self.graphWidget.setTitle("Running channels", color='blue', size=30)
        #Add Axis Labels
        self.graphWidget.setLabel('left', 'Data', color='black', size=30)
        self.graphWidget.setLabel('bottom', 'Time (ms)', color='black', size=30)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        #self.graphWidget.setXRange(0, 10, padding=0)
        #self.graphWidget.setYRange(20, 55, padding=0)
        
    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first 
        self.y.append( randint(0,100))  # Add a new random value.

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
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure(z=self.z, x=self.x)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initiate_timer(period=self.period)
           
    def initiate_timer(self,period=None):    
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(period)
        
    def compute_initial_figure(self,z=None, x=None, directory= None):
        cmap = plt.cm.get_cmap('tab20c')
        beamspot = np.zeros(shape=(z, x), dtype=np.float64)
        analysis_utils.save_to_h5(data=beamspot, outname='beamspot_Live.h5', directory=self.directory)
        im = self.axes.imshow(beamspot, aspect='auto', origin='upper', cmap=cmap)  
        self.plot_style(im=im , cmap=cmap, z=self.z, x=self.x)
    
    def update_figure(self): 
        try:    
            beamspot = analysis_utils.open_h5_file(outname='beamspot_Live.h5', directory=self.directory)
            cmap = plt.cm.get_cmap('tab20c')
            im = self.axes.imshow(beamspot, aspect='auto', origin='upper', cmap=cmap)
            self.draw()
        except IndexError:  #open file failure
                pass
        
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
        

if __name__ == '__main__':
    pass
