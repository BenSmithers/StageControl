from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget

from StageControl.ELLxControl import ELLxConnection
from StageControl.LEDControl import LEDBoard
from controlgui import Ui_Widget as gui 

from emailer import send_alert

class ControlWidget(QtWidgets.QWidget):
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

        self._led_locations = [
            2*i for i in range(7)
        ]
        self._led_locations.append(1)
        self._led_locations.append(7)

        self._conn = ELLxConnection("", fake=True)
        self._board = LEDBoard("", fake=True)
        self._board.enable()

        self._button_timer =  QtCore.QTimer(self)
        self._button_timer.timeout.connect(self._enable_button)

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
        self.ui.textBrowser.insertPlainText(msg)

    def set_adc(self):
        new_value = self.ui.adc_spin.value()
        msg= self._board.set_adc(new_value)
        self.ui.textBrowser.insertPlainText(msg)

    def wave_combo_change(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]
        self.ui.positionSpin.setValue(position)
    def go_wavelen(self):
        index_no = self.ui.waveCombo.currentIndex()
        position = self._led_locations[index_no]

        msg=self._board.activate_led(index_no+1)
        self.ui.textBrowser.insertPlainText(msg)
        self.set_position(position) 
        

    def go_pos(self):
        position = self.ui.positionSpin.value()
        self.set_position(position)

    def set_position(self, position):
        self.ui.positionSpin.setValue(position)

        packet = self._conn.move_absolute(position)

        self.ui.textBrowser.insertPlainText(packet["call"].decode())
        self.ui.textBrowser.insertPlainText(packet["response"].decode() +"\n")
        data = packet["data"]
        if "PO" in packet["response"].decode():
            self.ui.positionLbl.setText("{:.4f} mm".format(data))
        else:
            self.ui.textBrowser.insertPlainText("Unexpected response: \n")
            self.ui.textBrowser.insertPlainText("    {}\n".format(data))