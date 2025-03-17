# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Widget(object):
    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(800, 600)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.waveCombo = QtWidgets.QComboBox(Widget)
        self.waveCombo.setObjectName("waveCombo")

        self.waveCombo.addItem("450nm LED")
        self.waveCombo.addItem("410nm LED")
        self.waveCombo.addItem("365nm LED")
        self.waveCombo.addItem("295nm LED")
        self.waveCombo.addItem("278nm LED")
        self.waveCombo.addItem("255nm LED")
        self.waveCombo.addItem("235nm LED")
        self.waveCombo.addItem("Align 1")
        self.waveCombo.addItem("Align 2")


        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.waveCombo)
        self.positionSpin = QtWidgets.QDoubleSpinBox(Widget)
        self.positionSpin.setObjectName("positionSpin")
        self.positionSpin.setSingleStep(0.02)
        self.positionSpin.setMinimum(-1)
        self.positionSpin.setMaximum(52)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.positionSpin)
        self.goPosBut = QtWidgets.QPushButton(Widget)
        self.goPosBut.setObjectName("goPosBut")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.goPosBut)
        self.goWaveBut = QtWidgets.QPushButton(Widget)
        self.goWaveBut.setObjectName("goWaveBut")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.goWaveBut)

        self.adc_lbl = QtWidgets.QPushButton(Widget)
        self.adc_lbl.setObjectName("adc_lbl")
        self.adc_lbl.setText("Set ADC")
        self.adc_spin = QtWidgets.QSpinBox(Widget)
        self.adc_spin.setObjectName("adc_spin")
        self.adc_spin.setMinimum(0)
        self.adc_spin.setMaximum(1023)
        self.adc_spin.setValue(900)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.adc_lbl)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.adc_spin)

        self.rate_lbl = QtWidgets.QLabel(Widget)
        self.rate_lbl.setObjectName("rate_lbl")
        self.rate_lbl.setText("Flash Rate")
        self.rate_combo = QtWidgets.QComboBox(Widget)
        self.rate_combo.setObjectName("rate_combo")
        self.rate_combo.addItem("1.5kHz")
        self.rate_combo.addItem("8MHz")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.rate_lbl)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.rate_combo)



        self.label = QtWidgets.QLabel(Widget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label)
        self.positionLbl = QtWidgets.QLabel(Widget)
        self.positionLbl.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.positionLbl.setFrameShadow(QtWidgets.QFrame.Raised)
        self.positionLbl.setObjectName("positionLbl")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.positionLbl)

        self.waterlabel_lbl = QtWidgets.QPushButton(Widget)
        self.waterlabel_lbl.setText("Update Filename")
        self.waterlabel_lbl.setObjectName("waterlabel_lbl")
        self.waterlabel = QtWidgets.QComboBox(Widget)
        self.waterlabel.setObjectName("waterlabel")
        
        self.indexdict = {
            "Osmosis":0,
            "Supply Untreated":1,
            "Supply Filtered":2,
            "Return Untreated":3,
            "Return Filtered":4,
            "Air":5,
            "Other":4
        }

        self.waterlabel.addItem("Osmosis")
        self.waterlabel.addItem("Supply Untreated")
        self.waterlabel.addItem("Supply Filtered")
        self.waterlabel.addItem("Return Untreated")
        self.waterlabel.addItem("Return Filtered")
        self.waterlabel.addItem("Air")
        self.waterlabel.addItem("Other")
        
        #self.waterlabel.setStyleSheet("background-color:rgb(255,255,255)")

        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.waterlabel_lbl)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.waterlabel)

        self.disable_led = QtWidgets.QPushButton(Widget)
        self.disable_led.setObjectName("disable_led")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.disable_led)
        self.disable_led.setText("Disable LED")

        """
            - add horizontal line
            - add checkbox to "rotate wavelengths"
            - add Button for "START Run" that swaps to "STOP Run" when a run is going 
            - When a run is going it tells a thread to start taking data
                the thread takes data, then sets a timer for 20 seconds, then takes data again
                the thread sends a signal with the data whenever it takes it. The main thread appends that to a data file
                the thread can send a signal whenever a LED/ADC change is requested. The main thread keeps track; 
                    once both are done it sends a signal back to the data taker to take data again
        """
        
        self.hline = QtWidgets.QFrame(Widget)
        self.hline.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.hline.setFrameStyle(QtWidgets.QFrame.Shape.HLine)
        self.hline.setObjectName("Line")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.SpanningRole, self.hline)

        self.rotate_wave = QtWidgets.QCheckBox(Widget)
        self.rotate_wave.setObjectName("rotate_wave")
        self.rotate_wave.setText("Rotate Wavelengths?")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.rotate_wave)

        self.auto_refill = QtWidgets.QCheckBox(Widget)
        self.auto_refill.setObjectName("auto_refill")
        self.auto_refill.setText("Auto Refill?")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.auto_refill)

        self.gain_button = QtWidgets.QPushButton(Widget)
        self.gain_button.setObjectName("gain_button")
        self.gain_button.setText("Calibrate Threshold")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.gain_button)


        self.refill_freq_lbl = QtWidgets.QLabel(Widget)
        self.refill_freq_lbl.setObjectName("refill_freq_lbl")
        self.refill_freq_lbl.setText("Refill Period [min]:")
        self.refill_freq_spin = QtWidgets.QSpinBox(Widget)
        self.refill_freq_spin.setObjectName("refill_freq_spin")
        self.refill_freq_spin.setMaximum(240)
        self.refill_freq_spin.setMinimum(30)
        self.refill_freq_spin.setValue(120) # this must be updated based on the number of files in the data folder
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.refill_freq_lbl)
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.refill_freq_spin)

        self.refill_what_lbl = QtWidgets.QLabel(Widget)
        self.refill_what_lbl.setObjectName("refill_what_lbl")
        self.refill_what_lbl.setText("Refill With:")
        self.refill_what_combo = QtWidgets.QComboBox(Widget)
        self.refill_what_combo.setObjectName("refill_what_combo")
        self.refill_what_combo.addItem("Tank Water")
        self.refill_what_combo.addItem("Supply Water")
        self.refill_what_combo.addItem("RO Water")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.refill_what_lbl)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.refill_what_combo)

        self.run_numb_lbl = QtWidgets.QLabel(Widget)
        self.run_numb_lbl.setObjectName("run_numb_lbl")
        self.run_numb_lbl.setText("Run Number:")
        self.run_numb_line = QtWidgets.QSpinBox(Widget)
        self.run_numb_line.setObjectName("run_numb_line")
        self.run_numb_line.setMaximum(1000000)
        self.run_numb_line.setMinimum(0)
        self.run_numb_line.setValue(0) # this must be updated based on the number of files in the data folder
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.LabelRole, self.run_numb_lbl)
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.FieldRole, self.run_numb_line)

        self.start_data_but = QtWidgets.QPushButton(Widget)
        self.start_data_but.setObjectName("start_data_but")
        self.start_data_but.setText("Start Run")
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.FieldRole, self.start_data_but)

        bottom_start_index = 15

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(bottom_start_index,  QtWidgets.QFormLayout.FieldRole, spacerItem)

        self.shift_update = QtWidgets.QPushButton(Widget)
        self.shift_update.setObjectName("shift_update")
        self.shift_update.setText("Update Emails")
        self.formLayout.setWidget(bottom_start_index+1, QtWidgets.QFormLayout.FieldRole, self.shift_update)
        self.shift_two_lbl =QtWidgets.QLabel(Widget)
        self.shift_two_lbl.setObjectName("shift_two_lbl")
        self.shift_two_lbl.setText("Shifter Email:")
        self.shift_one_lbl =QtWidgets.QLabel(Widget)
        self.shift_one_lbl.setObjectName("shift_one_lbl")
        self.shift_one_lbl.setText("Shifter Email:")
        self.formLayout.setWidget(bottom_start_index+2,QtWidgets.QFormLayout.LabelRole, self.shift_one_lbl)
        self.formLayout.setWidget(bottom_start_index+3,QtWidgets.QFormLayout.LabelRole, self.shift_two_lbl)

        self.shifter_one = QtWidgets.QLineEdit(Widget)
        self.shifter_one.setObjectName("shifter_one")
        self.shifter_one.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.shifter_one.setMinimumSize(150,15)

        self.shifter_two = QtWidgets.QLineEdit(Widget)
        self.shifter_two.setObjectName("shifter_two")
        self.shifter_two.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.shifter_two.setMinimumSize(150,15)
        self.formLayout.setWidget(bottom_start_index+2,QtWidgets.QFormLayout.FieldRole, self.shifter_one)
        self.formLayout.setWidget(bottom_start_index+3,QtWidgets.QFormLayout.FieldRole, self.shifter_two)



        self.test_email = QtWidgets.QPushButton(Widget)
        self.test_email.setObjectName("test_email")
        self.formLayout.setWidget(bottom_start_index+4, QtWidgets.QFormLayout.FieldRole, self.test_email)

        self.horizontalLayout.addLayout(self.formLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.insertButton = QtWidgets.QPushButton(Widget)
        self.insertButton.setObjectName("insertButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.insertButton)
        self.lineEdit = QtWidgets.QLineEdit(Widget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setMinimumWidth(600)
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.textBrowser = QtWidgets.QTextBrowser(Widget)
        self.textBrowser.setObjectName("textBrowser")

        self.textBrowser.setTextBackgroundColor(QtGui.QColor(5,5,5))
        self.textBrowser.setTextColor(QtGui.QColor(0, 255, 0))
        self.textBrowser.setStyleSheet("background-color: black;")
        self.textBrowser.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
#        self.textBrowser.setEnabled(False)
        self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.verticalLayout.addWidget(self.textBrowser)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Widget)
        QtCore.QMetaObject.connectSlotsByName(Widget)

    def retranslateUi(self, Widget):
        _translate = QtCore.QCoreApplication.translate
        Widget.setWindowTitle(_translate("Widget", "Widget"))

        
        self.goPosBut.setText(_translate("Widget", "Go!"))
        self.goWaveBut.setText(_translate("Widget", "Go!"))
        self.label.setText(_translate("Widget", "Location:"))
        self.positionLbl.setText(_translate("Widget", "0.00 mm"))
        self.insertButton.setText(_translate("Widget", "Insert"))
        self.test_email.setText(_translate("Widget", "Test Alert Email"))
