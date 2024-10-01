from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView 
from PyQt5 import QtWidgets, QtGui, QtCore

from warn_widg import WarnWidget

from pipes_gui import Ui_Form as gui
import numpy as np 

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QColor
from emailer import send_alert
import os 

SCALE = 5.0


class Box(QPolygonF):
    def __init__(self, center:QPointF):
        points = [
            QPointF( center.x()-SCALE , center.y()-SCALE),
            QPointF( center.x()-SCALE , center.y()+SCALE),
            QPointF( center.x()+SCALE , center.y()+SCALE),
            QPointF( center.x()+SCALE , center.y()-SCALE),
        ]
        super().__init__(points)

class Diamond(QPolygonF):
    def __init__(self, center:QPointF):
        points = [
            QPointF( center.x()-SCALE , center.y()),
            QPointF( center.x() , center.y()+SCALE),
            QPointF( center.x()+SCALE , center.y()),
            QPointF( center.x() , center.y()-SCALE)
        ]
        super().__init__(points)


class Clicker(QGraphicsScene):
    def __init__(self, parent:QGraphicsView, parent_window):
        QGraphicsScene.__init__(self, parent)
        self.parent = parent 
        self._parent_window = parent_window


class PipesWidget(QtWidgets.QWidget):    
    def __init__(self, parent:QWidget,  logger):
        QtWidgets.QWidget.__init__(self, parent)
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
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)

        self.alarm_timer = QtCore.QTimer(self)
        self.alarm_timer.timeout.connect(self.flash)

        self._fake_chamber = 0
        self._fake_open_tank = 0

        self._automated = False
        self._draining = False 
        self._filling_filter = False 
        self._filling_osmo = False
        self._overflow_counter = 0
        self._chamber_drain_counter = 0

        self._flash_red = True
        self._alarm = np.array([False, False, False, False])

        sound_file = os.path.join(os.path.dirname(__file__), "data","alarm.mp3")

        self._alert_thrown = False 


        self.update()



    def drain_button_clicked(self):
        self._automated = True 
        self._draining = True 
        self._filling_filter = False 
        self._filling_osmo = False 
        self.ui.status_label.setText("... DRAINING")
        self.disable_all()

    def fill_osmosis_clicked(self):
        self._automated = True 
        self._draining = True 
        self._filling_osmo = True  
        self._filling_filter = False 
        self.disable_all()
        self.ui.status_label.setText("... DRAINING")
    def fill_filtered_clicked(self):
        self._automated = True 
        self._draining = True 
        self._filling_filter = True 
        self._filling_osmo = False 
        self.disable_all()
        self.ui.status_label.setText("... DRAINING")

    def flash(self):
        if any(self._alarm):
            if self._flash_red:
                self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,0,0)")
                self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,0,0)") 
                self._flash_red = False 
            else:
                self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,255,255)")
                self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,255,255)")
                self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,255,255)")
                self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,255,255)")
                self._flash_red = True

        if any(self._alarm):
            self.alarm_timer.start(250)
        else:
            self.alarm_timer.stop()

    def _generate_testdata(self):
        flows = np.array([
            0,0,0,0,0
        ])
        full = False
        if self.ui.pu2_button.isChecked():
            if self._fake_chamber>0:
                flows[3] = 1
                flows[4] = 1
            self._fake_chamber -= 10
            
        if self.ui.sv1_button.isChecked() and self.ui.sv2_button.isChecked():
            flows[0] = 1
            flows[4] = 1 
            if self.ui.bv6_button.isChecked():
                flows[1] = 1 
                self._fake_chamber += 10 
                if self._fake_chamber > 50:
                    full = True 
                    flows[2] = 1 
                    self._fake_chamber = 50
                if not full:
                    flows[4] = 0

        if self._fake_chamber<0:
            self._fake_chamber = 0


        flows = flows.astype(int)
        pressures = 20 + np.random.randn(4)*3
        scales = np.array([30, 5, -5, -10])
        if not self.ui.sv1_button.isChecked():
            pressures*=0
            scales*=0
        if False: # full:
            pressures[0] *= 20

        pressures = pressures + scales

        temperatures = np.zeros(6)

        return pressures, flows

    def disable_all(self):
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

    def update(self):
        
        pressures, flows = self._generate_testdata()

        flow_bar = flows*90+5
        self.ui.flow1.setValue(flow_bar[0])
        self.ui.flow2.setValue(flow_bar[1])
        self.ui.flow3.setValue(flow_bar[2])
        self.ui.flow4.setValue(flow_bar[3])
        self.ui.flow5.setValue(flow_bar[4])

        self._alarm = pressures>60

        self.ui.lcdNumber.setText("{:.2f}".format(pressures[0]))
        self.ui.lcdNumber_4.setText("{:.2f}".format(pressures[1]))
        self.ui.lcdNumber_3.setText("{:.2f}".format(pressures[2]))
        self.ui.lcdNumber_2.setText("{:.2f}".format(pressures[3]))

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
                        self.ui.status_label.setText("... Done!")
                else:
                    self._overflow_counter = 0
                        
        if any(self._alarm):
            if self._alert_thrown:
                pass 
            else:
                self._alert_thrown = True 
                self.enable_all()
                self._automated = False 
                self._filling_filter = False 
                self._filling_osmo = False 
                self.ui.sv1_button.setChecked(False)
                self.ui.sv2_button.setChecked(False)

                message = "Warning! The water pressure is dangerously high! Shutting off input valve and chamber valve"
                self._logger.insert_text(message + "\n")
                #send_alert( message)
                self.dialog = WarnWidget(parent=self,message=message)
                self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                self.dialog.exec_()
                self.alarm_timer.start(250)
        else:
            self._alert_thrown = False 
            self.alarm_timer.stop()
            self.ui.lcdNumber.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_4.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_3.setStyleSheet("background-color:rgb(255,255,255)")
            self.ui.lcdNumber_2.setStyleSheet("background-color:rgb(255,255,255)")

    def bv1_change(self):
        self._logger.insert_text("bv1 {}\n".format("on" if self.ui.bv1_button.isChecked() else "off")) 
    def bv2_change(self):
        self._logger.insert_text("bv2 {}\n".format("on" if self.ui.bv2_button.isChecked() else "off")) 
    def bv3_change(self):
        self._logger.insert_text("bv3 {}\n".format("on" if self.ui.bv3_button.isChecked() else "off")) 
    def bv4_change(self):
        self._logger.insert_text("bv4 {}\n".format("on" if self.ui.bv4_button.isChecked() else "off")) 
    def bv5_change(self):
        self._logger.insert_text("bv5 {}\n".format("on" if self.ui.bv5_button.isChecked() else "off")) 
    def bv6_change(self):
        self._logger.insert_text("bv6 {}\n".format("on" if self.ui.bv6_button.isChecked() else "off")) 

    def sv1_change(self):
        self._logger.insert_text("sv1 {}\n".format("on" if self.ui.sv1_button.isChecked() else "off")) 
    def sv2_change(self):
        self._logger.insert_text("sv2 {}\n".format("on" if self.ui.sv2_button.isChecked() else "off")) 

    def pu1_change(self):
        self._logger.insert_text("pu1 {}\n".format("on" if self.ui.pu1_button.isChecked() else "off")) 
    def pu2_change(self):
        self._logger.insert_text("pu2 {}\n".format("on" if self.ui.pu2_button.isChecked() else "off"))  
    def pu3_change(self):
        self._logger.insert_text("pu3 {}\n".format("on" if self.ui.pu3_button.isChecked() else "off"))  