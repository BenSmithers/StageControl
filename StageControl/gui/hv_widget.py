from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import sys 
import os 
from time import time 
from single_hvbox_gui import Ui_Widget as gui
from PyQt5.QtCore import pyqtSlot, QThreadPool, pyqtSignal
from constants import HV_ONE, HV_TWO
from StageControl.CAENControl import Status

class ComboWidgGui(object):
    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(1114, 543)
        self.verticalLayout = QtWidgets.QVBoxLayout(Widget)
        self.verticalLayout.setObjectName("verticalLayout")

        # will need to manually add in the things
        QtCore.QMetaObject.connectSlotsByName(Widget)


class HVBoxWidget(QtWidgets.QWidget):

    set_voltage = pyqtSignal(float)
    set_current = pyqtSignal(float)
    
    def __init__(self, parent:QWidget, name:str):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)
        self.ui.name_lbl.setText(name)
        self.ui.apply_v.clicked.connect(self.set_voltage_press)
        self.ui.apply_I.clicked.connect(self.set_current_press)

        self._all_checks = [
            self.ui.on_box, self.ui.rup_box, self.ui.rdwn_box, self.ui.ovv_box,
            self.ui.ovc_box, self.ui.unv_box, self.ui.maxv_box, self.ui.trip_box,
            self.ui.OVP_box, self.ui.RES0_box, self.ui.DIS_box, self.ui.KILL_box, 
            self.ui.ILK_box, self.ui.NOCAL_box, self.ui.RES1_box, self.ui.RES2_box
        ]

    @pyqtSlot(float)
    def setSetV(self, value):
        self.ui.voltage_set.setValue(value)
    @pyqtSlot(float)
    def setSetI(self, value):
        self.ui.current_set.setValue(value)

    @pyqtSlot(float)
    def setReadVoltage(self, value):
        self.ui.voltage_disp.setText("{:.3f} V".format(value))
    @pyqtSlot(float)
    def setReadCurrent(self, value):
        self.ui.current_disp.setText("{:.3f} uA".format(value))

    @pyqtSlot(Status)
    def setStatus(self, this_stat):
        for check in self._all_checks:
            check.setChecked(False)
        
        for i, name in enumerate(Status):
            if name in this_stat:
                self._all_checks[i].setChecked(True)

    def set_voltage_press(self):
        self.set_voltage.emit(self.ui.voltage_set.value())
    def set_current_press(self):
        self.set_current.emit(self.ui.current_set.value())

class HVWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = ComboWidgGui()
        self.ui.setupUi(self)

        self._hvboxone = HVBoxWidget(self, "HV One")
        self._hvboxtwo = HVBoxWidget(self, "HV Two")
        self.ui.verticalLayout.addWidget(self._hvboxone)
        self.ui.verticalLayout.addWidget(self._hvboxtwo)
    
    @property
    def hvboxone(self)->HVBoxWidget:
        return self._hvboxone
    @property
    def hvboxtwo(self)->HVBoxWidget:
        return self._hvboxtwo
