from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer

from StageControl.picocode.read_pico import main

def measure_faux():
    return 0, 0, 0

class DAQWorker(QObject):

    """
        Behavior:
            (start_data_taking) does setup, calls measure
            (measure) takes a datapoint by calling picoscope code. Then sets a 15 second timer
                it may need to change the wavelength. If so it stops the timer, then emits a change wavelength signal
            (resume) indicates the wavelength is changed. It takes a datapoint at the new wavelength, and starts the 15s timer 



    """
    change_wavelength = pyqtSignal(int)
    
    # wavelength, triggers, monitors, receivers 
    data_recieved = pyqtSignal(int, int, int, int)
    
    MAX_WAVE = 6
    def __init__(self):
        super(QObject, self).__init__()
        self._timer = QTimer()
        self._timer.timeout.connect(self.measure)

        self._last_wave = 0
        self._is_striping = False
        self._running = False

    @pyqtSlot(bool)
    def start_data_taking(self, is_striping:bool):
        self._is_striping = is_striping
        self._last_wave = 0 
        self._running = True 

        if self._is_striping:
            self.change_wavelength.emit(self._last_wave)
        else:
            self.measure()

    @pyqtSlot()
    def stop_data_taking(self):
        """
            Told to stop data taking. 
            So we do that and reset these variables
        """
        self._timer.stop()
        self._last_wave = 0
        self._is_striping = False
        self._running = False

    @pyqtSlot()
    def measure(self):
        """
            Measure the current intensity. 
            If we aren't doing "striping" we immediately send the data-log signal and wait 30 seconds before starting again
        """
        if self._running:
            trig, mon, rec = main()
            if self._is_striping:
                self.data_recieved.emit(self._last_wave, trig, mon, rec)
                self._last_wave+=1 
                self._last_wave = self._last_wave % self.MAX_WAVE
                self.change_wavelength.emit(self._last_wave)
            else:
                self.data_recieved.emit(-1, trig, mon, rec)
                self._timer.start(30) # take a 30 second break
        else:
            self._timer.stop()
