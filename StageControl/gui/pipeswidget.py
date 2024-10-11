from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView 
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, QThreadPool, pyqtSignal

from warn_widg import WarnWidget

from pipes_gui import Ui_Form as gui
import numpy as np 

import pexpect
from emailer import send_alert
import os 

from StageControl.gui.constants import PRESSURE_THRESH,TEMP_MAX
SCALE = 5.0
PUMP_REQUIRED = True

class Clicker(QGraphicsScene):
    def __init__(self, parent:QGraphicsView, parent_window):
        QGraphicsScene.__init__(self, parent)
        self.parent = parent 
        self._parent_window = parent_window

class PipesWidget(QtWidgets.QWidget): 
    # signals used to communicate with the Pi-manager whenever we click a button 
    pump_signal = pyqtSignal(int, bool)
    sv_signal = pyqtSignal(int, bool)
    bv_signal = pyqtSignal(int, bool)
    def __init__(self, parent:QWidget,  logger, fake=False):
        QtWidgets.QWidget.__init__(self, parent)

        self._fake = False
        self.ui = gui()
        self.ui.setupUi(self)
        self._logger = logger

        self.scene = Clicker(self.ui.graphicsView, self)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setMouseTracking(True)

        self.scene.addPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), "data","diagram.jpg")) ).setScale(0.25)
    
        self.ui.bv1_button.stateChanged.connect(self.bv1_change)
        self.ui.bv2_button.stateChanged.connect(self.bv2_change)
        self.ui.bv3_button.stateChanged.connect(self.bv3_change)
        self.ui.bv4_button.stateChanged.connect(self.bv4_change)
        self.ui.bv5_button.stateChanged.connect(self.bv5_change)
        self.ui.bv6_button.stateChanged.connect(self.bv6_change)
        self.ui.sv1_button.stateChanged.connect(self.sv1_change)
        self.ui.sv2_button.stateChanged.connect(self.sv2_change)
        self.ui.pu1_button.stateChanged.connect(self.pu1_change)
        self.ui.pu2_button.stateChanged.connect(self.pu2_change)
        self.ui.pu3_button.stateChanged.connect(self.pu3_change)
        self.ui.drain_button.clicked.connect(self.drain_button_clicked)
        self.ui.fill_filter.clicked.connect(self.fill_filtered_clicked)
        self.ui.fill_osmosis.clicked.connect(self.fill_osmosis_clicked)
        self.ui.stop_button.clicked.connect(self.stop_button)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)

        self.alarm_timer = QtCore.QTimer(self)
        self.alarm_timer.timeout.connect(self.flash)

        self._fake_chamber = 0
        self._fake_open_tank_lvl = 0

        self._automated = False
        self._draining = False 
        self._filling_filter = False 
        self._filling_osmo = False
        self._draining_open_tank = False
        self._overflow_counter = 0
        self._chamber_drain_counter = 0

        self._ncalls = 0

        self._test_thermo_temperature = 20.0

        self._flash_red = True
        self._alarm = np.array([False, False, False, False])

        sound_file = os.path.join(os.path.dirname(__file__), "data","alarm.mp3")

        self._alert_thrown = False 

        self.update()

        #self.thread_man = QThreadPool(self)
        #self.setupThread()


    def stop_button(self):
        self.ui.status_label.setText("... Awaiting Input")
        self.enable_all()
        self.ui.bv1_button.setChecked(False)
        self.ui.bv2_button.setChecked(False)
        self.ui.bv3_button.setChecked(False)
        self.ui.bv4_button.setChecked(False)
        self.ui.bv5_button.setChecked(False)
        self.ui.bv6_button.setChecked(False)
        self.ui.sv1_button.setChecked(False)
        self.ui.sv2_button.setChecked(False)
        self.ui.pu1_button.setChecked(False)
        self.ui.pu2_button.setChecked(False)
        self.ui.pu3_button.setChecked(False)
        self._automated = False
        self._draining = False 
        self._filling_filter = False 
        self._filling_osmo = False
        self._overflow_counter = 0
        self._chamber_drain_counter = 0

    def drain_button_clicked(self):
        """
            Set the state of these bools so this empties, then resets the state 
        """
        self._automated = True 
        self._draining = True 
        self._filling_filter = False 
        self._filling_osmo = False 
        self.ui.status_label.setText("... DRAINING")
        self.disable_all() # while automatically doing things, we don't want the user tweaking the configuration of the gui
        self.ui.stop_button.setEnabled(True)

    def fill_osmosis_clicked(self):
        self._automated = True 
        self._draining = True 
        self._filling_osmo = True  
        self._filling_filter = False 
        self.disable_all()
        self.ui.status_label.setText("... DRAINING")
        self.ui.stop_button.setEnabled(True)
    def fill_filtered_clicked(self):
        self._automated = True 
        self._draining = True 
        self._filling_filter = True 
        self._filling_osmo = False 
        self.disable_all()
        self.ui.status_label.setText("... DRAINING")
        self.ui.stop_button.setEnabled(True)

    def flash(self):
        if any(self._alarm):
            if self._flash_red:
                self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,0,0)") 
                self.ui.temp_value_1.setStyleSheet("background-color:rgb(255,0,0)") 
                self.ui.temp_value_2.setStyleSheet("background-color:rgb(255,0,0)") 
                self._flash_red = False 
            else:
                if self._alarm[0]:
                    self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,255,255)")
                if self._alarm[1]:
                    self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,255,255)")
                if self._alarm[2]:
                    self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,255,255)")
                if self._alarm[3]:
                    self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,255,255)")
                if self._alarm[4]:
                    self.ui.temp_value_1.setStyleSheet("background-color:rgb(255,255,255)")
                if self._alarm[5]:
                    self.ui.temp_value_2.setStyleSheet("background-color:rgb(255,255,255)")
                self._flash_red = True

        if any(self._alarm):
            self.alarm_timer.start(250)
        else:
            self.alarm_timer.stop()

    def _generate_testdata(self):
        """
            This is set to emulate the operation of the water filtration as it was at TRIUMF. 
            I don't know how applicable this is to how the setup will be at CERN 

            It's probably not perfect, but it's good enough 
        """
        flows = np.array([
            0,0,0,0,0
        ])
        full = False 
        # This is the chamber drain pump. If it's checked, and there's water in the chamber, then water flows through flow meters 4 and 5
        if self.ui.pu2_button.isChecked():
            if self._fake_chamber>0:
                flows[3] = 1
                flows[4] = 1
            self._fake_chamber -= 10
            
        """
            This section handles flow through flowmeters 1, 2, 3, and 5 

            Basically, if sv1, sv2, and the pump are on (if the last one is required), we will get flow through meters 1 and 5. 
            But then if bv6 is on, the chamber starts to fill. Flow meter 5 stops seeing flow, but meter 2 does 
            If the chamber is filled, then the open tank starts to fill. Then flow meter 3 sees flow too 

            To have flow, you need sv1 and sv2 to be flowing
            If the pump is required, you also need PU1 turned on 
                PR | not PR | sv2 |  not PR or sv2  
                T  |    F   |  T  |       T
                T  |    F   |  F  |       F
                F  |    T   |  T  |       T
                F  |    T   |  F  |       T

                    so this will only be false if the pump is needed and if sv2 is off 
        """
        if self.ui.sv1_button.isChecked() and self.ui.sv2_button.isChecked() and ((not PUMP_REQUIRED) or self.ui.pu1_button.isChecked()):
            flows[0] = 1
            flows[4] = 1 
            if self.ui.bv6_button.isChecked():
                flows[4] = 0
                flows[1] = 1 
                self._fake_chamber += 10 
                if self._fake_chamber > 50:
                    full = True 
                    flows[2] = 1 
                    self._fake_open_tank_lvl += self._fake_chamber-50
                    self._fake_chamber = 50

        # if pump3 is on and there's water in the fake open tank, then we expect flow in flow meter 5 
        # we then have some logic to fake-drain the fake open tank 
        if self.ui.pu3_button.isChecked() and self._fake_open_tank_lvl>0:
            flows[4] = 1
            self._fake_open_tank_lvl-=15
            if self._fake_open_tank_lvl<0:
                self._fake_open_tank_lvl = 0
        if self._fake_chamber<0:
            self._fake_chamber = 0

        # make up some fake pressures that go down
        # but only show pressure if 
        flows = flows.astype(int)
        pressures = 20 + np.random.randn(4)*3
        scales = np.array([30, 5, -5, -10])
        if not self.ui.sv1_button.isChecked() or (not ((not PUMP_REQUIRED) or self.ui.pu1_button.isChecked())):
            pressures*=0
            scales*=0
        # used to fake an alarm
        if False and full:
            pressures[0] *= 20

        pressures = pressures + scales

        # sample some temperatures 
        # have a counter to steadily ramp up the UV sterilizer heater 
        temperatures = np.random.randn(2)*0.1 + 20
        temperatures[0] += self._ncalls
        #self._ncalls += 5

        # Water will flow over the uv sterilizer in this case, so we simulate it cooling down here 
        # note - this doesn't account for whether the pump needs to be on... 
        if self.ui.pu1_button.isChecked() and self.ui.sv1_button.isChecked() and self.ui.sv2_button.isChecked() and self.ui.bv3_button.isChecked():
            self._ncalls -= 7
            if self._ncalls <0 :
                self._ncalls = 0

        
        return pressures, flows, temperatures

    def disable_all(self):
        """
            Disable the buttons, makes the gui non-interactable 
        """
        self.ui.bv1_button.setEnabled(False)
        self.ui.bv2_button.setEnabled(False)
        self.ui.bv3_button.setEnabled(False)
        self.ui.bv4_button.setEnabled(False)
        self.ui.bv5_button.setEnabled(False)
        self.ui.bv6_button.setEnabled(False)
        self.ui.sv1_button.setEnabled(False)
        self.ui.sv2_button.setEnabled(False)
        self.ui.pu1_button.setEnabled(False)
        self.ui.pu2_button.setEnabled(False)
        self.ui.pu3_button.setEnabled(False)
        self.ui.drain_button.setEnabled(False)
        self.ui.fill_filter.setEnabled(False)
        self.ui.fill_osmosis.setEnabled(False)

        # turn everything off! 
        self.ui.bv1_button.setChecked(False)
        self.ui.bv2_button.setChecked(False)
        self.ui.bv3_button.setChecked(False)
        self.ui.bv4_button.setChecked(False)
        self.ui.bv5_button.setChecked(False)
        self.ui.bv6_button.setChecked(False)
        self.ui.sv1_button.setChecked(False)
        self.ui.sv2_button.setChecked(False)
        self.ui.pu1_button.setChecked(False)
        self.ui.pu2_button.setChecked(False)
        self.ui.pu3_button.setChecked(False)

    def enable_all(self):
        self.ui.bv1_button.setEnabled(True)
        self.ui.bv2_button.setEnabled(True)
        self.ui.bv3_button.setEnabled(True)
        self.ui.bv4_button.setEnabled(True)
        self.ui.bv5_button.setEnabled(True)
        self.ui.bv6_button.setEnabled(True)
        self.ui.sv1_button.setEnabled(True)
        self.ui.sv2_button.setEnabled(True)
        self.ui.pu1_button.setEnabled(True)
        self.ui.pu2_button.setEnabled(True)
        self.ui.pu3_button.setEnabled(True)
        self.ui.drain_button.setEnabled(True)
        self.ui.fill_filter.setEnabled(True)
        self.ui.fill_osmosis.setEnabled(True)

    @pyqtSlot(dict)
    def data_received(self, data):
        """
            This is a slot that is accessed by the SSH manager (or really anything)
            This must be called with the new data.

            The new data is essentially just stored in the gui until its accessed later.
        """
        flows = data["flow"]
        pressures = data["pressure"]
        temperature = data["temperature"]

        # NOTE: there's a problem where the pi will hang while doing this sometimes. Need to find a way to catch that. 
        # will likely need some kind of threading :(
        ### -------------------------------- UPDATE GUI --------------------------------
        flow_bar = np.array(flows)*90+5
        self.ui.flow1.setValue(flow_bar[0])
        self.ui.flow2.setValue(flow_bar[1])
        self.ui.flow3.setValue(flow_bar[2])
        self.ui.flow4.setValue(flow_bar[3])
        self.ui.flow5.setValue(flow_bar[4])

        self.ui.temp_value_1.setText("{:.2f}".format(temperature[0]))
        self.ui.temp_value_2.setText("{:.2f}".format(temperature[1]))

        self.ui.lcdNumber.setText("{:.2f}".format(pressures[0]))
        self.ui.lcdNumber_4.setText("{:.2f}".format(pressures[1]))
        self.ui.lcdNumber_3.setText("{:.2f}".format(pressures[2]))
        self.ui.lcdNumber_2.setText("{:.2f}".format(pressures[3])) 

    def update(self):
        """
            Access the latest data from the gui
            check for warnings, proceed with automation
        """
        if self._fake:
            pressures, flows, temperature = self._generate_testdata()
        #else:

        ### -------------------------------- Check for Alarms --------------------------------

        pressures = np.array([float(self.ui.lcdNumber.text()),
                              float(self.ui.lcdNumber_4.text()),
                              float(self.ui.lcdNumber_3.text()),
                              float(self.ui.lcdNumber_2.text())
                              ])
        flows = np.array([
                            self.ui.flow1.value() > 50,
                            self.ui.flow2.value() > 50,
                            self.ui.flow3.value() > 50,
                            self.ui.flow4.value() > 50,
                            self.ui.flow5.value() > 50
        ])
        temperature = np.array([
            float(self.ui.temp_value_1.text()),
            float(self.ui.temp_value_2.text())
        ])

        self._alarm = pressures>PRESSURE_THRESH # all of the pressures 
        self._alarm=  self._alarm.tolist()
        self._alarm.append(temperature[0] > TEMP_MAX) # uv sterilizer temperature 
        self._alarm.append(temperature[1] > TEMP_MAX) # water temperature
        
        # if _any_ alarm is True, something is wrong 
        # we don't want to spam alarm messages, so we keep track of if an alarm is sounding between updates 
        if any(self._alarm):
            # this was thrown last update (or earlier)
            if self._alert_thrown:
                pass 
            else:
                # craft an alert message, make a note of what kind of problem this is 
                # a heat-related problem has us wanting to move water over the UV sterilizer, a pressure problem has us wanting to shut the valves off 

                self._alert_thrown = True 
                message = "Warning! The water pressure is dangerously high! Shutting off input valve and chamber valve"
                heat = False 
                if self._alarm[4]:
                    heat = True  
                    message = "Warning! The UV Thermocouple is reading a dangerously high temperature (>50C)! Trying to pass water over the UV sterilier. You should turn the UV sterilizer off too."
                if self._alarm[5]:
                    heat = True 
                    message = "Warning! The water temperature is dangerously high!"

                # call panic. This sends an email, makes a pop-up, and tries to fix the problem
                self.panic(message, heat)                
                self.alarm_timer.start(250) # start flashing the gui red and white
        else:
            # no problems. Make sure the gui looks ok and that no alarm is sounding
            self._alert_thrown = False 
            self.alarm_timer.stop()
            self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.temp_value_2.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.temp_value_1.setStyleSheet("background-color:rgb(255,255,255)")
            
        # these are automatic! 
        if self._fake:
            if self.open_tank_75:
                self.ui.pu3_button.setChecked(True)
                self._draining_open_tank = True 
            if self._draining_open_tank:
                if not self.open_tank_25:
                    self.ui.pu3_button.setChecked(False)
                    self._draining_open_tank=False

        self.timer.start(2500)

        if self._automated:
            # first, check if the chamber is being drained 
            if self._draining:
                setup = True 
                # if pump2 is already on, then the chamber is already draining, and we can check if water no longer flows out of the chamber 
                if self.ui.pu2_button.isChecked():
                    outflow = flows[3]
                    if not outflow:
                        self._chamber_drain_counter += 1
                    else:
                        self._chamber_drain_counter = 0
                    
                    # once it has been consistently empty for four updates, we stop the draining procedure 
                    if self._chamber_drain_counter>4:
                        self._draining = False 
                        # we only need to cleanup if there isn't a second step!
                        if not (self._filling_filter or self._filling_osmo):
                            self._automated = False 
                            self.enable_all()
                            self.ui.stop_button.setEnabled(False)
                            self.ui.status_label.setText("... Done!")

                        self._chamber_drain_counter = 0
                        self.ui.pu2_button.setChecked(False)
                        setup = False 

                if setup:
                    self.ui.bv6_button.setChecked(False)
                    self.ui.sv1_button.setChecked(False)
                    self.ui.sv2_button.setChecked(False)
                    self.ui.pu2_button.setChecked(True)
                    

            elif self._filling_filter or self._filling_osmo:
                self.ui.status_label.setText("... FILLING")
                overflow = flows[2]
                # first time around, these will both be turned off, so we don't turn bv6 on yet! 
                # bv6 will be turned on the _second_ time this is reached 
                if self.ui.sv1_button.isChecked() and self.ui.sv2_button.isChecked():
                    self.ui.bv6_button.setChecked(True)

                self.ui.pu1_button.setChecked(True)
                self.ui.sv1_button.setChecked(True)
                self.ui.sv2_button.setChecked(True)

                if self._filling_filter:
                    self.ui.bv2_button.setChecked(True)
                    self.ui.bv4_button.setChecked(True) 
                elif self._filling_osmo:
                    self.ui.bv5_button.setChecked(True)

                if overflow:
                    self._overflow_counter+=1

                    if self._overflow_counter>3:
                        self.ui.sv1_button.setChecked(False)
                        self.ui.bv2_button.setChecked(False)
                        self.ui.bv4_button.setChecked(False)
                        self.ui.bv5_button.setChecked(False)
                        self.ui.bv6_button.setChecked(False)
                        self.ui.sv2_button.setChecked(False)
                        self.ui.pu1_button.setChecked(False)
                        self._filling_filter = False 
                        self._filling_osmo = False 
                        self._automated = False
                        self._overflow_counter = 0
                        self.enable_all()
                        self.ui.stop_button.setEnabled(False)
                        self.ui.status_label.setText("... Done!")
                else:
                    self._overflow_counter = 0
        

    def panic(self, message, heat=False, skip_email=False):
        """
            Called in an emergency! 
            Shuts off automation, enables the gui, and then sets up the tubes in the right way
        """
        self.enable_all()
        self.ui.stop_button.setEnabled(False)
        self._automated = False 
        self._filling_filter = False 
        self._filling_osmo = False 

        if heat:
            self.ui.bv6_button.setChecked(False)
            self.ui.pu1_button.setChecked(True)
            self.ui.bv3_button.setChecked(True)

        self.ui.sv1_button.setChecked(heat)
        self.ui.sv2_button.setChecked(heat) 
        self._logger.insert_text(message + "\n")
        if not skip_email:
            self._logger.send_alert( message, "Warning!")
        self.dialog = WarnWidget(parent=self,message=message)
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.exec_()

    """
        Boilerplate stuff. Whenever one of these is changed the function gets called. 
        In non-test mode, the rhaspberry pi is told to do things
    """

    def bv1_change(self):
        if not self._fake:
            self.bv_signal.emit(1, self.ui.bv1_button.isChecked())
    def bv2_change(self):
        if not self._fake:
            self.bv_signal.emit(2, self.ui.bv2_button.isChecked())
    def bv3_change(self):
        if not self._fake:
            self.bv_signal.emit(3, self.ui.bv3_button.isChecked())
    def bv4_change(self):
        if not self._fake:
            self.bv_signal.emit(4, self.ui.bv4_button.isChecked())
    def bv5_change(self):
        if not self._fake:
            self.bv_signal.emit(5, self.ui.bv5_button.isChecked())
    def bv6_change(self):
        if not self._fake:
            self.bv_signal.emit(6, self.ui.bv6_button.isChecked())

    def sv1_change(self):
        if not self._fake:
            self.sv_signal.emit(1, self.ui.sv1_button.isChecked())
    def sv2_change(self):
        if not self._fake:
            self.sv_signal.emit(2, self.ui.sv2_button.isChecked())

    def pu1_change(self):
        if not self._fake:
            self.pump_signal.emit(1, self.ui.pu1_button.isChecked())
    def pu2_change(self):
        if not self._fake:
            self.pump_signal.emit(2, self.ui.pu2_button.isChecked())
    def pu3_change(self):
        if not self._fake:
            self.pump_signal.emit(3, self.ui.pu3_button.isChecked())

    @property
    def open_tank_25(self)->bool:
        if self._fake: 
            return self._fake_open_tank_lvl>50
        else:
            raise NotImplementedError("")
    @property
    def open_tank_50(self)->bool:
        if self._fake: 
            return self._fake_open_tank_lvl>100
        else:
            raise NotImplementedError("")
    @property
    def open_tank_75(self)->bool:
        if self._fake: 
            return self._fake_open_tank_lvl>150
        else:
            raise NotImplementedError("")
