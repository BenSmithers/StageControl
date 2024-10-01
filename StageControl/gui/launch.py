from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog, QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore
import sys 
from mainwindow import Ui_MainWindow as gui


from StageControl import message
from StageControl.utils import Status
from StageControl.ELLxControl import ELLxConnection
import os 

# self.parent.scene.get_system(hid)
class main_window(QMainWindow):
    def __init__(self,parent=None, fake=False):
        QWidget.__init__(self, parent)

        self.ui = gui()
        self.ui.setupUi(self, fake=fake)

        self.setWindowTitle("WCTE Water Control System")
        self.ui.filepathEdit.setText("/Users/bsmithers/software/PicoCode/ratio_data_osmosis.csv")
        self.ui.filepathEdit.doubleClicked.connect(self.declick)
        self.ui.filepathEdit.clicked.connect(self.declick)
        
    
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

