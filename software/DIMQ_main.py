# -*- coding: utf-8 -*-
from PyQt5 import QtCore,QtGui,QtWidgets
from PyQt5.QtWidgets import  QMainWindow, QApplication, QFileDialog

from dimq.gui import Ui_MainWindow
from dimq.dimq import dimq


import serial
import serial.tools.list_ports
import json
import datetime
import csv
import time 
import sys

com_port_list = []
port_list   =  serial.tools.list_ports.comports()

debug = True
#define SENSOR_PH_1    1 // 
#define SENSOR_PH_2    2 // 
#define SENSOR_PH_3    3 // 
#define SENSOR_PH_OPR  4 // 
#define SENSOR_DO_1    5 // 
#define SENSOR_DO_2    6 // 
#define SENSOR_NO3     7 // 
COM_PORT = "COM16"
DATA_PATH       = "data/"
TYPE_SENSORS    = [ {"ID":"0","type":"SENSOR_PH_1","val":"pH","unit":"pH"},    # sensor ph gravity
                    {"ID":"1","type":"SENSOR_PH_2","val":"pH","unit":"pH"},    # sensor ph gravity  lab
                    {"ID":"2","type":"SENSOR_PH_3","val":"pH","unit":"pH"},    # sensor ph aliexpres
                    {"ID":"3","type":"SENSOR_PH_4","val":"pH","unit":"pH"},    # sensor ph gravity
                    {"ID":"4","type":"SENSOR_DO_1","val":"DO","unit":"ppm"},   # sensor DO atlas scientific
                    {"ID":"6","type":"SENSOR_DO_2","val":"DO","unit":"ppm"},   # sensor DO gravity
                    {"ID":"5","type":"SENSOR_N03" ,"val":"NO3","unit":"ppm"} ]  # sensor NO3 aliexpress

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('DIMQ')
        self.setWindowIcon(QtGui.QIcon('dimq/img/logo.JPG'))
        #rest = self.setWindowIcon(QtGui.QIcon('dimq/img/logo.JPG'))
        #print(rest)

        self.com_port  = COM_PORT
        self.dimq   = None #eq("b1",self.com)
        self.m      = 0.028 #pH/mV
        self.n      = 0.6 #pH
        self.mv     = 1500 #pH
        self.ph     = 7.0

        self.sensors_array = []



        for k in TYPE_SENSORS:
            self.sensors_array.append(k["type"])

        self.sensor_type = self.sensors_array[0]

        self.time_now = ""
        self.file_name = ""

        #FILE OBJ TO SAVE DATA
        self.data_path    = DATA_PATH
        self.data_file    = None
        self.data_writer  = None

        self.com_ports_used = []
        self.com_ports = []

        self.run_state = False
        self.connected = False
        self.ready          = False
        self.auto_correct   = False
        self.temp_adj       = False 
        self.elapsed_time   = 0 
        self.sample_time    = 1# in seconds


        #TIME AND DATE     
        self.date_now = QtCore.QDate.currentDate()
        
        #MGMT UPDATE DATA
        self.run_timer = QtCore.QTimer()
        self.run_timer.setInterval(1000*self.sample_time)
        self.run_timer.timeout.connect(self.updateData)
        #self.run_timer.start()
        
        #MGMT OF TIME
        self.clock_timer = QtCore.QTimer()
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self.updateTime)
        self.clock_timer.start()

        self.ui.lineEdit_10.setReadOnly(True) 
        self.ui.lineEdit_11.setReadOnly(True) 
        self.ui.lineEdit_12.setReadOnly(True)
        self.ui.lineEdit_13.setReadOnly(True) 
        self.ui.lineEdit_5.setReadOnly(True) 
        self.ui.lineEdit_8.setReadOnly(True) 
        self.ui.lineEdit_9.setReadOnly(True) 
        

        self.ui.pushButton_8.setDisabled(True)
        self.ui.pushButton_6.setDisabled(True)
        self.ui.pushButton_9.setDisabled(True)
        self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.ui.pushButton_4.setDisabled(True)
        self.ui.pushButton_7.setDisabled(True)

        self.ui.lineEdit_2.setDisabled(True)
        self.ui.lineEdit_3.setDisabled(True)
        self.ui.comboBox_2.setDisabled(True)


        self.ui.radioButton.setChecked(True)

        self.ui.lineEdit_8.setText(str(self.m))
        self.ui.lineEdit_9.setText(str(self.n))
        
        self.ui.lineEdit_5.setText(str(self.mv))
        self.ui.lineEdit_10.setText(str(self.ph))

        for port, desc, hwid in sorted(port_list):
            com_port_list.append("{}".format(port))
        
        self.ui.comboBox.addItems(com_port_list)
        self.ui.comboBox_2.addItems(self.sensors_array)

        #select com port
        self.ui.comboBox.currentIndexChanged.connect(self.selectPort)
        #connect
        self.ui.pushButton.clicked.connect(self.connect)
        #Change directory
        self.ui.pushButton_3.clicked.connect(self.changeDir)
        #set sensor type
        self.ui.pushButton_2.clicked.connect(self.setSensorType)
        #set sample time
        self.ui.pushButton_4.clicked.connect(self.setSampleTime)
        #set automatic mode
        self.ui.radioButton.toggled.connect(self.setMode)
        #set manual adjust values
        self.ui.pushButton_5.clicked.connect(self.setParameters)
        #set auto adjust
        self.ui.pushButton_6.clicked.connect(self.autoAdjust)
        #set temperature compensation
        self.ui.pushButton_9.clicked.connect(self.tempCompensation)


    def selectPort(self):
        self.com_port = self.ui.comboBox.currentText()
        if debug:
            print(f"new com port : {self.com_port}")
        
    def connect(self):
        if self.connected:
            self.ui.label_2.setText("Disconnected")
            self.ui.pushButton.setText("CONNECT")
            try:
                self.dimq.disconnectSerialPort()
                self.connected = False
            except Exception as e:
                print("Not COM available")
            self.ui.comboBox_2.setDisabled(True)
            self.ui.pushButton_2.setDisabled(True)
            self.ui.lineEdit_3.setDisabled(True)
            self.ui.pushButton_4.setDisabled(True)
            self.ui.lineEdit_2.setDisabled(True)
            self.ui.pushButton_3.setDisabled(True)
            self.ui.pushButton_7.setDisabled(True)
            self.ready = False
         
        else:
            self.ui.label_2.setText("Connected")
            self.ui.pushButton.setText("DISCONNECT")
            self.com_port = self.ui.comboBox.currentText()
            self.dimq =  dimq("b1",self.com_port)
            self.dimq.connectSerialPort()
            self.connected = True
            self.run_timer.start()
            self.ui.comboBox_2.setDisabled(False)
            self.ui.pushButton_2.setDisabled(False)
            if debug:
                print(f" connected to port : {self.com_port}")

    def changeDir(self):
        self.data_path = QFileDialog.getExistingDirectory(self, caption = 'Seleccione nuevo directorio',directory = DATA_PATH)+"/"        
        if debug:
            print (self.data_path)
        self.ui.lineEdit_2.setText(self.data_path)
        self.ui.lineEdit_3.setDisabled(False)
        self.ui.pushButton_4.setDisabled(False)


    def setMode(self):
        self.mode = self.ui.radioButton.isChecked()
        if self.mode: #manual mode
            self.ui.pushButton_6.setText('Off')
            self.ui.pushButton_9.setText('Off')
            self.auto_correct   = False
            self.temp_adj       = False
            self.ui.pushButton_6.setDisabled(True)
            self.ui.pushButton_9.setDisabled(True)
            self.ui.label_7.setDisabled(False)
            self.ui.label_8.setDisabled(False)
            self.ui.lineEdit_7.setDisabled(False)
            self.ui.lineEdit_6.setDisabled(False)
            self.ui.pushButton_5.setDisabled(False)

        else:
            self.ui.pushButton_6.setDisabled(False)
            self.ui.pushButton_9.setDisabled(False)
            self.ui.label_7.setDisabled(True)
            self.ui.label_8.setDisabled(True)
            self.ui.lineEdit_7.setDisabled(True)
            self.ui.lineEdit_6.setDisabled(True)
            self.ui.pushButton_5.setDisabled(True)

    def calibrate(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def setSensorType(self):
        self.sensor_type = self.ui.comboBox_2.currentText()
        for k in TYPE_SENSORS:
            if k["type"] == self.sensor_type:          
                self.ui.label_18.setText(k["val"])
                self.ui.label_6.setText(k["unit"])
                self.ui.label_10.setText("Slope ["+k["unit"]+"/mV]")
                self.ui.label_10.setText("Slope ["+k["unit"]+"/mV]")
                self.ui.label_7.setText("m ["+k["unit"]+"/mV]")
                self.ui.label_8.setText("n ["+k["unit"]+"]")
                print(f"sensor selecciondado { self.sensor_type}")
        self.ui.lineEdit_2.setDisabled(False)
        self.ui.pushButton_3.setDisabled(False)



    def setSampleTime(self):
        self.sample_time = float(self.ui.lineEdit_3.text())

        if self.sample_time < 0.1:
            self.sample_time = 0.1
            self.ui.label_21.setText(str(self.sample_time))
        if self.connected:
            self.run_timer.stop()
            self.run_timer.setInterval(int(1000*self.sample_time))
            self.run_timer.start()
        self.ui.pushButton_7.setDisabled(False)
        self.ready = True

    def setParameters(self):
        self.m = float(self.ui.lineEdit_6.text())
        self.n = float(self.ui.lineEdit_7.text())
        self.ui.lineEdit_8.setText(str(self.m))
        self.ui.lineEdit_9.setText(str(self.n))

    def autoAdjust(self):
        if self.auto_correct:
            self.ui.pushButton_6.setText('Off')
            self.auto_correct = False
        else:
            self.ui.pushButton_6.setText('On')
            self.auto_correct = True

    def tempCompensation(self):
        if self.temp_adj:
            self.ui.pushButton_9.setText('Off')
            self.temp_adj = False
        else:
            self.ui.pushButton_9.setText('On')
            self.temp_adj = True

    def updateTime(self):
        current_time = QtCore.QTime.currentTime()
        label_time   = current_time.toString('hh:mm:ss')
        self.ui.lineEdit_11.setText(label_time)
        if self.run_state:
            self.elapsed_time += 1
            self.ui.lineEdit_12.setText(str(datetime.timedelta(seconds = self.elapsed_time)))

    def updateData(self):
        if self.connected and self.ready:      
            self.ui.lineEdit_13.setText(format(self.dimq.getTemp()    ,'.2f'))
            self.ui.lineEdit_5.setText( format(self.dimq.getmV()      ,'.2f'))
            self.ui.lineEdit_10.setText(format(self.dimq.getValue()   ,'.2f'))

    def Close(self):
        if self.connected:
            self.dimq.stopRcvr()
        self.clock_timer.stop()
        self.run_timer.stop()

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
   
    ret = app.exec_()
    main.Close()
    print("stoped")
    sys.exit(ret)