from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import sys 
import os 

from controlgui import Ui_Widget as gui 

from datetime import datetime 
from emailer import get_current_addresses, send_alert_to, get_time_to_next_shift
from warn_widg import WarnWidget, HelpWidget


class ControlWidget(QtWidgets.QWidget):
    led_signal = pyqtSignal(int)
    adc_signal = pyqtSignal(int)
    freq_signal = pyqtSignal(bool)
    move_signal = pyqtSignal(float)
    
    def __init__(self, parent:QWidget):
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

        self._button_timer =  QtCore.QTimer(self)
        self._button_timer.timeout.connect(self._enable_button)


        self.insert_text("Initialized GUI\n")

        self.update_emails()
        self.ui.shift_update.clicked.connect(self.update_emails)

        tts = get_time_to_next_shift()
        self._updater_clock = QtCore.QTimer(self)
        self._updater_clock.timeout.connect(self.auto_update)
        self._updater_clock.start(int(tts*1000))
        print("{} hours until next shift".format(tts/3600))


    def send_alert(self, message, headline):
        if self.ui.shifter_one.text()!="":
            self.insert_text("Sending email to {}\n".format(self.ui.shifter_one.text()))
        if self.ui.shifter_two.text()!="":
            self.insert_text("Sending email to {}\n".format(self.ui.shifter_two.text()))
        send_alert_to([self.ui.shifter_one.text(), self.ui.shifter_two.text(), ], message, headline)

    def auto_update(self):
        self._updater_clock.stop()
        self.update_emails()
        self._updater_clock.start(int(8*3600*1000))

    def update_emails(self):
        shifter1, shifter2 = get_current_addresses()
        self.ui.shifter_one.setText(shifter1)
        self.ui.shifter_two.setText(shifter2)

    @pyqtSlot(str)
    def insert_text(self, msg):
        if "\n" not in msg:
            msg = msg +"\n"

        now = datetime.now()
        data = open(self._logfile, 'a+')
        data.write("{} : {}".format(now, msg))
        data.close()
        self.ui.textBrowser.insertPlainText("{} : {}".format(now, msg))
        self.ui.textBrowser.verticalScrollBar().setValue(self.ui.textBrowser.verticalScrollBar().maximumHeight())


    def help(self):
        self.dialog = HelpWidget(parent=self,message="For help, please contact the expert on shift")
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.ui.buttonBox.helpRequested.connect(self.help)
        self.dialog.exec_() 

    def _enable_button(self):
        self._button_timer.stop()
        self.ui.test_email.setEnabled(True)
    def test_email(self):
        self.send_alert("This is just a test, and you received it!", "Success!")
        self.ui.test_email.setEnabled(False)
        self._button_timer.start(10000)

    def set_freq(self):   
        self.freq_signal.emit(self.ui.rate_combo.currentIndex()==0)

    def set_adc(self):
        new_value = self.ui.adc_spin.value()
        self.adc_signal.emit(new_value)

    def wave_combo_change(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]
        self.ui.positionSpin.setValue(position)
    def go_wavelen(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]

        self.led_signal.emit(index_no+1)        
        self.set_position(position) 
        

    def go_pos(self):
        position = self.ui.positionSpin.value()
        self.set_position(position)

    def set_position(self, position):
        self.ui.positionSpin.setValue(position)
        self.move_signal.emit(position)

    @pyqtSlot(dict)
    def process_response(self, packet):
        self.insert_text(packet["call"].decode())
        self.insert_text(packet["response"].decode())
        if "\n" not in packet["response"].decode():
            self.insert_text("\n")
        data = packet["data"]
        if "PO" in packet["response"].decode():
            self.ui.positionLbl.setText("{:.4f} mm".format(data))
        elif "GS" in packet["response"].decode():
            self.insert_text("GS Status response: {}\n".format(data)) 

            self.dialog = WarnWidget(parent=self,message="Notice! Linear stage returned status: {}".format(data))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.help)
            self.dialog.exec_() 
        elif "IN" in packet["response"].decode():
            for entry in data:
                self.insert_text("Begin Info Response Dump\n")
                self.insert_text("    {}\n".format(entry))
        else:
            self.insert_text("Unexpected response: \n")
            self.insert_text("    {}\n".format(packet["response"]))