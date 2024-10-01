import serial 
import time 
from contextlib import ContextDecorator
from StageControl.utils import LEDNotFound
import os 

BAUD = 115200
class LEDBoard(ContextDecorator):
    """
        opens and manages a connection with an LED flasher board 
    """
    def __init__(self, usb_interface, fake=False ):
        self._fake = fake 
        if not self._fake:
            if not os.path.exists(usb_interface):
                raise LEDNotFound("Could not find LED board!")
            self._con = serial.Serial(usb_interface, baudrate=BAUD)
        time.sleep(1)
        

    def set_int_trigger(self):
        if not self._fake:
            self._con.write("TI\n".encode())
        return "TI\n"
    def set_ext_trigger(self):
        if not self._fake:
            self._con.write("TE\n".encode())
        return "TE\n"
    def set_fast_rate(self):
        if not self._fake:
            self._con.write("RF\n".encode())
        return "RF\n"
    
    def set_slow_rate(self):
        if not self._fake:
            self._con.write("RS\n".encode())
        return "RS\n"

    def set_adc(self, value:int):
        if not isinstance(value, int):
            raise TypeError("`which` must be an integer; found {}".format(type(which)))
        if value<0 or value>1023:
            raise ValueError("Invalid no {}".format(value))
        msg = "S{0:04d}\n".format(value).encode()
        
        if not self._fake:
            self._con.write(msg)
        return "LED -- {}".format(msg.decode())
    
    def activate_led(self, which:int):
        if not isinstance(which, int):
            raise TypeError("`which` must be an integer; found {}".format(type(which)))
        if which<1 or which>9:
            raise ValueError("Invalid no {}".format(which))
        msg = "L{}\n".format(which).encode()
        if not self._fake:
            self._con.write(msg)
        return "LED -- {}".format(msg.decode())
    
    def led_off(self):
        msg = "L0\n".encode()
        if not self._fake:
            self._con.write(msg)
        return "LED -- {}".format(msg.decode())
    def enable(self, *args):
        if not self._fake:
            self._con.write("E\n".encode())
        time.sleep(1)
        return "LED -- enable\n"
        
    def disable(self, *args):
        if not self._fake:
            self._con.write("L0\n".encode())
            self._con.write("D\n".encode())

    def __enter__(self, *args):
        self.enable()
    def __exit__(self, *args):
        self.disable()