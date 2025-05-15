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

time_edge  = np.logspace(1, 8, 100)
time_edge = np.arange(4, 370, 4)
tbinm = np.zeros(len(time_edge)-1)
tbinr = np.zeros(len(time_edge)-1)
for i in range(100):
    trig, monitor, rec = test.measure(True)

    times = np.linspace(0, (test.totalSamples - 1) * test.actualSampleIntervalNs, test.totalSamples)
    


    thresh = 10
    montime, m_partial = get_cfd_time(times, -monitor, thresh, True)

    rectime,r_partial = get_cfd_time(times, -rec, thresh, True)

    mondiff = np.diff(montime)
    recdiff = np.diff(rectime)
    tbinm += np.histogram(mondiff, time_edge)[0]
    tbinr += np.histogram(recdiff, time_edge)[0]

plt.clf()
plt.stairs(tbinr, time_edge, label="Receiver")
plt.stairs(tbinm, time_edge, label="Monitor")
plt.grid(which='both', alpha=0.3)
plt.legend()
plt.yscale('log')
#plt.xscale('log')
plt.xlabel(r"$\Delta$ t [ns]")
plt.tight_layout()
plt.savefig("./plots/time_tdiff.png", dpi=400)
plt.show()
    
