from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtWidgets, QtGui, QtCore
from scipy.interpolate import interp1d
from scipy.optimize import minimize 
import numpy as np 
import os 
from scipy import stats 

from plotgui import Ui_Form as gui 

class PlotsWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget, logger:QtWidgets.QTextBrowser):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        self._logger = logger

        self._filepath = "/Users/bsmithers/software/PicoCode/ratio_data_osmosis.csv"
        
        self.ui.monitorBox.setChecked(True)
        self.ui.receiverBox.setChecked(True)
        self.ui.ratioBox.setChecked(True)
        self.update_plots()

        self.ui.monitorBox.stateChanged.connect(self.update_plots)
        self.ui.ratioBox.stateChanged.connect(self.update_plots)
        self.ui.receiverBox.stateChanged.connect(self.update_plots)
        self.ui.mintime.valueChanged.connect(self.update_plots)
        self.ui.maxtime.valueChanged.connect(self.update_plots)
        self.ui.comboBox.currentIndexChanged.connect(self.update_plots)

        self.ui.rollingBox.stateChanged.connect(self.update_plots)
        self.ui.showFitBox.stateChanged.connect(self.update_plots)
        self.ui.spinBox.valueChanged.connect(self.update_plots)

    def update_filepath(self, path):
        self._filepath = path
        self.update_plots()

    def update_plots(self):
        """

            Reload the data
            Check the configuration
            Process the data (as desired)

            Show only what is requested
        
        """
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
        if max_time<min_time:
            max_time = min_time+20

        mask = np.logical_and(times > min_time, times < max_time)
        times = times[mask]


        show_monitor = self.ui.monitorBox.isChecked()
        show_receiver = self.ui.receiverBox.isChecked()
        show_ratio = self.ui.ratioBox.isChecked() 
        as_mu = self.ui.comboBox.currentIndex() ==0
        as_no_pulse = self.ui.comboBox.currentIndex() == 1
        as_pulse_pulse = self.ui.comboBox.currentIndex() == 2

        rolling = self.ui.rollingBox.isChecked()
        do_fit = self.ui.showFitBox.isChecked()


        receiver_data = data[1][mask]
        monitor_data = data[3][mask]

        if as_no_pulse:
            receiver_data= 1-receiver_data
            monitor_data = 1-monitor_data
        elif as_mu:
            receiver_data = -np.log(1-receiver_data)
            monitor_data = -np.log(1-monitor_data)
        ratio = receiver_data / monitor_data
        
        if rolling:
            roll_amt = self.ui.spinBox.value()
            roll_time = np.convolve(times, np.ones(roll_amt), "valid")/roll_amt
            roll_value = np.convolve(ratio, np.ones(roll_amt), "valid")/roll_amt
            roll_mon =  np.convolve(monitor_data, np.ones(roll_amt), "valid")/roll_amt
            roll_rec = np.convolve(receiver_data, np.ones(roll_amt), "valid")/roll_amt

        else:
            roll_time = times
            roll_value = ratio 
            roll_mon = monitor_data
            roll_rec = receiver_data
            roll_amt = 5

        pval = np.nan
        if do_fit:
            # still need to get the error, so we grab a roll_fit_thing
            roll_amt = max([roll_amt, 5])
            if not rolling: 
                roll_amt = 5
                roll_fit_time = np.convolve(times, np.ones(roll_amt), "valid")/roll_amt
                roll_fit_value = np.convolve(ratio, np.ones(roll_amt), "valid")/roll_amt
            else:
                roll_fit_time = roll_time
                roll_fit_value = roll_value

            interpo = interp1d(roll_fit_time, roll_fit_value, bounds_error= False) # the noisiest 
            error = interpo(times) - ratio # difference between
            keep_mask = np.logical_not(np.isnan(error))
            error = error[keep_mask]
            error = np.percentile(np.abs(error), 68)

            def func_eval(xs, params):
                return params[0]*xs + params[1] 

            def metric(params, nosum=False):
                # params are m and b 

                y = func_eval(roll_time, params)
                if nosum:
                    return  0.5*((roll_value - y)/error)**2
                else:
                    return np.nansum( 0.5*((roll_value - y)/error)**2 )
            x0 = [0.2, np.nanmean(roll_value)]
            bounds = [[-50,50], [-2000, 2000]]
            res = minimize(metric, x0=x0, bounds=bounds, options={"eps":1e-15, "ftol":1e-20, "gtol":1e-20})
            fit_min = res.x

            dof = len(roll_time)-2
            fit_metric =2*metric(fit_min)
            pval = 1-stats.chi2.cdf(fit_metric, dof)
            self.ui.pval_value.setText(str(pval))

        

        if show_monitor:
            self.axes.plot(roll_time, roll_mon, label="Monitor")
        if show_receiver:
            self.axes.plot(roll_time, roll_rec, label="Receiver")
        if (show_monitor or show_receiver) and (show_ratio or do_fit):
            if show_ratio:
                self.axes.plot([], [], color='gray', label="Ratio")
            if do_fit:
                self.axes.plot([], [], color='red', label="Fit")
            self.axes.legend()
        if show_ratio or do_fit:
            twax = self.axes.twinx()
            twax.plot(roll_time, roll_value, color="gray", label="Ratio")
            twax.set_ylabel("Ratio")
            if do_fit:
                twax.plot(roll_time, func_eval(roll_time, fit_min), label="Fit", color='red',alpha=0.2, zorder=-5)

        self.axes.set_xlabel("Time [hr]", size=14)
        if show_monitor or show_receiver:
            if as_mu:
                self.axes.set_ylabel(r"$\mu=-\log(1-P_{0})$", size=14)
            elif as_no_pulse:
                self.axes.set_ylabel("No Pulse Rate", size=14)
            elif as_pulse_pulse:
                self.axes.set_ylabel("Pulse Rate", size=14)

        self.ui.canvas.draw()