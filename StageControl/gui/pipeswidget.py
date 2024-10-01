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
    def __init__(self, parent:QWidget,  logger:QtWidgets.QTextBrowser):
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
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)

        self.alarm_timer = QtCore.QTimer(self)
        self.alarm_timer.timeout.connect(self.flash)

        self._fake_chamber = 0
        self._fake_open_tank = 0
        self.update()

        self._flash_red = True
        self._alarm = np.array([False, False, False, False])

        sound_file = os.path.join(os.path.dirname(__file__), "data","alarm.mp3")

        self._alert_thrown = False 

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


        flows = flows.astype(int)*90 + 5 
        pressures = 20 + np.random.randn(4)*3
        scales = np.array([30, 5, -5, -10])
        if not self.ui.sv1_button.isChecked():
            pressures*=0
            scales*=0
        if full:
            pressures[0] *= 20

        pressures = pressures + scales

        temperatures = np.zeros(6)

        return pressures, flows

    def update(self):

        
        pressures, flows = self._generate_testdata()

        self.ui.flow1.setValue(flows[0])
        self.ui.flow2.setValue(flows[1])
        self.ui.flow3.setValue(flows[2])
        self.ui.flow4.setValue(flows[3])
        self.ui.flow5.setValue(flows[4])



        self._alarm = pressures>60

        self.ui.lcdNumber.setStyleSheet

        self.ui.lcdNumber.setText("{:.2f}".format(pressures[0]))
        self.ui.lcdNumber_4.setText("{:.2f}".format(pressures[1]))
        self.ui.lcdNumber_3.setText("{:.2f}".format(pressures[2]))
        self.ui.lcdNumber_2.setText("{:.2f}".format(pressures[3]))

        self.timer.start(2500)

        if any(self._alarm):
            if self._alert_thrown:
                pass 
            else:
                self._alert_thrown = True 
                message = "Warning! The water pressure is dangerously high!"
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
        self._logger.insertPlainText("bv1 {}\n".format("on" if self.ui.bv1_button.isChecked() else "off")) 
    def bv2_change(self):
        self._logger.insertPlainText("bv2 {}\n".format("on" if self.ui.bv2_button.isChecked() else "off")) 
    def bv3_change(self):
        self._logger.insertPlainText("bv3 {}\n".format("on" if self.ui.bv3_button.isChecked() else "off")) 
    def bv4_change(self):
        self._logger.insertPlainText("bv4 {}\n".format("on" if self.ui.bv4_button.isChecked() else "off")) 
    def bv5_change(self):
        self._logger.insertPlainText("bv5 {}\n".format("on" if self.ui.bv5_button.isChecked() else "off")) 
    def bv6_change(self):
        self._logger.insertPlainText("bv6 {}\n".format("on" if self.ui.bv6_button.isChecked() else "off")) 

    def sv1_change(self):
        self._logger.insertPlainText("sv1 {}\n".format("on" if self.ui.sv1_button.isChecked() else "off")) 
    def sv2_change(self):
        self._logger.insertPlainText("sv2 {}\n".format("on" if self.ui.sv2_button.isChecked() else "off")) 

    def pu1_change(self):
        self._logger.insertPlainText("pu1 {}\n".format("on" if self.ui.pu1_button.isChecked() else "off")) 
    def pu2_change(self):
        self._logger.insertPlainText("pu2 {}\n".format("on" if self.ui.pu2_button.isChecked() else "off"))  
    def pu3_change(self):
        self._logger.insertPlainText("pu3 {}\n".format("on" if self.ui.pu3_button.isChecked() else "off"))  