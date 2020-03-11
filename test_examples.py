import sys
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel, QApplication

class Screen(QWidget):
    def __init__(self):
        super(Screen, self).__init__()
        layout = QHBoxLayout(self)
        self.screen_layout = layout
        self.all_running()
        layout.addWidget(self.running_full_widget)
        self.actions_full_widget = None
        self.actions('1')
        # layout.addWidget(self.actions_full_widget)
        self.setLayout(layout)
        self.show()
    def all_running(self):
        self.running_full_widget = QWidget()
        runnning_full_layout= QVBoxLayout()
        button1 = QPushButton("btn1")
        button2 = QPushButton("btn2")
        button1.clicked.connect(lambda: self.actions('2'))
        button2.clicked.connect(lambda: self.actions('3'))
        runnning_full_layout.addWidget(button1)
        runnning_full_layout.addWidget(button2)
        self.running_full_widget.setLayout(runnning_full_layout)
    
    def actions(self,value):
        # Remove any previously added widget
        if self.actions_full_widget is not None:
            self.screen_layout.removeWidget(self.actions_full_widget)
            self.actions_full_widget.deleteLater()
        self.actions_full_widget= QWidget()
        val = int(value)
        print(val)
        actions_layout = QVBoxLayout()
        for i in range(val):
           actions_item = QLabel(str(i))
           actions_layout.addWidget(actions_item)
        self.actions_full_widget.setLayout(actions_layout)
        self.screen_layout.addWidget(self.actions_full_widget)

app = QApplication(sys.argv)
Gui = Screen()
sys.exit(app.exec_())