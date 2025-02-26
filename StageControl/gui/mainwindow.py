# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


from plot_widget import PlotsWidget 
from control_widget import ControlWidget
from pipeswidget import PipesWidget
from camera import Camera
from history_widget import HistoryWidget

class LineEdit(QtWidgets.QLineEdit):
    doubleClicked = QtCore.pyqtSignal()
    clicked = QtCore.pyqtSignal()

    def event(self, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
            self.doubleClicked.emit()
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.clicked.emit()
        return super().event(event)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, fake=False):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.controlTab = QtWidgets.QWidget()
        self.controlTab.setObjectName("controlTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.controlTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.control_widget = ControlWidget(self.controlTab)
        self.control_widget.setObjectName("controlinst")

        self.verticalLayout_2.addWidget(self.control_widget)
        self.tabWidget.addTab(self.controlTab, "")
        self.plotTab = QtWidgets.QWidget()
        self.plotTab.setObjectName("plotTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.plotTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")


        self.plot_widg = PlotsWidget(self.plotTab, self.control_widget)
        self.plot_widg.setObjectName("widget_inst")


        self.verticalLayout_3.addWidget(self.plot_widg)
        self.filepathEdit = LineEdit(self.plotTab)
        self.filepathEdit.setObjectName("filepathEdit")
        self.verticalLayout_3.addWidget(self.filepathEdit)
        self.tabWidget.addTab(self.plotTab, "")
        self.pipes = PipesWidget(self.centralwidget,self.control_widget, fake)
        self.tabWidget.addTab(self.pipes, "Pump Operations")
        self.history = HistoryWidget(self.centralwidget, self.control_widget)
        self.tabWidget.addTab(self.history, "History")

        self.camera = Camera(self.centralwidget, self.control_widget)
        self.tabWidget.addTab(self.camera, "Camera Control")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 37))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.controlTab), _translate("MainWindow", "Control"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.plotTab), _translate("MainWindow", "Plots"))
