# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pipes.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1096, 731)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        spacerItem0 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem0)

        self.drain_button = QtWidgets.QPushButton(Form)
        self.drain_button.setText("Drain Chamber")
       # self.drain_button.setEnabled(False)
        self.verticalLayout.addWidget(self.drain_button)

        self.fill_filter = QtWidgets.QPushButton(Form)
        self.fill_filter.setText("Fill with Return Wayer")
        #self.fill_filter.setEnabled(False)
        self.verticalLayout.addWidget(self.fill_filter)

        self.fill_return = QtWidgets.QPushButton(Form)
        self.fill_return.setText("Fill with Supply Water")
        #self.fill_filter.setEnabled(False)
        self.verticalLayout.addWidget(self.fill_return)

        self.fill_osmosis = QtWidgets.QPushButton(Form)
        self.fill_osmosis.setText("Fill with Osmosis")
        #self.fill_osmosis.setEnabled(False)
        self.verticalLayout.addWidget(self.fill_osmosis)

        self.flow_button = QtWidgets.QPushButton(Form)
        self.flow_button.setText("Start Flow")
        self.verticalLayout.addWidget(self.flow_button)
        
        self.status_label = QtWidgets.QLabel(Form)
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setText("... Awaiting Input")
        self.verticalLayout.addWidget(self.status_label)
        self.stop_button = QtWidgets.QPushButton(Form)
        self.stop_button.setObjectName("stop_butotn")
        self.stop_button.setText("Stop Automation")
        self.stop_button.setEnabled(False)
        self.verticalLayout.addWidget(self.stop_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.bv1_button = QtWidgets.QCheckBox(Form)
        self.bv1_button.setObjectName("bv1_button")
        self.verticalLayout.addWidget(self.bv1_button)
        self.bv2_button = QtWidgets.QCheckBox(Form)
        self.bv2_button.setObjectName("bv2_button")
        self.verticalLayout.addWidget(self.bv2_button)
        self.bv3_button = QtWidgets.QCheckBox(Form)
        self.bv3_button.setObjectName("bv3_button")
        self.verticalLayout.addWidget(self.bv3_button)
        self.bv4_button = QtWidgets.QCheckBox(Form)
        self.bv4_button.setObjectName("bv4_button")
        self.verticalLayout.addWidget(self.bv4_button)
        self.bv5_button = QtWidgets.QCheckBox(Form)
        self.bv5_button.setObjectName("bv5_button")
        self.verticalLayout.addWidget(self.bv5_button)
        self.bv6_button = QtWidgets.QCheckBox(Form)
        self.bv6_button.setObjectName("bv6_button")
        self.verticalLayout.addWidget(self.bv6_button)

        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.sv1_button = QtWidgets.QCheckBox(Form)
        self.sv1_button.setObjectName("sv1_button")
        self.verticalLayout.addWidget(self.sv1_button)
        self.sv2_button = QtWidgets.QCheckBox(Form)
        self.sv2_button.setObjectName("sv2_button")
        self.verticalLayout.addWidget(self.sv2_button)
        self.sv3_button = QtWidgets.QCheckBox(Form)
        self.sv3_button.setObjectName("sv3_button")
        self.verticalLayout.addWidget(self.sv3_button)

        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.pu1_button = QtWidgets.QCheckBox(Form)
        self.pu1_button.setObjectName("pu1_button")
        self.verticalLayout.addWidget(self.pu1_button)
        self.pu2_button = QtWidgets.QCheckBox(Form)
        self.pu2_button.setObjectName("pu2_button")
        self.verticalLayout.addWidget(self.pu2_button)
        self.pu3_button = QtWidgets.QCheckBox(Form)
        self.pu3_button.setObjectName("pu3_button")
        self.verticalLayout.addWidget(self.pu3_button)

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setMinimumSize(QtCore.QSize(600, 0))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.horizontalLayout.addWidget(self.graphicsView)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        
        self.plbl_1 = QtWidgets.QLabel(Form)
        self.plbl_1.setObjectName("plbl_1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.plbl_1)
        self.lcdNumber = QtWidgets.QLabel(Form)
        self.lcdNumber.setObjectName("lcdNumber")
        self.lcdNumber.setText("0.0")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lcdNumber)
        self.plbl_2 = QtWidgets.QLabel(Form)
        self.plbl_2.setObjectName("plbl_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.plbl_2)
        self.lcdNumber_4 = QtWidgets.QLabel(Form)
        self.lcdNumber_4.setObjectName("lcdNumber_4")
        self.lcdNumber_4.setText("0.0")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lcdNumber_4)
        self.plbl_3 = QtWidgets.QLabel(Form)
        self.plbl_3.setObjectName("plbl_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.plbl_3)
        self.lcdNumber_3 = QtWidgets.QLabel(Form)
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.lcdNumber_3.setText("0.0")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lcdNumber_3)
        self.plbl_4 = QtWidgets.QLabel(Form)
        self.plbl_4.setObjectName("plbl_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.plbl_4)
        self.lcdNumber_2 = QtWidgets.QLabel(Form)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.lcdNumber_2.setText("0.0")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lcdNumber_2)
        spacerItem3 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.FieldRole, spacerItem3)

        self.temp_label_1 = QtWidgets.QLabel(Form)
        self.temp_label_1.setObjectName("temp_label_1")
        
        self.temp_value_1 = QtWidgets.QLabel(Form)
        self.temp_value_1.setObjectName("temp_value_1")
        self.temp_value_1.setText("0.0")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.temp_label_1)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.temp_value_1)
        self.temp_label_2 = QtWidgets.QLabel(Form)
        self.temp_label_2.setObjectName("temp_label_2")
        self.temp_value_2 = QtWidgets.QLabel(Form)
        self.temp_value_2.setObjectName("temp_value_2")
        self.temp_value_2.setText("0.0")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.temp_label_2)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.temp_value_2)

        spacerItem3 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.formLayout.setItem(7, QtWidgets.QFormLayout.FieldRole, spacerItem3)
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.flow1 = QtWidgets.QProgressBar(Form)
        self.flow1.setProperty("value", 3)
        self.flow1.setObjectName("flow1")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.flow1)
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.flow2 = QtWidgets.QProgressBar(Form)
        self.flow2.setProperty("value", 3)
        self.flow2.setObjectName("flow2")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.flow2)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.flow3 = QtWidgets.QProgressBar(Form)
        self.flow3.setProperty("value", 3)
        self.flow3.setObjectName("flow3")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.flow3)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.flow4 = QtWidgets.QProgressBar(Form)
        self.flow4.setProperty("value", 3)
        self.flow4.setObjectName("flow4")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole, self.flow4)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.flow5 = QtWidgets.QProgressBar(Form)
        self.flow5.setProperty("value", 3)
        self.flow5.setObjectName("flow5")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.flow5)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(13, QtWidgets.QFormLayout.FieldRole, spacerItem4)


        self.light_1 = QtWidgets.QLabel(Form)
        self.light_1.setObjectName("light_1")
        self.light_1.setText("Monitor Light Level")
        
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.LabelRole, self.light_1)
        self.lightlcdNumber = QtWidgets.QLabel(Form)
        self.lightlcdNumber.setObjectName("lightlcdNumber")
        self.lightlcdNumber.setText("0.0")
        self.formLayout.setWidget(14, QtWidgets.QFormLayout.FieldRole, self.lightlcdNumber)
        self.light_2 = QtWidgets.QLabel(Form)
        self.light_2.setObjectName("light_2")
        self.light_2.setText("Receiver Light Level")
        self.formLayout.setWidget(15, QtWidgets.QFormLayout.LabelRole, self.light_2)
        self.lightlcdNumber_4 = QtWidgets.QLabel(Form)
        self.lightlcdNumber_4.setObjectName("lcdNumber_4")
        self.lightlcdNumber_4.setText("0.0")
        self.formLayout.setWidget(15, QtWidgets.QFormLayout.FieldRole, self.lightlcdNumber_4)

        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(16, QtWidgets.QFormLayout.FieldRole, spacerItem5)



        self.water1_lbl = QtWidgets.QLabel(Form)
        self.water1_lbl.setObjectName("waterlbl1")
        self.water1_lbl.setText("Water Level 1")
        self.water1_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.formLayout.setWidget(17, QtWidgets.QFormLayout.LabelRole, self.water1_lbl)
        self.water_lvl1 = QtWidgets.QCheckBox(Form)
        self.water_lvl1.setObjectName("water_lvl1")
        self.water_lvl1.setEnabled(False)
#        self.water_lvl1.setText("Water Level 1")
        self.formLayout.setWidget(17, QtWidgets.QFormLayout.FieldRole, self.water_lvl1)

        self.water2_lbl = QtWidgets.QLabel(Form)
        self.water2_lbl.setObjectName("waterlbl2")
        self.water2_lbl.setText("Water Level 2")
        self.water2_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.LabelRole, self.water2_lbl)
        self.water_lvl2 = QtWidgets.QCheckBox(Form)
        self.water_lvl2.setObjectName("water_lvl2")
        self.water_lvl2.setEnabled(False)
#        self.water_lvl2.setText("Water Level 2")
        self.formLayout.setWidget(18, QtWidgets.QFormLayout.FieldRole, self.water_lvl2)
        
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(19, QtWidgets.QFormLayout.FieldRole, spacerItem5)



        self.horizontalLayout.addLayout(self.formLayout)

        self.relaunch_button = QtWidgets.QPushButton(Form)
        self.relaunch_button.setText("Relaunch Interface")
        self.relaunch_button.setEnabled(False)
        self.formLayout.setWidget(20, QtWidgets.QFormLayout.FieldRole, self.relaunch_button)
        

        self.flow1.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.flow2.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.flow3.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.flow4.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.flow5.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Ball Valves"))
        self.bv1_button.setText(_translate("Form", "BV1 (Supply Water)"))
        self.bv2_button.setText(_translate("Form", "BV2 (Filters)"))
        self.bv3_button.setText(_translate("Form", "BV3 (UV Lamp)"))
        self.bv4_button.setText(_translate("Form", "BV4 (Ion Filter)"))
        self.bv5_button.setText(_translate("Form", "BV5 (Osmosis)"))
        self.bv6_button.setText(_translate("Form", "BV6 (Chamber)"))
        self.label_2.setText(_translate("Form", "Solenoid Valves"))
        self.sv1_button.setText(_translate("Form", "SV1 (main)"))
        self.sv2_button.setText(_translate("Form", "SV2 (Pre-Chamber)"))
        self.sv3_button.setText(_translate("Form", "SV3 (Gas Removal)"))
        self.label_3.setText(_translate("Form", "Pumps"))
        self.pu1_button.setText(_translate("Form", "Pump 1 (input)"))
        self.pu2_button.setText(_translate("Form", "Pump 2 (Chamber)"))
        self.pu3_button.setText(_translate("Form", "Pump 3 (Tank Return)"))
        self.temp_label_1.setText(_translate("Form", "UV Thermocouple"))
        self.temp_label_2.setText(_translate("Form", "Post-Filter Temperature"))
        self.temp_value_1.setText(_translate("Form", "0"))
        self.temp_value_2.setText(_translate("Form", "0"))
        self.plbl_1.setText(_translate("Form", "Input Pressure"))
        self.plbl_2.setText(_translate("Form", "Pre-Filter Pressure"))
        self.plbl_3.setText(_translate("Form", "Post-Filter Pressure"))
        self.plbl_4.setText(_translate("Form", "Osmosis Pressure"))
        self.label_8.setText(_translate("Form", "Flow 1"))
        self.label_6.setText(_translate("Form", "Flow 2"))
        self.label_4.setText(_translate("Form", "Flow 3"))
        self.label_5.setText(_translate("Form", "Flow 4"))
        self.label_7.setText(_translate("Form", "Flow 5"))
