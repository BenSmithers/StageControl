"""
This script handles the SSH connection to the Rhasperry pi that interfaces with the pumps and stuff 
"""
import pexpect
from pexpect import pxssh
from StageControl.gui.constants import HOST, USER, KEY_LOC
import time 
class PiConnect:
    """
        TODO 

        update the prompt to be correct 
    """
    def __init__(self):
        self._connection = pxssh.pxssh() 
        self._connection.login(
            server = HOST,
            user = USER,
            ssh_key = KEY_LOC,
            auto_prompt_reset=False
        )

        self.send_receive("cd wmsLabview")
        time.sleep(1)
        self._connection.sendline("python3 wms_main.py")
        # update prompt now 
        self._connection.set_unique_prompt()
        self._connection.PROMT = "" # reg ex
        time.sleep(1)

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
        raise NotImplementedError("Add data parser!")
        ret_dat = {
            "flow":[],
            "pressure":[],
            "temperature":[]
        }
        return ret_dat["pressure"], ret_dat["flow"], ret_dat["temperature"]

    
    def pump(self, number:int, on:bool):
        if not(number>=1 and number<=3):
            raise ValueError("Pump must be between 1 and 3")
        self.send_receive("pu{} {}".format(
            number, "on" if on else "off"
        ))
        time.sleep(1)

    def sv(self, number:int, on:bool):
        if not(number>=1 and number<=2):
            raise ValueError("SV must be between 1 and 2")
        self.send_receive("sv{} {}".format(
            number, "on" if on else "off"
        ))
        time.sleep(1)    
    def bv(self, number:int, on:bool):
        if not(number>=1 and number<=6):
            raise ValueError("BV must be between 1 and 6")
        self.send_receive("bv{} {}".format(
            number, "on" if on else "off"
        ))
        time.sleep(1)