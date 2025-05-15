import sys 
import json
import matplotlib.pyplot as plt 
import numpy as np
from math import log10
filename = sys.argv[1]

newname = filename.replace("json", "png")

_obj = open(filename,'rt')
data = json.load(_obj)
_obj.close()

bins = data["bins"]
mon = np.array(data["monitor"])
rec = np.array(data["rec"])

binno = np.digitize(6, bins)
mon_slope = (mon[binno] - mon[binno-1])/(bins[binno] - bins[binno-1])
rec_slope = (rec[binno] - rec[binno-1])/(bins[binno] - bins[binno-1])

mon_all = np.sum(mon[binno:])
rec_all = np.sum(rec[binno:])

before = log10( 1 - (rec_all/np.sum(rec))) / log10( 1 - (mon_all/np.sum(mon)))

after = log10( 1 - ((rec_all + rec_slope*0.05)/np.sum(rec))) / log10( 1 - ((mon_all + mon_slope*0.05)/np.sum(mon)))

print("Change from 0.05mV change {} -> {}".format(before, after))
print((before - after)/after)

plt.stairs(mon, bins, color='blue', label="Monitor")
plt.stairs(rec, bins, color='orange', label="Receiver")
plt.vlines([6,], 1e1, 1e5, color='gray')
plt.legend()
plt.ylim([1e1, 5e5])
plt.xlim([0, 100])
plt.yscale('log')
plt.xlabel("Peak Height [mV]")
plt.ylabel("Counts")
plt.savefig("./plots/"+newname, dpi=400)