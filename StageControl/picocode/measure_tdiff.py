from read_pico import PicoMeasure
import numpy as np 
import json 
import time 
from utils import get_rtime, get_valid, get_cfd_time
import matplotlib.pyplot as plt 
print("Initializing")
test = PicoMeasure(True)
test.initialze()
tdiff_bins = np.arange(4, 374, 4)
tdiff_bins = np.arange(4, 3740, 4)

rec_bin = np.zeros(len(tdiff_bins)-1)
mon_bin = np.zeros(len(tdiff_bins)-1)
plt.style.use("wms.mplstyle")
print("Receiving Waveforms")
for i in range(50):
    trig, monitor, rec = test.measure(True)

    times = np.linspace(0, (test.totalSamples - 1) * test.actualSampleIntervalNs, test.totalSamples)
    

    ctime,t_partial = get_cfd_time(times, trig, 1000, use_rise=True)

    tgood =(times.max() - times.min())/len(ctime)


    thresh = 10
    montime, m_partial = get_cfd_time(times, -monitor, thresh, True)

    tdiffs = get_rtime(ctime, montime)
    mon_bin += np.histogram(tdiffs, tdiff_bins)[0]

    rectime,r_partial = get_cfd_time(times, -rec, thresh, True)

    tdiffs = get_rtime(ctime, rectime)
    rec_bin += np.histogram(tdiffs, tdiff_bins)[0]

plt.clf()
plt.stairs(rec_bin, tdiff_bins, label="Receiver")
plt.stairs(mon_bin, tdiff_bins, label="Monitor")
plt.grid(which='both', alpha=0.3)
plt.legend()
plt.yscale('log')
plt.xlabel("Time Since Trigger [ns]")
plt.tight_layout()
plt.savefig("./plots/time_distr.png", dpi=400)
plt.show()
    
