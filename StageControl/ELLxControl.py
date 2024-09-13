import serial 
import time 

BAUD = 9600
DATABIT = 9
PARITY=serial.PARITY_NONE
HANDSHAKE=False
STOP_BIT=serial.STOPBITS_ONE

class ELLxConnection:
    def __ini__(self, usb_interface):
        """
            Pass the full file path to the USB interface used to connect with the linear stage 

            purge dwell 50ms
            purge
            post putge dwell 50ms
            reset device
            no flow control 
        """
        self._con = serial.Serial(usb_interface, baudrate=BAUD, parity=PARITY, bytesize=DATABIT, stopbits=STOP_BIT)
        self._pulses_per_rev = 1024 # from datasheet 

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

    def send_and_receive(self, message:str):
        """
            Pass un-encoded string without a linebreak 
                ie "0in" for information 

            Returns the decoded response 
        """
        self._con.write((message+"\n").encode()) 
        return self._con.readline().decode()
    def get_device_information(self):
        pass 