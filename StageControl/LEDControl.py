import serial 
import time 
from contextlib import ContextDecorator

BAUD = 115200
class LEDBoard(ContextDecorator):
    """
        opens and manages a connection with an LED flasher board 
    """
    def __init__(self, usb_interface):
        self._con = serial.Serial(usb_interface, baudrate=BAUD)
        time.sleep(1)

    def set_int_trigger(self):
        pass
    def set_ext_trigger(self):
        pass
    def set_fast_rate(self):
        pass 
    def set_slow_rate(self):
        pass

    def set_adc(self, value:int):
        if not isinstance(value, int):
            raise TypeError("`which` must be an integer; found {}".format(type(which)))
        if value<0 or value>1234:
            raise ValueError("Invalid no {}".format(value))
        msg = "S{0:04d}\n".format(value).encode()
        print("LED -- {}".format(msg))
        self._con.write()
    def activate_led(self, which:int):
        if not isinstance(which, int):
            raise TypeError("`which` must be an integer; found {}".format(type(which)))
        if which<1 or which>9:
            raise ValueError("Invalid no {}".format(which))
        msg = "L{}\n".format(which).encode()
        self._con.write(msg)
        print("LED -- {}".format(msg))
    def __enter__(self, *args):
        self._con.write("E\n".encode())
        print("LED -- enable")
        time.sleep(1)
    def __exit__(self, *args):
        self._con.write("L0\n".encode())
        self._con.write("D\n".encode())