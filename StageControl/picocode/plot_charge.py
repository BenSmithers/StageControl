import sys 
import json
import matplotlib.pyplot as plt 
import numpy as np

filename = sys.argv[1]

newname = filename.replace("json", "png")

_obj = open(filename,'rt')
data = json.load(_obj)
_obj.close()

bins = data["bins"]
mon = np.array(data["monitor"])
rec = np.array(data["rec"])

plt.stairs(mon, bins, color='blue', label="Monitor")
plt.stairs(rec, bins, color='orange', label="Receiver")
plt.vlines([6,], 1e1, 1e5, color='gray')
plt.legend()
plt.ylim([9e3,2e4])
plt.xlim([0, 10])
#plt.yscale('log')
plt.xlabel("Peak Height [mV]")
plt.ylabel("Counts")
plt.savefig("./plots/"+newname, dpi=400)