from history_widget_gui import Ui_Form as gui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtCore import pyqtSlot
import numpy as np 

import matplotlib.pyplot as plt
def get_color(n, colormax=3.0, cmap="viridis"):
    """
        Discretize a colormap. Great getting nice colors for a series of trends on a single plot! 
    """
    this_cmap = plt.get_cmap(cmap)
    return this_cmap(n/colormax)

class HistoryWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget, logger:QtWidgets.QTextBrowser):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        self._filepath = "/home/watermon/software/StageControl/StageControl/gui/data/data_history.csv"
        self.update_plots()

    @pyqtSlot()
    def update_plots(self):
        if self.ui.cbox.isChecked():
            return

        data = np.loadtxt(self._filepath, delimiter=',').T

        times = data[0]
        times = -(np.max(times) - times)/3600

        mask = times > -8

        p1 = data[1][mask]
        p2 = data[2][mask]
        p3 =  data[3][mask]
        p4 =  data[4][mask]
        temperature =  data[5][mask]
        times = times[mask]

        self.ui.figure.clear()
        self.axes = self.ui.figure.add_subplot(111)
        self.axes.plot(times, p1, label="Input P", color=get_color(1,5, "Reds"))
        self.axes.plot(times, p2, label="Pre-Filter", color=get_color(2,5, "Reds"))
        self.axes.plot(times, p3, label="Post-Filer", color=get_color(3,5, "Reds"))
        self.axes.plot(times, p4, label="Osmosis", color=get_color(4,5, "Reds"))
        self.axes.plot([], [], color='blue', label="Temperature")
        self.axes.legend()

        twax = self.axes.twinx()
        twax.plot(times,temperature, color='blue')
        twax.set_ylabel("Temp")
        self.ui.canvas.draw()



