import os 
import numpy as np 
import datetime 
from scipy.interpolate import interp1d 

logfile = os.path.join(os.path.dirname(__file__), "..", "gui","data", "command.log")
def load_log():
    _obj = open(logfile,'rt')
    lines = _obj.readlines()
    _obj.close()

    timestamps = []
    entry = []
    for line in lines:
        brk = line.split(" : ")
        if "TUBEFULL" in brk[1]:

            timestamps.append(datetime.datetime.fromisoformat(brk[0]).timestamp())
            entry.append("TUBEFULL")

    return np.array(timestamps, dtype=float)


FILL_TIMES = load_log()

def get_fill_times(times):
    mint = times.min()
    maxt = times.max()


    mask = np.logical_and(FILL_TIMES>mint, FILL_TIMES<maxt)
    return FILL_TIMES[mask]

def build_bounds(filepath:str):
    """
        Runs the bounds water-analysis on the data at the given filepath. 
        Gets the expected bounds for each wavelength as a function of hours since the "TUBEFULL" signal
    """
    wavelens = [450, 410, 365, 295, 278, 255]
    data = np.loadtxt(filepath, delimiter=",").T

    times = data[0]

    trigger_data = data[1]
    receiver_data = -1*np.log(1 - data[2]/trigger_data)
    monitor_data = -1*np.log(1- data[3]/trigger_data)

    waveno = data[5] 

    ratio = monitor_data/receiver_data

    fills = get_fill_times(data[0])
    fills = (fills- np.nanmin(times))/3600
    times = (times - np.nanmin(times))/3600

    # get the nominal fill characteristic PER wavelength

    partial_sums = {}
    diffsq = {}
    test_times = np.linspace(0.01, 1.35, 50)


    for it in range(len(fills)):
        if it==0:
            continue

        mintime = fills[it]
        if it==len(fills)-1:
            maxtime = times[-1]
        else:
            maxtime = fills[it+1]

        big_mask = np.logical_and(times>mintime, times<maxtime)
        these_times = times[big_mask]
        these_ratios = ratio[big_mask]

        for _i in range(5):
            i = _i+1
            submask = waveno[big_mask]==i 
            #print(these_times[submask].min()-mintime, these_times[submask].max()-mintime)
            these_values = these_ratios[submask]

            diffs = np.diff(these_values)
            diffs = np.append(diffs, diffs[-1])
            good_mask = np.abs(diffs/these_values)< 0.25 # a 50% change in one step


            interpo = interp1d(these_times[submask][good_mask]-mintime, these_ratios[submask][good_mask], fill_value='extrapolate')

            if i in partial_sums:
                partial_sums[i].append(interpo(test_times))
            else:
                partial_sums[i] = [interpo(test_times)]

            
                #plt.plot(these_times[submask][good_mask]-mintime, these_ratios[submask][good_mask], alpha=0.25, ls='-', marker='d', color='gray')
            # , color=get_color(i+2, 7, 'nipy_spectral_r'),label="{} nm".format(wavelens[i]), ls='-', marker='d')

    results={
        "times":test_times,
        "mean":{},
        "std":{}
    }
    for _i in range(5):
        i = _i+1
        results["mean"][i]  = np.mean(partial_sums[i], axis=0)
        results["std"][i]   = np.std(partial_sums[i], axis=0)

    return results

    
        