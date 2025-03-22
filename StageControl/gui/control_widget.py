from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import sys 
import os 
from time import time 
from controlgui import Ui_Widget as gui 

from datetime import datetime 
from emailer import get_current_addresses, send_alert_to, get_time_to_next_shift
from warn_widg import WarnWidget, HelpWidget
from glob import glob

class ControlWidget(QtWidgets.QWidget):
    led_signal = pyqtSignal(int)
    adc_signal = pyqtSignal(int)
    freq_signal = pyqtSignal(bool)
    move_signal = pyqtSignal(float)
    
    # called when it's done doing things
    done_signal = pyqtSignal()
    start_signal = pyqtSignal(bool)
    stop_signal = pyqtSignal()
    start_refil = pyqtSignal(int, int)
    start_circulation = pyqtSignal(int, int)


    def __init__(self, parent:QWidget):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)
        self.ui.run_numb_line.setValue(len(glob("./picodat/*")))
        self.ui.goWaveBut.clicked.connect(self.go_wavelen)
        self.ui.goPosBut.clicked.connect(self.go_pos)
#        self.ui.adc_spin.valueChanged.connect(self.set_adc)
        self.ui.adc_lbl.clicked.connect(self.set_adc)
        self.ui.rate_combo.currentIndexChanged.connect(self.set_freq)
        self.ui.waveCombo.currentIndexChanged.connect(self.wave_combo_change)
        self.ui.waterlabel_lbl.clicked.connect(self.write_new_name)
        self.ui.test_email.clicked.connect(self.test_email)
        self.ui.start_data_but.clicked.connect(self.run_button)
        self.ui.auto_refill.clicked.connect(self.auto_refill_toggle)
        self.ui.circulate.clicked.connect(self.auto_refill_toggle)
        
        self.start_mode = True 

        self._logfile = os.path.join(os.path.dirname(__file__), "data","command.log")

        self._led_locations = [
            8.5*i for i in range(7)
        ]
        self._led_locations = [x -1.0 for x  in self._led_locations]
        self._led_locations.append(8.74)
        self._led_locations.append(51.24)
        self._led_locations[0] = 0.02
        self._led_locations[1] = 7.57
        self._adcs= [
                720,
                840,
                715,
                610,
                778,
                800
                ]

        self._button_timer =  QtCore.QTimer(self)
        self._button_timer.timeout.connect(self._enable_button)

        self._running = False

        self.insert_text("Initialized GUI\n")

        self.update_emails()
        self.ui.shift_update.clicked.connect(self.update_emails)

        self._dataclock = QtCore.QTimer(self) 
        self._dataclock.timeout.connect(self.done_signal)

        tts = get_time_to_next_shift()
        self._updater_clock = QtCore.QTimer(self)
        self._updater_clock.timeout.connect(self.auto_update)
        #if tts>0:
        #self._updater_clock.start(int(tts*1000))
        print("{} hours until next shift".format(tts/3600))

        self._outfilename = os.path.join(os.path.dirname(__file__),"..","..","..","PicoCode","outfilename.txt")
        self._write_to = ""
        if os.path.exists(self._outfilename):
            _obj = open(self._outfilename,'r')
            text = _obj.readline()
            kind = text.split("_")[1]
            try:
                self.ui.waterlabel.setCurrentIndex(self.ui.indexdict[kind])
            except Exception as e:
                self.ui.waterlabel.setCurrentIndex(self.ui.indexdict[ " ".join([text.split("_")[1], text.split("_")[2]])])
            _obj.close()
        else:
            self.ui.waterlabel.setCurrentIndex(4) 

        self._write_to = os.path.join("picodat", "picodat_{}_{}_{}adc_{}.dat".format(
            self.ui.waterlabel.currentText(),
            self.ui.waveCombo.currentText().split(" ")[0],
            self.ui.adc_spin.value(),
            "mHz" if self.ui.rate_combo.currentIndex()==1 else "kHz"
        ))

        self._led_done = False 
        self._adc_done = False
        self._stage_done = False 
        self.auto_refill_toggle()

    @pyqtSlot()
    def unlock(self):
        self.ui.goPosBut.setEnabled(True)
        self.ui.goWaveBut.setEnabled(True) 
        self.ui.adc_lbl.setEnabled(True)
        self.ui.start_data_but.setEnabled(True)

    def auto_refill_toggle(self):
        self.ui.start_data_but.setEnabled(True)
        auto_refill = self.ui.auto_refill.isChecked()
        circulate = self.ui.circulate.isChecked()
        if auto_refill:
            self.ui.circulate.setEnabled(False)
            self.ui.refill_freq_lbl.setText("Refill Period [min]:")
            self.ui.refill_what_lbl.setText("Refill With:")
            self.ui.refill_freq_spin.setMaximum(240)
            self.ui.refill_freq_spin.setMinimum(30)
            self.ui.refill_freq_spin.setValue(90)
        else:
            self.ui.circulate.setEnabled(True)
        if circulate:
            self.ui.refill_freq_lbl.setText("Toggle Freq [min]:")
            self.ui.refill_what_lbl.setText("Circulate With:")
            self.ui.refill_freq_spin.setMaximum(10)
            self.ui.refill_freq_spin.setMinimum(2)
            self.ui.refill_freq_spin.setValue(5)
            self.ui.auto_refill.setEnabled(False)
        else:
            self.ui.auto_refill.setEnabled(True)
        if auto_refill and circulate:
            self.ui.auto_refill.setEnabled(True)
            self.ui.auto_refill.setEnabled(True)
            self.ui.start_data_but.setEnabled(False) # this should be unreachable...


    def run_button(self):
        if self.start_mode:
            striping = self.ui.rotate_wave.isChecked()
            if striping:
                wave = "various"
                adc = "various"
            else:
                wave = self.ui.waveCombo.currentText().split(" ")[0] 
                adc =self.ui.adc_spin.value()
                
            self._write_to = os.path.join("picodat", "picodat_run{}_{}_{}_{}adc_{}.dat".format(
                self.ui.run_numb_line.value(),
                self.ui.waterlabel.currentText(),
                wave,
                adc,
                "mHz" if self.ui.rate_combo.currentIndex()==1 else "kHz"
            ))

            refill_period = self.ui.refill_freq_spin.value()
            auto_refill = self.ui.auto_refill.isChecked()
            circulate = self.ui.circulate.isChecked()
            if auto_refill and circulate:
                print("Invalid configuration! Aborting")
                return 
            selected = self.ui.refill_what_combo.currentIndex()
            """
                0 - tank 
                1 - supply 
                2 - osmosis
            """
            self.start_signal.emit(striping)
            if auto_refill:
                self.start_refil.emit(selected, refill_period)
            if circulate:
                self.start_circulation.emit(selected, refill_period*60)
            
            self.ui.start_data_but.setText("Stop Run")
            
            self.ui.adc_spin.setEnabled(False)
            self.ui.waveCombo.setEnabled(False)
            self.ui.rotate_wave.setEnabled(False)
            self.ui.positionSpin.setEnabled(False)
            self.ui.goPosBut.setEnabled(False)
            self.ui.goWaveBut.setEnabled(False)
            self.ui.refill_what_combo.setEnabled(False)
            self.ui.refill_freq_spin.setEnabled(False)
            self.ui.run_numb_line.setEnabled(False)
            self.ui.auto_refill.setEnabled(False)
            self.ui.rotate_wave.setEnabled(False)
            #self.ui.rate_combo.setEnabled(False)
            self._dataclock.start(int(1.5*60*1000))
            self._running = True 
        else:
            self.stop_signal.emit()
            self._dataclock.stop()
            self.ui.start_data_but.setText("Start Run")
            self.ui.run_numb_line.setValue(self.ui.run_numb_line.value() + 1)
            self.ui.auto_refill.setEnabled(True)
            self.ui.rotate_wave.setEnabled(True)
            self.ui.adc_spin.setEnabled(True)
            self.ui.waveCombo.setEnabled(True)
            self.ui.rotate_wave.setEnabled(True)
            self.ui.positionSpin.setEnabled(True)
            self.ui.goPosBut.setEnabled(True)
            self.ui.goWaveBut.setEnabled(True)
            self.ui.refill_what_combo.setEnabled(True)
            self.ui.refill_freq_spin.setEnabled(True)
            self.ui.run_numb_line.setEnabled(True)
            #self.ui.rate_combo.setEnabled(True)
            self._running = False 
        self.start_mode = not self.start_mode
            
    def write_new_name(self):
        """
            Writes a new out-file file name
        """
        
        self._write_to = "picodat_{}_{}_{}adc_{}.dat".format(
            self.ui.waterlabel.currentText().replace(" ", "_"),
            self.ui.waveCombo.currentText().split(" ")[0],
            self.ui.adc_spin.value(),
            "mHz" if self.ui.rate_combo.currentIndex()==1 else "kHz"
        )

        _obj = open(self._outfilename,'wt')
        _obj.write(self._write_to)
        _obj.close()
        self.insert_text("Updated PicoCode savefile: {}".format(self._write_to))



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

    @pyqtSlot(int, int, int, int, int, int)
    def write_data(self, wavelen, trig, mon, rec, mon_dark, rec_dark):
        write_header = not os.path.exists(self._write_to)
        
        _obj = open(self._write_to, 'at')
        if write_header:
            _obj.write("#Time, trig, monitor, receiver, monitor_dark, receiver_dark, ADC, wave length\n")
        
        if self.ui.rotate_wave.isChecked():            
            _obj.write("{}, {},{},{}, {}, {}, {}, {}\n".format(time(), trig, mon, rec,mon_dark,rec_dark, self.ui.adc_spin.value(), wavelen, ))
        else:
            _obj.write("{}, {},{},{}, {}, {}, {}, {}\n".format(time(), trig, mon, rec,mon_dark, rec_dark, self.ui.adc_spin.value(), self.ui.waveCombo.currentIndex()))
        _obj.close()
    
    @pyqtSlot()
    def led_ready(self):
        self._led_done = True 
        self.checker()
    @pyqtSlot()
    def adc_ready(self):
        self._adc_done = True 
        self.checker()
    def checker(self):
        if self._led_done and self._adc_done and self._stage_done:
            if self._running:
                self.insert_text("Ready - taking data")
                self.done_signal.emit()

    @pyqtSlot(int)
    def change_wavelength(self, index_no):
        self._led_done = False 
        self._stage_done = False
        self._adc_done = False 

        self.ui.waveCombo.setCurrentIndex(index_no)
        # LOOK UP ADC VALUE 
#        new_adc = 1
        new_adc = self._adcs[index_no]
        self.ui.adc_spin.setValue(new_adc)
        self.set_adc()
        # we need to emit the signals to tell the USB worker thread to move stuff
        self.go_wavelen()
        
        # emit some signals

    @pyqtSlot(dict)
    def process_response(self, packet):
        self.insert_text(packet["call"].decode())
        self.insert_text(packet["response"].decode())
        if "\n" not in packet["response"].decode():
            self.insert_text("\n")
        data = packet["data"]
        if "PO" in packet["response"].decode():
            self.ui.positionLbl.setText("{:.4f} mm".format(data))
            self._stage_done = True 
            self.checker()
        elif "GS" in packet["response"].decode():
            self.insert_text("GS Status response: {}\n".format(data)) 

            position = self.ui.positionSpin.value()
            self.move_signal.emit(position)
            #self.dialog = WarnWidget(parent=self,message="Notice! Linear stage returned status: {}".format(data))
            #self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            #self.dialog.ui.buttonBox.helpRequested.connect(self.help)
            #self.dialog.exec_() 
        elif "IN" in packet["response"].decode():
            for entry in data:
                self.insert_text("Begin Info Response Dump\n")
                self.insert_text("    {}\n".format(entry))
        else:
            self.insert_text("Unexpected response: \n")
            self.insert_text("    {}\n".format(packet["response"]))
