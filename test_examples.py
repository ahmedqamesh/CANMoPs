from PyQt5 import QtWidgets, QtCore, QtGui
import string

grid = [[["text", "GREEN"], 0, ["text", "RED"], 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]]

BTN = """QPushButton{{font-weight: bold; color: {};
        font-size: 14px; background-color: {}; 
        border-width: 2px; border-radius: 100px}}"""


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.letter_count = dict(zip(string.ascii_uppercase, [x for x in range(26)]))

        self.initUI()
        self.buttons = []
        self.createLayout()
        self.center_widget()

    def initUI(self):
        p = self.palette()
        gradient = QtGui.QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QtGui.QColor('#f1f1f1'))
        gradient.setColorAt(1.0, QtGui.QColor('#00a1de'))
        p.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
        self.setPalette(p)

    def createLayout(self):
        hlay = QtWidgets.QHBoxLayout(self)
        frameL = QtWidgets.QFrame()

        vlay = QtWidgets.QVBoxLayout(frameL)
        frame = QtWidgets.QFrame()
        frame.setObjectName("principal")
        frame.setStyleSheet("#principal{border: 2px solid white;}")
        hlay.addWidget(frameL)
        hlay.addWidget(frame)

        self.gridLayout = QtWidgets.QGridLayout(frame)

        h = 60  # height

        for i, row in enumerate(grid):
            letter = "{}".format(string.ascii_uppercase[i])
            frameButton = QtWidgets.QFrame()
            frameButton.setFixedHeight(h)
            frameButton.setContentsMargins(0, 0, 0, 0)
            lay = QtWidgets.QVBoxLayout(frameButton)
            button = QtWidgets.QPushButton(letter)
            button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            button.clicked.connect(lambda x, letter=letter: self.populate_row(letter)) # Every button click returns 'J'
            lay.addWidget(button)
            vlay.addWidget(frameButton)
            self.buttons.append([])
            for j, val in enumerate(row):
                gridButton = QtWidgets.QPushButton()
                gridButton.setFixedSize(h, h)
                self.buttons[i].append(gridButton)
                self.gridLayout.addWidget(gridButton, i, j)
        for ix in range(j + 1):
            label = QtWidgets.QLabel("{}".format(ix + 1))
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayout.addWidget(label, i + 1, ix)
        vlay.addWidget(QtWidgets.QLabel())
        self.update_data()


    def update_data(self):
        for i, row in enumerate(grid):
            for j, val in enumerate(row):
                btn = self.buttons[i][j]
                if isinstance(val, list):
                    btn.setText(val[0])
                    if val[1] == "GREEN":
                        btn.setStyleSheet(BTN.format('white', 'green'))
                    elif val[1] == "RED":
                        btn.setStyleSheet(BTN.format('white', 'red'))
                else:
                    btn.setStyleSheet(BTN.format('black', 'white'))
                    btn.setText("{}".format(val))


    def center_widget(self):
        self.window().setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.window().size(),
                QtWidgets.QApplication.desktop().availableGeometry())
        )

    def populate_row(self, letter):
        dialog = QtWidgets.QDialog()
        dialog.resize(660, 360)
        textBox = QtWidgets.QPlainTextEdit(dialog)
        Rbtn = QtWidgets.QPushButton('Add To Row')
        Rbtn.clicked.connect(lambda: self.input_to_grid(textBox.toPlainText(), letter))       

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(textBox)
        layout.addWidget(Rbtn)
        dialog.exec_()

    def input_to_grid(self, text, letter):
        print(text, letter)
        lst = text.split(' ')
        for i, x in enumerate(lst):
            self.add_to_grid((letter, i + 1), x)
            print((letter, i + 1), x)
        self.print_grid()
        self.update_data()

    def add_to_grid(self, loc, item):
        x, y = self.translate(loc)
        grid[x][y] = item

    def translate(self, loc):
        for k, v in self.letter_count.items():
            if loc[0].upper() == k:
                x = v
        y = int(loc[1]) - 1
        return x, y

    def print_grid(self):
        """ Print the grid prettier than normal.. """
        print('\n'.join(['\t'.join([str(c) for c in r]) for r in grid]))


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())