from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QTimer


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
    data_recieved = pyqtSignal(int, int, int, int, int, int)
    message_signal = pyqtSignal(str)
    initialized = pyqtSignal()
    waveforms = pyqtSignal(dict)
    
    def __init__(self, nopico=False):
        super(QObject, self).__init__()
        from StageControl.picocode.read_pico import PicoMeasure

        self._timer=QTimer(self)
        self._nopico = nopico
        if nopico:
            self._pico = None
        else:
            self._pico = PicoMeasure(True)
        
        """
            0 - don't refill
            1 - filtered 
            2 - tank
            3 - osmosis 
        """

        self._waves = [-1, 1,2,3,4,5]
        self._refill_kind = 0 
        
        self._wave_ind = 0
        self._is_striping = False
        self._running = False
        self._timer.timeout.connect(self.measure)
    
    @pyqtSlot()
    def get_waves(self):
        self.message_signal.emit("Ignoring WF request")
        adc2mVChAMax, adc2mVChBMax, adc2mVChDMax  = self._pico.measure(True)
        data_dict = {
            "trigger":adc2mVChAMax,
            "monitor":adc2mVChBMax, 
            "receiver":adc2mVChDMax
        }
        self.waveforms.emit(data_dict)

    @pyqtSlot()
    def initialize(self):
        if self._nopico:
            self.message_signal.emit("IN DEBUG MODE!")
            return 
        self._pico.initialze()
        self.message_signal.emit("Initialized PicoScope")
        self.initialized.emit()

    @pyqtSlot()
    def gain_run(self):
        if self._nopico:
            return
        self.message_signal.emit("Making Gain Measurement")
        self._pico.calibrate()
        

    @pyqtSlot(bool)
    def start_data_taking(self, is_striping:bool):
        if self._nopico:
            self.message_signal.emit("In nopico mode. No data will be taken")
            return 
        self._is_striping = is_striping
        self._wave_ind = 0
        self._running = True 

        if self._is_striping:
            self.change_wavelength.emit(self._wave_ind )
        else:
            self._timer.start(5)
        self.message_signal.emit("Starting run")    

    @pyqtSlot()
    def stop_data_taking(self):
        """
            Told to stop data taking. 
            So we do that and reset these variables
        """
        self._wave_ind = 0
        self._is_striping = False
        self._running = False
        self.message_signal.emit("Stopping run")
        self._timer.stop()

    @pyqtSlot()
    def measure(self):
        """
            Measure the current intensity. 
            If we aren't doing "striping" we immediately send the data-log signal and wait 30 seconds before starting again
        """
        if self._running and (not self._nopico):
            try:
                trig, mon, rec, mon_dark, rec_dark = self._pico.measure()
            except Exception as e:
                self.message_signal.emit(str(e))
                trig = 0
                mon = 0
                rec = 0
                mon_dark = 0
                rec_dark =0 

            if self._is_striping and self._running:
                self.data_recieved.emit(self._waves[self._wave_ind], trig, mon, rec, mon_dark, rec_dark)

                grab_waves = (mon_dark/trig > 0.02 or rec_dark/trig > 0.02) and self._waves[self._wave_ind]==-1
                if grab_waves:
                    self.get_waves()
                self._wave_ind+=1
                self._wave_ind = self._wave_ind % len(self._waves)

                self.change_wavelength.emit(self._waves[self._wave_ind])
            elif (not self._is_striping) and self._running:
                self.data_recieved.emit(-1, trig, mon, rec, mon_dark, rec_dark)
                self._timer.start(10)
            else:
                # not running? 
                return
                #self._timer.start(15) # take a 30 second break
        else:
            self._running = False 

