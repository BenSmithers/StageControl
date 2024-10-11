from warn_gui import Ui_Dialog as gui 
from warn_gui import HelpDialog_gui
from PyQt5 import QtGui, QtCore, QtWidgets


class WarnWidget(QtWidgets.QDialog):
    def __init__(self, parent, message) -> None:
        super().__init__(parent)
        self.setWindowTitle("Water Alert!")
        self.ui = gui()
        
        self.ui.setupUi(self)
        self.ui.label_2.setText("{}".format(message))
        self.parent = parent

class HelpWidget(QtWidgets.QDialog):
    def __init__(self, parent, message) -> None:
        super().__init__(parent)
        self.setWindowTitle("Help!")
        self.ui = HelpDialog_gui()
        
        self.ui.setupUi(self)
        self.ui.label_2.setText("{}".format(message))
        self.parent = parent
