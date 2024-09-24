from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtWidgets, QtGui, QtCore

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from controlgui import Ui_Widget as gui 

class ControlWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        