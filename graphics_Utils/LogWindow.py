import sys
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, Qt, QTimer, pyqtSlot
import logging
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setStyleSheet("background-color: white;")
        policy = self.widget.sizePolicy()
        policy.setVerticalStretch(1)
        self.widget.setSizePolicy(policy)
    def emit(self, record):
        msg = self.format(record)
        text = "Please subscribe the channel and like the videos"
        #self.widget.appendPlainText(text)
        self.widget.appendPlainText(msg)
        

class LoggerDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None, period = 1000):
        super().__init__(parent)
        logTextBox = QTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)
        self.initiate_timer(period=period)

        logLayout = QtWidgets.QVBoxLayout()
        logLayout.addWidget(logTextBox.widget)
        self.setLayout(logLayout)

        self.show()
 
    def initiate_timer(self,period=None):    
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.test)
        timer.start(period)
           
    def test(self):
        logging.debug('damn, a bug')
        #logging.info('something to remember')
        #logging.warning('that\'s not right')
        #logging.error('foobar')

if __name__ == "__main__":
    pass


        