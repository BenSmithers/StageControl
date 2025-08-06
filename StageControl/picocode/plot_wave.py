import numpy as np 
import matplotlib.pyplot as plt 
import sys 

print("Loading")
plt.style.use("wms.mplstyle")

grab = 200000
import h5py as h5 
from scipy import fftpack
from scipy import fft

data = h5.File(sys.argv[1],'r')
trig = np.array(data["trigger"])
monitor = np.array(data["monitor"])
rec = np.array(data["receiver"])

times = np.array(range(len(rec)))*4
times = times[:grab]

plt.plot(times, rec[:grab], label="Receiver")
plt.plot(times, monitor[:grab], label="Monitor")
plt.plot(times, trig[:grab]/200,label="Trigger/200")
plt.legend()
plt.xlabel("Time [ns]")
plt.ylabel("Amplitude [mV]")
plt.tight_layout()
plt.show()

plt.clf()

sample_spacing = (times[1] - times[0])
print("Spacing", sample_spacing)

freq_space = fft.fft(rec)
freqs = fftpack.fftfreq(len(rec), sample_spacing)


if False:
    plt.plot(times, monitor, label="Monitor")
    plt.plot(times, rec, label="Reciever")
    plt.plot(times, trig, label="Trigger")
    plt.legend()
    plt.xlabel("Time [ns]", size=14)
    plt.ylabel("ADC", size=14)
    plt.tight_layout()
    plt.show()

def average(thisdat, nmerge=3):
    if nmerge==1:
        return thisdat
    if int((len(thisdat)%nmerge))!=0:
        thisdat = thisdat[:-(len(thisdat)%nmerge)]
    return np.mean(np.reshape(thisdat, (int(len(thisdat)/nmerge), nmerge)), axis=1)

import os 
plt.plot(average(freqs*1e9, 100), average(np.log10(np.abs(freq_space)), 100) )
plt.xlim([ -6e6, 6e6])
plt.ylim([3.2, 5])
path, fname = os.path.split(sys.argv[1])
plt.savefig("fourier_{}.png".format(fname), dpi=400)

plt.show()
