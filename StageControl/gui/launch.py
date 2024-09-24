from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore
import sys 
from form import Ui_MainWindow as gui


from StageControl import message
from StageControl.utils import Status
from StageControl.ELLxControl import ELLxConnection

# self.parent.scene.get_system(hid)
class main_window(QMainWindow):
    def __init__(self,parent=None):
        QWidget.__init__(self, parent)

        self.ui = gui()
        self.ui.setupUi(self)

        self.ui.pushButton_3.clicked.connect(self.insert_text)

    def keyPressEvent(self, e):
        if e.key()==Qt.EnterKeyType.EnterKeyReturn or e.key()==16777220:
            self.insert_text()

    def insert_text(self):
        what = self.ui.lineEdit.text()
        if what=="":
            return 
        self.ui.lineEdit.clear()
        self.ui.scrollArea.insertPlainText(what + "\n")

    def move_absolute(self):
        pass

app = QApplication(sys.argv)
app_instance = main_window()

if __name__=="__main__":
    # make sure the base saves folder exists 
    app_instance.show()
    sys.exit(app.exec_())

