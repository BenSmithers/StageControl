
from cameragui import Ui_Widget as gui
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtCore import QObject

from enum import Enum
import os 

ISOMIN = 24
ISOMAX = 75
SHUTTER = 19


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
        self.ui.camera1.setPixmap(QtGui.QPixmap("./photo_camera_0.jpg"))
        self.ui.camera2.setPixmap(QtGui.QPixmap("./photo_camera_1.jpg"))

class CameraWorker(QObject):
    pictureTaken = pyqtSignal()
    message_signal = pyqtSignal(str)    

    def __init__(self):
        self._camera1 = "172.29.134.51"
        self._camera2 = "172.29.134.51"

        self._last_iso = 0 # 800?
        # 0 is 800! 
        # 3 is 100, it's weird and opposite 

    def configure(self, camera, setting, option):
        os.system("curl --request GET --url 'http://{}:8080/gopro/camera/setting?setting={}&option={}'".format(camera,setting, option))  

    @pyqtSlot(int)
    def update_shutter(self, index:int):
        self.message_signal.emit("Updating Shutter")
        self.configure(self._camera1, SHUTTER, index) 
        self.configure(self._camera2, SHUTTER, index)

    @pyqtSlot(int)
    def update_iso(self, index:int):
        self.message_signal.emit("Updating ISO")
        return 
        if index < self._last_iso:
            # going to a higher iso
            # update max first and then min 
            self.configure(self._camera1, ISOMAX, index)
            self.configure(self._camera1, ISOMIN, index)
            
            self.configure(self._camera2, ISOMAX, index)
            self.configure(self._camera2, ISOMIN, index)
        else:
            # drop the minimum then the maximum
            self.configure(self._camera1, ISOMIN, index)
            self.configure(self._camera1, ISOMAX, index)
            
            self.configure(self._camera2, ISOMIN, index)
            self.configure(self._camera2, ISOMAX, index) 
        self._last_iso = index  
    @pyqtSlot(int)
    def update_aperture(self, index:int):
        self.message_signal.emit("Updating Aperture")
        return 
    @pyqtSlot()
    def take_picture(self):
        from takeimage import entrypoint
        self.message_signal.emit("Taking Camera 1 image")
        entrypoint(0)
        self.message_signal.emit("Taking Camera 2 image")
        entrypoint(1) 
        self.pictureTaken.emit()
        