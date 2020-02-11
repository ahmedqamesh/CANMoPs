import sys
import yaml
from PyQt5.QtWidgets import QHBoxLayout, QAction, QApplication, QMainWindow

class menudemo(QMainWindow):
    def __init__(self, parent = None):
        super(menudemo, self).__init__(parent)

        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New")

        save = QAction("Save",self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)

        edit = file.addMenu("Edit")
        edit.addAction("copy")
        edit.addAction("paste")

        quit = QAction("Quit",self)
        file.addAction(quit)
        file.triggered[QAction].connect(self.processtrigger)
        self.setWindowTitle("menu demo")

    def processtrigger(self, q):
        print(q.text()+" is triggered")


def main():
#     app = QApplication(sys.argv)
#     ex = menudemo()
#     ex.show()
#     sys.exit(app.exec_())
    with open("MOPS_daq_cfg.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    for section in cfg:
        print(section)
    print(cfg['CAN_Interface'])
    print(cfg['CAN_Interface']['AnaGate']['ipAddress'])

    
    


if __name__ == '__main__':
    main()