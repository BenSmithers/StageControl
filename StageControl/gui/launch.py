from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot, QThreadPool, pyqtSignal, QThread

import sys 
import pexpect
from mainwindow import Ui_MainWindow as gui
from StageControl import message
from StageControl.utils import Status
from StageControl.ELLxControl import ELLxConnection
from StageControl.gui.raspberry import PiConnect
import os 

# self.parent.scene.get_system(hid)
class main_window(QMainWindow):
    """
        This handles the main gui and makes some widgets that go into it

        A key part of this is the thread manager, which spawns a sub-thread used to manage the SSH connection to the raspberry pi. 
        This needs to be here, in the QMainWindow instance, for weird Qt reasons. 

        No memory is directly shared between this gui window and the sub-thread. 
        Instead, a slot-signal interface is used for communications! 

    """
    initialize = pyqtSignal()
    def __init__(self,parent=None, fake=False):
        QWidget.__init__(self, parent)

        self.ui = gui()
        self.ui.setupUi(self, fake=fake)

        # we create a thread manager and we start it up
        self.thread_man = QThread(self)
        self.thread_man.start()
        self.setup_thread()
        

        self.setWindowTitle("WCTE Water Control System")
        self.ui.filepathEdit.setText("/Users/bsmithers/software/PicoCode/ratio_data_osmosis.csv")
        self.ui.filepathEdit.doubleClicked.connect(self.declick)
        self.ui.filepathEdit.clicked.connect(self.declick)
        
    def setup_thread(self):
        """
            Here we actually spawn the SSH worker and connect all of the signals and slots 
        """
        try:
            self.worker_thread = PiConnect()
            self.worker_thread.moveToThread(self.thread_man)
            # connections 
            self.initialize.connect(self.worker_thread.initialize)
            self.worker_thread.data_signal.connect(self.ui.pipes.data_received)
            self.ui.pipes.pump_signal.connect(self.worker_thread.pump)
            self.ui.pipes.bv_signal.connect(self.worker_thread.bv)
            self.ui.pipes.sv_signal.connect(self.worker_thread.sv)

            # used for status updates
            self.worker_thread.message_siganl.connect(self.thread_message)

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
            if hasattr(self.worker_thread, 'finish'):
                self.worker_thread.finish()
            event.accept()
        else:
            event.ignore()
            
    def declick(self):
        print("Double click")
        pathto = QFileDialog.getOpenFileName(None, 'Open File',os.path.join(os.path.dirname(__file__), ".."), 'csv (*.csv)')[0]
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

    def move_absolute(self):
        pass

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

