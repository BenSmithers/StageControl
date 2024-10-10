"""
This script handles the SSH connection to the Rhasperry pi that interfaces with the pumps and stuff 
"""
import pexpect
from pexpect import pxssh
import numpy as np 
import time 

from constants import HOST, USER, KEY_LOC, PORT

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
    
    @pyqtSlot()
    def initialize(self):
        self._connection = pxssh.pxssh() 
        self._connection.login(
            server = HOST,
            username = USER,
            ssh_key = KEY_LOC,
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
        raw_response = self.send_receive("data")
        """
            NEED TO IMPLEMENT PARSER
        """
        #raise NotImplementedError("Add data parser!")
        ret_dat = {
            "flow":np.array([0,]*6),
            "pressure":np.random.randn(6)*5 + 20,
            "temperature":np.random.randn(2)*2 + 27
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