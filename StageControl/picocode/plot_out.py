import json 
import matplotlib.pyplot as plt
import numpy as np 
_obj = open('out.json', 'r')
data = json.load(_obj)
_obj.close()

time = np.array(data["times"] )
time = time - min(time)


plt.plot(time, data["all_bs"], label="Channel B")
plt.plot(time, data["all_ds"], label="Channel D")
plt.ylabel("Pedestal [mV]")
plt.xlabel("Time [seconds]")
plt.legend()
plt.savefig("./plots/pedestal_drift3.png", dpi=400)
plt.show()