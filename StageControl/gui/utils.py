import numpy as np 
import os 
import datetime
logfile = os.path.join(os.path.dirname(__file__), "data", "command.log")

def fold(thisdat, nmerge=2):
    if nmerge==1:
        return thisdat
    # cut off the extra so it's divisible
    if int(len(thisdat)%nmerge)!=0:
        thisdat = thisdat[:-(len(thisdat)%nmerge)]
    holder =np.nansum(np.reshape(thisdat, (int(len(thisdat)/nmerge), nmerge)), axis=1)
    return holder

def average(thisdat, nmerge=3):
    if nmerge==1:
        return thisdat
    if int((len(thisdat)%nmerge))!=0:
        thisdat = thisdat[:-(len(thisdat)%nmerge)]
    return np.mean(np.reshape(thisdat, (int(len(thisdat)/nmerge), nmerge)), axis=1)

def get_event_time(times, text_key):
    mint = times.min()
    maxt = times.max()

    _obj = open(logfile,'rt')
    lines = _obj.readlines()
    _obj.close()

    timestamps = []
    for line in lines:
        brk = line.split(" : ")
        if text_key in brk[1]:

            timestamps.append(datetime.datetime.fromisoformat(brk[0]).timestamp())
    gstimes = np.array(timestamps)
    mask = np.logical_and(gstimes>mint, gstimes<maxt)
    return gstimes[mask]

