"""
This script handles the SSH connection to the Rhasperry pi that interfaces with the pumps and stuff 
"""
import pexpect
from pexpect import pxssh
import numpy as np 
import time 
import ast
from constants import HOST, USER, PASSWORD, PORT

from PyQt5.QtCore import QRunnable , QObject, pyqtSignal, pyqtSlot, QTimer 

class PiConnect(QObject):
    """
        This is a separate worker thread run separately from other stuff. 
        It starts a python script which it uses to access data on the pi.
        
        slots are used by the main window to signal this thread to tell the pi to do things
        Signals are used here to transmit (1) the data and (2) status messages back to the main window
        An initialize method is used to signal this thread the need to open the connection
    """
    data_signal = pyqtSignal(dict)
    message_siganl = pyqtSignal(str)

    def __init__(self):
        super(QObject, self).__init__()

    def finish(self):
        self._connection.sendline("exit")
        time.sleep(1)
        return 0
        
    @pyqtSlot()
    def initialize(self):
        self._connection = pxssh.pxssh() 
        self._connection.login(
            server = HOST,
            username = USER,
            password = PASSWORD,
            port=PORT,
            auto_prompt_reset=False
        )
        
        self.message_siganl.emit("changing to labview folder\n")
        # update prompt now 
        self._connection.set_unique_prompt()
        self._connection.PROMT = "^\$" # reg ex
        self.send_receive("cd wmsLabview")
        time.sleep(1)
        self.message_siganl.emit("starting wms_main\n")
        self._connection.sendline("python3 wms_main.py")
        self.message_siganl.emit("started!\n")

        time.sleep(1)
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.data)
        self.data_timer.start(2500)

    def send_receive(self, what):
        self._connection.sendline(what)
        self._connection.prompt()
        # get response, split by carriage return 
        raw = self._connection.before.decode('UTF-8').split("\r")
        return raw [2]
    
    def data(self):
        #raw_response = self.send_receive("data")
        self._connection.sendline("data")
        index = self._connection.expect(['request', pexpect.EOF, pexpect.TIMEOUT])
        #self._connection.prompt()
        if index:
            raw_response = ''
            print("No response")
            return
        if index == 0:            
            raw_response = self._connection.before.decode('UTF-8').split("\r")
            #print("** raw response ", raw_response)
            raw_data = raw_response[-2]
            #print("**** raw data ", raw_data)
            if "Pressure" not in raw_data:
                return
            data_list = ast.literal_eval(raw_data.strip())
            pressure = np.array([row[0] for row in data_list[1:]])
            flow = np.array([row[1] for row in data_list[1:]])
            temperature = np.array([row[2] for row in data_list[1:]])
            #raise NotImplementedError("Add data parser!")
            ret_dat = {
                "flow":flow,
                "pressure":pressure,
                "temperature":temperature,
            }        
            self.data_signal.emit(ret_dat)

    
    @pyqtSlot(int, bool)
    def pump(self, number:int, on:bool):
        if not(number>=1 and number<=3):
            raise ValueError("Pump must be between 1 and 3")
        self.send_receive("pu{} {}".format(
            number, "on" if on else "off"
        ))
        self.message_siganl.emit("pu{} {} signal sent\n".format(number, "on" if on else "off"))
        time.sleep(1)

    @pyqtSlot(int, bool)
    def sv(self, number:int, on:bool):
        if not(number>=1 and number<=2):
            raise ValueError("SV must be between 1 and 2")
        self.send_receive("sv{} {}".format(
            number, "on" if on else "off"
        ))
        self.message_siganl.emit("sv{} {} signal sent\n".format(number, "on" if on else "off"))
        time.sleep(1)   

    @pyqtSlot(int, bool)
    def bv(self, number:int, on:bool):
        if not(number>=1 and number<=6):
            raise ValueError("BV must be between 1 and 6")
        self.send_receive("bv{} {}".format(
            number, "on" if on else "off"
        ))
        self.message_siganl.emit("bv{} {} signal sent\n".format(number, "on" if on else "off"))
        time.sleep(1)
