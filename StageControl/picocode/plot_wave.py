from read_pico import PicoMeasure
import numpy as np 
import json 
import time 
from utils import get_rtime, get_valid, get_cfd_time
import matplotlib.pyplot as plt 
print("Initializing")
plt.style.use("wms.mplstyle")

test = PicoMeasure(True)
test.initialze()
tdiff_bins = np.arange(4, 374, 4)
rec_bin = np.zeros(len(tdiff_bins)-1)
mon_bin = np.zeros(len(tdiff_bins)-1)

grab = 10000

print("Receiving Waveforms")
for i in range(10):
    trig, monitor, rec = test.measure(True)
    times = np.linspace(0, (test.totalSamples - 1) * test.actualSampleIntervalNs, test.totalSamples)[:grab]
    plt.clf()

    
    plt.plot(times, rec[:grab], label="Receiver")
    plt.plot(times, monitor[:grab], label="Monitor")
    plt.plot(times, trig[:grab]/200,label="Trigger/200")
    plt.legend()
    plt.xlabel("Time [ns]")
    plt.ylabel("Amplitude [mV]")
    plt.tight_layout()
    plt.show()
