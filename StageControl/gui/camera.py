
from cameragui import Ui_Widget as gui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from PyQt5.QtCore import QObject

class Camera(QtWidgets.QWidget):

    shoot_signal = pyqtSignal()
    iso_signal = pyqtSignal(int)
    aperture_signal = pyqtSignal(int)
    shutter_signal = pyqtSignal(int)

    def __init__(self, parent:QWidget, logger):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = gui()
        self.ui.setupUi(self)
        self._logger = logger

        self.ui.takepic.clicked.connect(self.take_picture)
        self.ui.isocombo.currentIndexChanged.connect(self.update_iso)
        self.ui.aperturecombo.currentIndexChanged.connect(self.update_aperture)
        self.ui.shuttercombo.currentIndexChanged.connect(self.update_shutter)
    def update_shutter(self):
        self.shutter_signal.emit(self.ui.shuttercombo.currentIndex())
    def update_aperture(self):
        self.aperture_signal.emit(self.ui.aperturecombo.currentIndex()) 
    def update_iso(self):
        self.iso_signal.emit(self.ui.isocombo.currentIndex()) 
    def take_picture(self):
        self.shoot_signal.emit()         
    
    @pyqtSlot()
    def update_images(self):
        pass 

class CameraWorker(QObject):
    pictureTaken = pyqtSignal()

    @pyqtSlot(int)
    def update_shutter(self, index:int):
        pass 
    @pyqtSlot(int)
    def update_iso(self, index:int):
        pass 
    @pyqtSlot(int)
    def update_aperture(self, index:int):
        pass 
    @pyqtSlot()
    def take_picture(self):
        pass 