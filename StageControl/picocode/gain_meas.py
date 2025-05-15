from read_pico import PicoMeasure
import numpy as np 
import json 
import time 
from utils import get_rtime, get_valid, get_cfd_time
import matplotlib.pyplot as plt 
print("Initializing")
plt.style.use("wms.mplstyle")

counter = 0

test = PicoMeasure(True)
keepon = False
onct = 1
mon_run = None
rec_run = None
for i in range(30):

    od = test.calibrate(False)
   
    if mon_run is None:
        mon_run =np.array( od["monitor"])
        rec_run = np.array(od["rec"])
    else:
        mon_run = mon_run + np.array(od["monitor"])
        rec_run = rec_run + np.array(od["rec"])
    

plt.clf()

plt.stairs(rec_run, od["bins"],label="Receiver")
plt.stairs(mon_run,  od["bins"],label="Monitor")
plt.xlabel("Pulse Height [ADC]")
plt.yscale('log')
plt.xlim([0, 200])
plt.legend()
plt.tight_layout()
plt.savefig("./plots/gain.png")
plt.show()

