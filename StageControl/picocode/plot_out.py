import json 
import matplotlib.pyplot as plt

_obj = open('out.json', 'r')
data = json.load(_obj)
_obj.close()


plt.plot(range(len(data["all_bs"])), data["all_bs"], label="Channel B")
plt.plot(range(len(data["all_ds"])), data["all_ds"], label="Channel D")
plt.ylabel("mV")
plt.xlabel("Measurement [~seconds]")
plt.legend()
plt.savefig("./plots/pedestal_drift.png", dpi=400)
plt.show()