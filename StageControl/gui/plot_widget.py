from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from scipy.interpolate import interp1d
from scipy.optimize import minimize 
import numpy as np 
import os 
from scipy import stats 
import json
import time 
from plotgui import Ui_Form as gui 

from StageControl.water.utils import build_bounds, get_fill_times

wavelens = [450, 410, 365, 295, 278, 255]
import matplotlib.pyplot as plt 
def get_color(n, colormax=3.0, cmap="viridis"):
    """
        Discretize a colormap. Great getting nice colors for a series of trends on a single plot! 
    """
    this_cmap = plt.get_cmap(cmap)
    return this_cmap(n/colormax)


class PlotsWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget, logger:QtWidgets.QTextBrowser):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        self._logger = logger

#        self._filepath = "/home/watermon/software/PicoCode/ratio_data_live.csv"
        self._filepath = "/home/watermon/software/StageControl/StageControl/gui/picodat/picodat_run23_Return Untreated_various_variousadc_mHz.dat"
        self._warned=False
        self._oldname=self._filepath 

        if False:
            self.ui.monitorBox.setChecked(True)
            self.ui.receiverBox.setChecked(True)
            self.ui.ratioBox.setChecked(True)
            

            self.ui.monitorBox.stateChanged.connect(self.update_plots)
            self.ui.ratioBox.stateChanged.connect(self.update_plots)
            self.ui.receiverBox.stateChanged.connect(self.update_plots)
            self.ui.mintime.valueChanged.connect(self.update_plots)
            self.ui.maxtime.valueChanged.connect(self.update_plots)
            self.ui.comboBox.currentIndexChanged.connect(self.update_plots)

            self.ui.rollingBox.stateChanged.connect(self.update_plots)
            self.ui.showFitBox.stateChanged.connect(self.update_plots)
            self.ui.spinBox.valueChanged.connect(self.update_plots)

        self._ref_data = {}
        self._filltime = -1
        self._reference_file = "/home/watermon/software/StageControl/StageControl/gui/picodat/picodat_run24_Return Untreated_various_variousadc_mHz.dat"
        self.update_reference()

        self.update_plots()

    def update_reference(self):
        if os.path.exists(self._reference_file):
            self._ref_data =  build_bounds(self._reference_file)
    
    @pyqtSlot()
    def update_filltime(self):
        self._filltime = -1

    def update_filepath(self, path):
        self._filepath = path
        self._filltime = -1
        self.update_plots()

    @pyqtSlot(int, int , int, int)
    def plot_wrap(self, a,b,c,d):
        self.update_plots()

    def update_plots(self):
        """
            Reload the data
            Check the configuration
            Process the data (as desired)

            Show only what is requested
        
        """
        self.ui.figure.clear()
        if self._oldname != self._filepath:
            self._warned = False 
            self._oldname = self._filepath

        if not os.path.exists(self._filepath):
            print("couldn't find it")
            print(self._filepath)
            return 
        self.axes = self.ui.figure.add_subplot(111)

        data = np.loadtxt(self._filepath, delimiter=",").T 
        
        
        trigger_data = data[1]
        tmask = trigger_data>0
        receiver_data = -1*np.log(1 - data[2][tmask]/trigger_data[tmask])
        monitor_data = -1*np.log(1- data[3][tmask]/trigger_data[tmask])
    
        if self._filltime==-1:
            self._filltime = get_fill_times(data[0]) # the _last_ fill time    

        
            if len(self._filltime)==0:
                self._filltime = data[0][0]
            else:
                self._filltime =self._filltime[-1]

        fill_mask = data[0][tmask]>=self._filltime

        ratio = (monitor_data/receiver_data)[fill_mask]
        times = (data[0][tmask][fill_mask] - self._filltime)/3600

        if len(times)==0:
            print("No valid fills found - this is likely older data")
            return 
        waveno =  data[5][tmask][fill_mask]
        
        for _i in range(len(self._ref_data["mean"])):
            i = _i+1
            self.axes.fill_between(self._ref_data["times"], 
                             self._ref_data["mean"][i]- self._ref_data["std"][i],
                             self._ref_data["mean"][i]+self._ref_data["std"][i],
                             color=get_color(i+1, 8, 'nipy_spectral_r'),label="{} nm".format(wavelens[i]), alpha=0.5, zorder=i)
        
        
        for _i in range(5):
            i = _i+1

            wavemask = waveno==i 
            self.axes.plot(times[wavemask], ratio[wavemask], color=get_color(i+1, 8, 'nipy_spectral_r'), zorder=10+i, marker='d', ls='')

        self.axes.set_ylim([0, 0.3])
        self.axes.set_xlim([0, 1.4])
        self.axes.set_xlabel("Hours Since Tube Full", size=14)
        self.axes.set_ylabel(r"Mean $\mu$ Ratio", size=14)
        self.axes.legend()

        self.ui.canvas.draw()
