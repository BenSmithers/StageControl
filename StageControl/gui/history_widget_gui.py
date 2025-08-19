from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(487, 381)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cbox = QtWidgets.QPushButton(Form)
        self.cbox.setText("Update Plot")
        self.lock = QtWidgets.QCheckBox(Form)
        self.lock.setText("Auto-Zoom?")
        self.n_hours = QtWidgets.QSpinBox(Form)
        self.n_hours.setMinimum(1)
        self.n_hours.setMaximum(24)
        self.n_hours.setValue(8)
        self.n_hours.setToolTip("Number of Hours to Plot")


        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, Form)

        self.verticalLayout.addWidget(self.canvas)
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.cbox)
        self.verticalLayout.addWidget(self.lock)
        self.verticalLayout.addWidget(self.n_hours)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
