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
from datetime import datetime
from plotgui import Ui_Form as gui 

from StageControl.water.utils import build_bounds, get_fill_times
from utils import get_event_time 
wavelens = [450, 410, 365, 295, 278, 255]
baseline = [np.nan, 1.2548, 0.82710, 0.336267, 0.283956677, 0.2406189]
baseline = [np.nan, 1.17566, 0.7802, 0.3149, 0.266777, 0.2183807]
baseline = [np.nan, 1.1820821, 0.7887177, 0.3253037, 0.279768, 0.2285]
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
        self._reference_file = "/home/watermon/software/StageControl/StageControl/gui/picodat/picodat_run37_Supply Untreated_various_variousadc_mHz.dat"
        self._warned=False
        self._oldname=self._filepath 

        self._firstpt = True
        self._putimes = -1
        self._mintime = datetime(1980,1, 1, 1, 1)

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
        

        self.update_reference(self._reference_file)

        self.update_plots()

    def update_reference(self, newname):
        self._mintime = datetime(1980,1, 1, 1, 1)
        if os.path.exists(newname):
            self._reference_file = newname
            self._ref_data =  build_bounds(self._reference_file)
    
    @pyqtSlot()
    def update_filltime(self):
        self._filltime = -1

    def update_filepath(self, path):
        self._mintime = datetime(1980,1, 1, 1, 1)
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
        if not (self._firstpt):
            oldx = self.axes.get_xlim()
            oldy = self.axes.get_ylim()
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
        if len(data)<7:
            print("Old unsupported data")
            return 
        
        trigger_data = data[1]
        tmask = trigger_data>0
        scale = 1.0
        receiver_data = -1*np.log(1 - (data[3][tmask]-0.75*data[5][tmask])/trigger_data[tmask])
        monitor_data = -1*np.log(1- (data[2][tmask]-0.5*data[4][tmask])/trigger_data[tmask])


        

        dt_time =  np.array([datetime.fromtimestamp(entry) for entry in data[0][tmask]])
        
        # okay now we need a new one...
        pre_shift = int(dt_time[-1].hour<3)
        mo_shift = int( (dt_time[-1].day<2) and (pre_shift==1) ) # shifting a day back on the first of the month
        self._mintime = datetime(dt_time[-1].year, dt_time[-1].month-mo_shift, dt_time[-1].day-pre_shift, (dt_time[-1].hour-2) % 24)
        othermin = datetime(2020, 1, 1, 1)
        fill_mask = data[0][tmask] > int(othermin.timestamp())

        ratio = (receiver_data/monitor_data)[fill_mask]
        ratio = np.log((trigger_data[tmask] - data[3][tmask])/(trigger_data[tmask]-0.75*data[5][tmask]))/np.log((trigger_data[tmask]-data[2][tmask])/(trigger_data[tmask]-0.5*data[4][tmask]))

        waveno =  data[7][tmask][fill_mask]
        
        puoff_time = get_event_time(data[0], "pu1 off signal sent")
        puoff_time = [datetime.fromtimestamp(entry) for entry in puoff_time]
        for _i in range(len(self._ref_data["mean"])):
            i = _i+1
            break
            self.axes.fill_between(self._ref_data["times"], 
                             self._ref_data["mean"][i]- self._ref_data["std"][i],
                             self._ref_data["mean"][i]+self._ref_data["std"][i],
                             color=get_color(i+1, 8, 'nipy_spectral_r'),label="{} nm".format(wavelens[i]), alpha=0.5, zorder=i)
        
         #self.axes.set_ylim([0, 1.0])
        dayshift = int(self._mintime.hour+4 >23)
        
        lims = [self._mintime, datetime(self._mintime.year, self._mintime.month+mo_shift, self._mintime.day+dayshift, (self._mintime.hour+4) % 24)]



        for _i in range(5):
            i = _i+1
            wavemask = waveno==i 
#            self.axes.fill_between(lims, baseline[i]-0.02*baseline[i], baseline[i]+0.02*baseline[i], color=get_color(i+1, 8, 'nipy_spectral_r'), zorder=i, alpha=0.3)
            self.axes.plot(dt_time[fill_mask][wavemask], (ratio[wavemask] - baseline[i])/baseline[i], color=get_color(i+1, 8, 'nipy_spectral_r'), label="{}nm".format(wavelens[i]), marker='d', ls='', zorder=10+i)

        self.axes.vlines(puoff_time, -0.1, 0.1, color='gray', alpha=0.5, ls='--',label="Pump Off Time")
        self._putimes = len(puoff_time)
        self.axes.hlines([-0.03, 0.03], datetime(year=2024,month=1,day=1), datetime(year=2027, month=1, day=1), color='red', ls='--')
        self.axes.set_xlabel("Time Stamp", size=14)
        self.axes.set_ylabel(r"Fractional Deviation", size=14)

        if self._firstpt or self.ui.zoombut.isChecked():
            self.axes.set_xlim(lims)
            self.axes.set_ylim([-0.10, 0.10])
        else:
            self.axes.set_xlim(oldx)
            self.axes.set_ylim(oldy)
        
        self.axes.legend()
        self.ui.figure.autofmt_xdate()
        self.ui.canvas.draw()
        if self._firstpt:
            self._firstpt = False
        


