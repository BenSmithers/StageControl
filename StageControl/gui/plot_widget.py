from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtWidgets, QtGui, QtCore

import numpy as np 
import os 

from plotgui import Ui_Form as gui 

class PlotsWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        self._filepath = ""

        self.ui.monitorBox.stateChanged.connect(self.update_plots)
        self.ui.ratioBox.stateChanged.connect(self.update_plots)
        self.ui.receiverBox.stateChanged.connect(self.update_plots)
        self.ui.mintime.valueChanged.connect(self.update_plots)
        self.ui.maxtime.valueChanged.connect(self.update_plots)
        self.ui.comboBox.currentIndexChanged.connect(self.update_plots)


    def update_filepath(self, path):
        self._filepath = path
        self.update_plots()
        print("new path", path)

    def update_plots(self):
        self.ui.figure.clear()
    
        if not os.path.exists(self._filepath):
            print("couldn't find it")
            print(self._filepath)
            return 
        self.axes = self.ui.figure.add_subplot(111)
        data = np.loadtxt(self._filepath, delimiter=",").T 

        times = (data[0] - np.min(data[0]))/3600

        min_time = self.ui.mintime.value()
        max_time = self.ui.maxtime.value()

        mask = np.logical_and(times > min_time, times < max_time)
        times = times[mask]


        show_monitor = self.ui.monitorBox.isChecked()
        show_receiver = self.ui.receiverBox.isChecked()
        show_ratio = self.ui.ratioBox.isChecked() 
        as_mu = self.ui.comboBox.currentIndex() ==0
        as_no_pulse = self.ui.comboBox.currentIndex() == 1
        as_pulse_pulse = self.ui.comboBox.currentIndex() == 2

        receiver_data = data[1][mask]
        monitor_data = data[3][mask]

        if as_no_pulse:
            receiver_data= 1-receiver_data
            monitor_data = 1-monitor_data
        elif as_mu:
            receiver_data = -np.log(1-receiver_data)
            monitor_data = -np.log(1-monitor_data)
        ratio = receiver_data / monitor_data


        if show_monitor:
            self.axes.plot(times, monitor_data, label="Monitor")
        if show_receiver:
            self.axes.plot(times, receiver_data, label="Monitor")
        if (show_monitor or show_receiver) and show_ratio:
            self.axes.plot([], [], color='gray', label="Ratio")
            self.axes.legend()
        if show_ratio:
            twax = self.axes.twinx()
            twax.plot(times, ratio, color="gray", label="Ratio")
            twax.set_ylabel("Ratio")

        self.axes.set_xlabel("Time [hr]", size=14)
        if show_monitor or show_receiver:
            if as_mu:
                self.axes.set_ylabel(r"$\mu$", size=14)
            elif as_no_pulse:
                self.axes.set_ylabel("No Pulse Rate", size=14)
            elif as_pulse_pulse:
                self.axes.set_ylabel("Pulse Rate", size=14)

        self.ui.canvas.draw()