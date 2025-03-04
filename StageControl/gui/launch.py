from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog, QMessageBox
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot, QThreadPool, pyqtSignal, QThread, QObject

import sys 
import pexpect
from mainwindow import Ui_MainWindow as gui
from StageControl.gui.raspberry import PiConnect
from warn_widg import WarnWidget
from camera import CameraWorker
import os 
import time 

# self.parent.scene.get_system(hid)
from StageControl.ELLxControl import ELLxConnection
from StageControl.LEDControl import LEDBoard
from daq import DAQWorker

class USBWorker(QObject):
    ELLxSignal = pyqtSignal(dict)
    StatusSignal = pyqtSignal(str)
    led_changed_signal = pyqtSignal()
    adc_changed_signal = pyqtSignal()
    def __init__(self, fake):
        super(QObject, self).__init__()
        from constants import STAGE_USB, LED_BOARD_USB

        self._stage_path = STAGE_USB
        self._led_path = LED_BOARD_USB
        self._fake = fake 

    @pyqtSlot()
    def initialize(self):
        self._conn = ELLxConnection(self._stage_path, fake=fake)
        self._conn.go_home()
        self._board = LEDBoard(self._led_path, fake=fake)
        self._board.enable()
        self._board.set_int_trigger()
        self._board.set_fast_rate()
        self._board.set_adc(900) 
        self.StatusSignal.emit("Initialized USB Connections")


    @pyqtSlot(bool)
    def set_freq(self, is_slow):
        if is_slow:
            msg=self._board.set_slow_rate()
        else:
            msg=self._board.set_fast_rate()
        self.StatusSignal.emit(msg)
    
    @pyqtSlot(int)
    def set_adc(self, new_value):
        msg=self._board.set_adc(int(new_value))
        self.StatusSignal.emit(msg)
        self.adc_changed_signal.emit()

    @pyqtSlot(int)
    def activate_led(self, led_no):
        msg=self._board.activate_led(led_no)
        self.StatusSignal.emit(msg)
        self.led_changed_signal.emit()

    @pyqtSlot()
    def disable_board(self):
        self._board.disable()
        self.StatusSignal.emit("LED - L0\n")
        self.StatusSignal.emit("LED - D\n")


    @pyqtSlot(float)
    def move_absolute(self, position):
#        self._conn.go_home()
#        time.sleep(1)
        packet = self._conn.move_absolute(position)
        self.ELLxSignal.emit(packet)


class main_window(QMainWindow):
    """
        This handles the main gui and makes some widgets that go into it

        A key part of this is the thread manager, which spawns a sub-thread used to manage the SSH connection to the raspberry pi. 
        This needs to be here, in the QMainWindow instance, for weird Qt reasons. 

        No memory is directly shared between this gui window and the sub-thread. 
        Instead, a slot-signal interface is used for communications! 

    """
    initialize = pyqtSignal()
    initialize_usb = pyqtSignal()
    killConnection = pyqtSignal()

    reinitialize = pyqtSignal()
    def __init__(self,parent=None, fake=False):
        QWidget.__init__(self, parent)

        self.ui = gui()
        self.ui.setupUi(self, fake=fake)

        # setup for Raspberry Pi management 
        self.thread_man = QThread(self)
        self.thread_man.start()
        self.setup_thread()
        
        # setup for USB management
        self.thread_man_2 = QThread(self)
        self.thread_man_2.start()
        self.setup_usb_thread(fake)

        # setup for camera management 
        self.camera_threadman = QThread()
        self.camera_threadman.start()
        self.init_cameras()

        self.daq_threadman = QThread()
        self.daq_threadman.start()
        self.init_daq()

        self.setWindowTitle("WCTE Water Control System")
        self.ui.filepathEdit.setText("/home/watermon/software/PicoCode/data/{}".format(self.ui.control_widget._write_to))
        self.ui.filepathEdit.doubleClicked.connect(self.declick)
        self.ui.filepathEdit.clicked.connect(self.declick)
        
    def init_daq(self):
        try:
            self.daq_worker = DAQWorker()
            self.daq_worker.moveToThread(self.daq_threadman)
            self.daq_worker.data_recieved.connect(self.ui.control_widget.write_data)
            self.ui.control_widget.done_signal.connect(self.daq_worker.measure)
            self.ui.control_widget.start_signal.connect(self.daq_worker.start_data_taking)
            self.ui.control_widget.stop_signal.connect(self.daq_worker.stop_data_taking)
            self.daq_worker.change_wavelength.connect(self.ui.control_widget.change_wavelength)
            
        except Exception as e:
            self.dialog = WarnWidget(parent=self, message="Critical Error {}".format(e))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.ui.control_widget.help)
            self.dialog.exec_()  
            sys.exit(1)

    def init_cameras(self):
        try:
            self.camera_worker = CameraWorker()
            self.camera_worker.moveToThread(self.camera_threadman)
            self.camera_worker.pictureTaken.connect(self.ui.camera.update_images)
            self.camera_worker.message_signal.connect(self.thread_message)
            self.ui.camera.iso_signal.connect(self.camera_worker.update_iso)
            self.ui.camera.shutter_signal.connect(self.camera_worker.update_shutter)
            self.ui.camera.aperture_signal.connect(self.camera_worker.update_aperture)
            self.ui.camera.shoot_signal.connect(self.camera_worker.take_picture)
        except Exception as e:
            self.dialog = WarnWidget(parent=self, message="Critical Error {}".format(e))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.ui.control_widget.help)
            self.dialog.exec_()  
            sys.exit(1)

    def setup_usb_thread(self, fake):
        try:
            self.usb_worker_thread = USBWorker(fake)
            self.usb_worker_thread.moveToThread(self.thread_man_2)

            # connect the thread's signals to the control widget slots 
            
            self.usb_worker_thread.ELLxSignal.connect(self.ui.control_widget.process_response)
            self.usb_worker_thread.StatusSignal.connect(self.ui.control_widget.insert_text)

            # connect the signals from the control widget to the USB worker thread 
            self.ui.control_widget.led_signal.connect(self.usb_worker_thread.activate_led)
            self.ui.control_widget.adc_signal.connect(self.usb_worker_thread.set_adc)
            self.ui.control_widget.freq_signal.connect(self.usb_worker_thread.set_freq)
            self.ui.control_widget.move_signal.connect(self.usb_worker_thread.move_absolute)
            
            self.usb_worker_thread.adc_changed_signal.connect(self.ui.control_widget.adc_ready)
            self.usb_worker_thread.led_changed_signal.connect(self.ui.control_widget.led_ready)

            self.ui.control_widget.ui.disable_led.clicked.connect(self.usb_worker_thread.disable_board)
            self.initialize_usb.connect(self.usb_worker_thread.initialize)
            self.initialize_usb.emit()
        except Exception as e:
            self.dialog = WarnWidget(parent=self,message="Critical Error! {}".format(e))
            self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.dialog.ui.buttonBox.helpRequested.connect(self.ui.control_widget.help)
            self.dialog.exec_()  
            sys.exit(1)
   

    def setup_thread(self):
        """
            Here we actually spawn the SSH worker and connect all of the signals and slots 
        """
        try:
            self.worker_thread = PiConnect()
            self.worker_thread.moveToThread(self.thread_man)
            # connections 
            self.initialize.connect(self.worker_thread.initialize)
            self.ui.pipes.update_plot_signal.connect(self.ui.history.update_plots)
            self.worker_thread.data_signal.connect(self.ui.pipes.data_received)
            self.ui.pipes.pump_signal.connect(self.worker_thread.pump)
            self.ui.pipes.bv_signal.connect(self.worker_thread.bv)
            self.ui.pipes.sv_signal.connect(self.worker_thread.sv)
            self.ui.pipes.interrupt_signal.connect(self.worker_thread.interrupt)
            self.killConnection.connect(self.worker_thread.finish)
            
            # first, we connect a signal here to the initializer 
            self.reinitialize.connect(self.worker_thread.initialize)
            # and a button to a function here
            # the button first emits the re-initializer signal
            #    and then it instructs the pipes manager to send signals to turn on/off the appropriate valves and pumps
            self.ui.pipes.ui.relaunch_button.clicked.connect(self.functional_reinit)

            # used for status updates
            self.worker_thread.message_signal.connect(self.thread_message)

            # tell the SSH connection to open up
            self.initialize.emit()

        except pexpect.ExceptionPexpect as e:
            self.ui.pipes.panic("{}".format(e) + " for water monitoring", heat=False, skip_email=True)
        except Exception as e:
            self.ui.pipes.panic("{}".format(e), heat=False, skip_email=True) 

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm Exit',
                                     'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:

            self.killConnection.emit() # allow the PiConnect object to clean itself up
            # tell it to quit and wait for it to quit 
            time.sleep(2.5)
            self.thread_man.quit()
            self.thread_man.wait()
            # tell the _other_ one to quit, and then wait for it to quit
            self.thread_man_2.quit()
            self.thread_man_2.wait()

            event.accept()
        else:
            event.ignore()
            
    def functional_reinit(self):
        self.reinitialize.emit()
        self.ui.pipes.refresh()
        
    def declick(self):
        print("Double click")
        pathto = QFileDialog.getOpenFileName(None, 'Open File',"/home/watermon/software/PicoCode/data/", 'dat (*.dat)')[0]
        if pathto is not None:
            if pathto!="":
                self.ui.filepathEdit.setText(pathto)
                self.ui.plot_widg.update_filepath(pathto)

    def keyPressEvent(self, e):
        if e.key()==Qt.EnterKeyType.EnterKeyReturn or e.key()==16777220:
            self.insert_text()

    def insert_text(self):
        what = self.ui.control_widget.ui.lineEdit.text()
        if what=="":
            return 
        self.ui.control_widget.ui.lineEdit.clear()
        self.ui.control_widget.insert_text(what + "\n")

    @pyqtSlot(str)
    def thread_message(self, message):
        self.ui.control_widget.insert_text(message)


import sys 
fake = False
if len(sys.argv)>1:
    fake = sys.argv[1]=="fake"
app = QApplication(sys.argv)
app_instance = main_window(fake=fake)

if __name__=="__main__":
    # make sure the base saves folder exists 
    app_instance.show()
    sys.exit(app.exec_())

