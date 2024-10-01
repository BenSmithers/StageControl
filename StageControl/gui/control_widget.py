from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget
import sys 
import os 

from StageControl.ELLxControl import ELLxConnection
from StageControl.LEDControl import LEDBoard
from controlgui import Ui_Widget as gui 

from datetime import datetime 

from emailer import send_alert

from warn_widg import WarnWidget, HelpWidget

class ControlWidget(QtWidgets.QWidget):
    def __init__(self, parent:QWidget, fake=False):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)

        self.ui.goWaveBut.clicked.connect(self.go_wavelen)
        self.ui.goPosBut.clicked.connect(self.go_pos)
        self.ui.adc_spin.valueChanged.connect(self.set_adc)
        self.ui.rate_combo.currentIndexChanged.connect(self.set_freq)
        self.ui.waveCombo.currentIndexChanged.connect(self.wave_combo_change)
        self.ui.test_email.clicked.connect(self.test_email)

        self._logfile = os.path.join(os.path.dirname(__file__), "data","command.log")

        self._led_locations = [
            2*i for i in range(7)
        ]
        self._led_locations.append(1)
        self._led_locations.append(7)

        failure = False 
        try:
            self._conn = ELLxConnection("", fake=fake)
        except Exception as e:
            self.dialog = WarnWidget(parent=self,message="Critical Error! {}".format(e))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.help)
            self.dialog.exec_() 
            
            failure = True 

        try:
            self._board = LEDBoard("", fake=fake)
            self._board.enable()

            self._button_timer =  QtCore.QTimer(self)
            self._button_timer.timeout.connect(self._enable_button)
        except Exception as e:
            self.dialog = WarnWidget(parent=self,message="Critical Error! {}".format(e))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.help)
            self.dialog.exec_() 
            failure = True 

        if failure:
            sys.exit(1)    
        self.insert_text("Initialized GUI\n")

    def insert_text(self, msg):
        now = datetime.now()
        data = open(self._logfile, 'a+')
        data.write("{} : {}".format(now, msg))
        data.close()
        self.ui.textBrowser.insertPlainText("{} : {}".format(now, msg))


    def help(self):
        self.dialog = HelpWidget(parent=self,message="For help, please contact the expert on shift")
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.ui.buttonBox.helpRequested.connect(self.help)
        self.dialog.exec_() 

    def _enable_button(self):
        self._button_timer.stop()
        self.ui.test_email.setEnabled(True)
    def test_email(self):
        send_alert("This is just a test, and you received it!", "Success!")
        self.ui.test_email.setEnabled(False)
        self._button_timer.start(10000)

    def set_freq(self):
        if self.ui.rate_combo.currentIndex()==0:
            msg=self._board.set_slow_rate()
        else:
            msg=self._board.set_fast_rate()
        self.insert_text(msg)

    def set_adc(self):
        new_value = self.ui.adc_spin.value()
        msg= self._board.set_adc(new_value)
        self.insert_text(msg)

    def wave_combo_change(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]
        self.ui.positionSpin.setValue(position)
    def go_wavelen(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]

        msg=self._board.activate_led(index_no+1)
        self.insert_text(msg)
        self.set_position(position) 
        

    def go_pos(self):
        position = self.ui.positionSpin.value()
        self.set_position(position)

    def set_position(self, position):
        self.ui.positionSpin.setValue(position)

        packet = self._conn.move_absolute(position)

        self.insert_text(packet["call"].decode())
        self.insert_text(packet["response"].decode() +"\n")
        data = packet["data"]
        if "PO" in packet["response"].decode():
            self.ui.positionLbl.setText("{:.4f} mm".format(data))
        else:
            self.insert_text("Unexpected response: \n")
            self.insert_text("    {}\n".format(data))