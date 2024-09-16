import serial 
import time 

BAUD = 9600
DATABIT = 8
PARITY=serial.PARITY_NONE
HANDSHAKE=False
STOP_BIT=serial.STOPBITS_ONE

from StageControl import message
from StageControl.utils import Status
class ELLxConnection:
    def __init__(self, usb_interface, pulses_per_rev=1024):
        """
            Pass the full file path to the USB interface used to connect with the linear stage 

            purge dwell 50ms
            purge
            post putge dwell 50ms
            reset device
            no flow control 
        """
        self._con = serial.Serial(usb_interface, baudrate=BAUD, parity=PARITY, bytesize=DATABIT, stopbits=STOP_BIT)
        self._pulses_per_rev = pulses_per_rev

        # The Thorlabs protocol description recommends toggeling the RTS pin and resetting the
        # input and output buffer. This makes sense, since the internal controller of the Thorlabs
        # device does not know what data has reached us of the FTDI RS232 converter.
        # Similarly, we do not know the state of the controller input buffer.
        # Be toggling the RTS pin, we let the controller know that it should flush its caches.
        self._con.setRTS(1)
        time.sleep(0.05)
        self._con.reset_input_buffer()
        self._con.reset_output_buffer()
        time.sleep(0.05)
        self._con.setRTS(0)

        self._port = usb_interface
        self._debug = False

        time.sleep(0.5)
        self._con.reset_input_buffer()

    def _send_and_receive(self, this_call:message.Call, *args):
        """
            Encodes the a message type along with its required arguments

            Then, reads the response, and returns the appriate data depending on the kind of response received

        """
        self._send(this_call.encode(*args))
        time.sleep(1)
        raw_response = self._con.readline()
        resp = message.response_handler(raw_response)

        if resp[1]=="GS":
            code = int(resp[-1])
            this_stat = Status(code)
            if code!=0:
                print("Status : {}".format(this_stat))
            return this_stat 
        elif resp[1]=="PO":
            return int(resp[-1])
        elif resp[1]=="HO":
            return int(resp[-1])
        elif resp[1]=="GV":
            return int(resp[-1])
        elif resp[1]=="IN":
            return resp[2:]

    def _send(self, signal:bytes):
        """
            Pass un-encoded string without a linebreak 
                ie "0in" for information 

            Returns the decoded response 
        """
        self._con.write(signal + "\n".encode() ) 
        

    """
        Boilerplate access functions for the call/response handler
    """
    def go_home(self):
        return self._send_and_receive(message.GoHome)
    def get_position(self):
        return self._send_and_receive(message.RequestPosition)/self._pulses_per_rev
    def get_info(self):
        return self._send_and_receive(message.RequestInfo)
    def move_absolute(self, distance:float):
        return self._send_and_receive(message.MoveAbsolute, int(self._pulses_per_rev*distance))
    def move_relative(self, distance:float):
        return self._send_and_receive(message.MoveRelative, int(self._pulses_per_rev*distance))
    def set_velocity(self, pcent:int):
        return self._send_and_receive(message.SetVelocity, pcent)
    def get_velocity(self):
        return self._send_and_receive(message.GetVeolicty)
    def stop(self):
        return self._send_and_receive(message.Stop)