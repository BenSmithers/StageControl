from read_pico import PicoMeasure
import numpy as np 
import json 
import time 
from utils import get_rtime, get_valid, get_cfd_time
import matplotlib.pyplot as plt 
print("Initializing")
counter = 0

keepon = False
onct = 1
while True:
    if not keepon:
        test = PicoMeasure(True)

    od = test.calibrate(True)
    keepon = False # sum(od["rec"][60:])>500 or keepon 
    if keepon:
        onct +=1 
    
    if True: # onct%100==0:
        plt.clf()
        plt.stairs(od["monitor"], od["bins"],label="Mon")
        plt.stairs(od["rec"], od["bins"],label="Rec")
        plt.yscale('log')
    #    plt.ylim([1e1, 5e5])
        plt.xlim([0, 200])
    #    plt.vlines([8,], 1e1, 1e5, color='gray')
        plt.legend()
        plt.show()
    
#    plt.savefig("stupid_plots/test_{}_amp.png".format(counter),dpi=400)
    counter +=1
    if not keepon:
        test.close()
    #plt.show()
