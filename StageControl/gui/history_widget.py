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
        
        self.ui.cbox.clicked.connect(self.update_plots)
        self._firstpt = True 
        self.update_plots()

    @pyqtSlot()
    def update_plots(self):
        if not (self._firstpt):
            oldx = self.axes[0].get_xlim()
            oldy = self.axes[0].get_ylim()
            oldy2 = self.twax.get_ylim()

        data = np.loadtxt(self._filepath, delimiter=',').T

        times = data[0]
        times = -(np.max(times) - times)/3600

        mask = times > - self.ui.n_hours.value()

        p1 = data[1][mask]
        p2 = data[2][mask]
        p3 =  data[3][mask]
        p4 =  data[4][mask]
        f1 = data[7][mask]
        f2 = data[8][mask]
        f3 = data[9][mask]
        f4 = data[10][mask]
        f5 = data[11][mask]
        temperature =  data[5][mask]
        times = times[mask]

        self.ui.figure.clear()
        self.axes = (self.ui.figure.add_subplot(1, 2, 1), self.ui.figure.add_subplot(1, 2, 2))
        print(self.axes)
        self.axes[0].plot(times, p1, label="Input P", color=get_color(1,5, "Reds"))
        self.axes[0].plot(times, p2, label="Pre-Filter", color=get_color(2,5, "Reds"))
        self.axes[0].plot(times, p3, label="Post-Filer", color=get_color(3,5, "Reds"))
        self.axes[0].plot(times, p4, label="Osmosis", color=get_color(4,5, "Reds"))
        self.axes[0].plot([], [], color='blue', label="Temperature")
        self.axes[0].set_xlabel("Hours Ago")
        self.axes[0].legend()


        self.axes[1].plot(times, f1, label="Input", color=get_color(1,6, "viridis"))
        self.axes[1].plot(times, f2+10, label="Chamber", color=get_color(2,6, "viridis"))
        self.axes[1].plot(times, f3+20, label="Overflow", color=get_color(3,6, "viridis"))
        self.axes[1].plot(times, f4+30, label="Drain", color=get_color(4,6, "viridis"))
        self.axes[1].plot(times, f5+40, label="Discard", color=get_color(5,6, "viridis"))
        self.axes[1].set_xlabel("Hours Ago")
        self.axes[1].legend()

        self.twax = self.axes[0].twinx()
        self.twax.plot(times,temperature, color='blue')
        self.twax.set_ylabel("Temp")
        if self._firstpt or self.ui.lock.isChecked():
            pass 
        else:
            self.axes[0].set_xlim(oldx)
            self.axes[0].set_ylim(oldy)
            self.twax.set_ylim(oldy2)
            self.axes[1].set_xlim(oldx)
            self.axes[1].set_ylim([-10, 150])
        self.ui.canvas.draw()
        if self._firstpt:
            self._firstpt = False


