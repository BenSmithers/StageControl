
        
import os 
import ctypes
import numpy as np
import h5py as h5 
from picosdk.ps3000a import ps3000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, PICO_STATUS_LOOKUP
import time
from scipy.signal import find_peaks
from StageControl.picocode.utils import get_valid, get_cfd_time
import json 

thresh = 10
bped = -0.55
dped = -1.0

channelInputRanges = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]
def adc2mV(buffer, rang, maxADC):
    """
    Rewrote the picoscode version of this to use vectorized numpy math
    Got some 100x speed improvements 
    """
    return (buffer.astype(float)*channelInputRanges[rang])/maxADC.value 



class PicoMeasure:
    def __init__(self, block_mode = False):
        self.nextSample = 0
        self.autoStopOuter = False
        self.wasCalledBack = False
        self._initialized = True
        self._block_mode = block_mode

        self.collection_time = 30

        self.rec_lt_good = 40./376
        self.mon_lt_good = 40./376


        # Create self.chandle and self.status ready for use
        self.chandle = ctypes.c_int16()
        self.status = {}
        self._good = False 
        self.start()
        
        self.collection_time = 30
        return
        while not self._good:
            print("Check")
            self.start()
            self.collection_time = 10
            self.calibrate() 
            if not self._good:
                self.close()
        self.collection_time = 30


    def start(self):

        # Open PicoScope 5000 Series device
        self.status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(self.chandle), None)

        try:
            assert_pico_ok(self.status["openunit"])
        except: # PicoNotOkError:

            powerStatus = self.status["openunit"]

            # try powering it up in a few ways. AC adapter or USB 
            if powerStatus == 286:
                self.status["changePowerSource"] = ps.ps3000aChangePowerSource(self.chandle, powerStatus)
            elif powerStatus == 282:
                self.status["changePowerSource"] = ps.ps3000aChangePowerSource(self.chandle, powerStatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])


        enabled = 1
        disabled = 0
        analogue_offset = 0.0

        # Set up channel A
        # handle = self.chandle
        # channel = PS3000A_CHANNEL_A = 0
        # enabled = 1
        # coupling type = PS3000A_DC = 1
        # range = PS3000A_2V = 7
        # analogue offset = 0 V
        self.channel_range = ps.PS3000A_RANGE['PS3000A_2V']
        self.ch_range_2 = ps.PS3000A_RANGE['PS3000A_100MV'] 
        self.ch_range_3 = ps.PS3000A_RANGE['PS3000A_100MV'] 
        self.status["setChA"] = ps.ps3000aSetChannel(self.chandle,
                                                ps.PS3000A_CHANNEL['PS3000A_CHANNEL_A'],
                                                enabled,
                                                ps.PS3000A_COUPLING['PS3000A_DC'],
                                                self.channel_range,
                                                analogue_offset)
        
        #ps.ps3000aGetChannelInformation()
        assert_pico_ok(self.status["setChA"])
        
        # Set up channel B
        # handle = self.chandle
        # channel = PS3000A_CHANNEL_B = 1
        # enabled = 1
        # coupling type = PS3000A_DC = 1
        # range = PS3000A_2V = 7
        # analogue offset = 0 V
        self.status["setChB"] = ps.ps3000aSetChannel(self.chandle,
                                                ps.PS3000A_CHANNEL['PS3000A_CHANNEL_B'],
                                                enabled,
                                                ps.PS3000A_COUPLING['PS3000A_DC'],
                                                self.ch_range_2,
                                                analogue_offset)
        assert_pico_ok(self.status["setChB"])
        

        self.status["setChD"] = ps.ps3000aSetChannel(self.chandle,
                                                ps.PS3000A_CHANNEL['PS3000A_CHANNEL_D'],
                                                enabled,
                                                ps.PS3000A_COUPLING['PS3000A_DC'],
                                                self.ch_range_3,
                                                analogue_offset)
        assert_pico_ok(self.status["setChB"])
        


        # Size of capture
        # we want a lot of these. The more the better. Eventually reached diminishing returns 
        if self._block_mode:
            self.sizeOfOneBuffer = 370*10000
            self.totalSamples = self.sizeOfOneBuffer*1
        else:
            self.sizeOfOneBuffer = 500 # 0000
            self.sizeOfOneBuffer *= 100000

            numBuffersToCapture = 1

            self.totalSamples = self.sizeOfOneBuffer * numBuffersToCapture

        # Create buffers ready for assigning pointers for data collection
        self.bufferAMax = np.zeros(shape=self.sizeOfOneBuffer, dtype=np.int16)
        self.bufferBMax = np.zeros(shape=self.sizeOfOneBuffer, dtype=np.int16)
        self.bufferDMax = np.zeros(shape=self.sizeOfOneBuffer, dtype=np.int16)
        self.memory_segment = 0

        # Set data buffer location for data collection from channel A
        # handle = self.chandle
        # source = PS3000A_CHANNEL_A = 0
        # pointer to buffer max = ctypes.byref(self.bufferAMax)
        # pointer to buffer min = ctypes.byref(bufferAMin)
        # buffer length = maxSamples
        # segment index = 0
        # ratio mode = PS3000A_RATIO_MODE_NONE = 0
        self.status["setDataBuffersA"] = ps.ps3000aSetDataBuffers(self.chandle,
                                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_A'],
                                                            self.bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                            None,
                                                            self.sizeOfOneBuffer,
                                                            self.memory_segment,
                                                            ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersA"])
        
        # Set data buffer location for data collection from channel B
        # handle = self.chandle
        # source = PS3000A_CHANNEL_B = 1
        # pointer to buffer max = ctypes.byref(self.bufferBMax)
        # pointer to buffer min = ctypes.byref(bufferBMin)
        # buffer length = maxSamples
        # segment index = 0
        # ratio mode = PS3000A_RATIO_MODE_NONE = 0
        self.status["setDataBuffersB"] = ps.ps3000aSetDataBuffers(self.chandle,
                                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_B'],
                                                            self.bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                            None,
                                                            self.sizeOfOneBuffer,
                                                            self.memory_segment,
                                                            ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersB"])
        
        self.status["setDataBuffersD"] = ps.ps3000aSetDataBuffers(self.chandle,
                                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_D'],
                                                            self.bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                            None,
                                                            self.sizeOfOneBuffer,
                                                            self.memory_segment,
                                                            ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersD"])
        
        self.sampleInterval = ctypes.c_int32(8)
        self.actualSampleInterval = self.sampleInterval.value

        if self._block_mode:
            self._timebase = 1
            timeIntervalns = ctypes.c_float()
            returnedMaxSamples = ctypes.c_int16()
            n_segments= 1
            status= ps.ps3000aGetTimebase2(self.chandle, self._timebase, self.totalSamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
            print("Using Time interval: {} ns".format(timeIntervalns))

            self.actualSampleInterval = timeIntervalns.value

            assert_pico_ok(status)
            status=ps.ps3000aMemorySegments(self.chandle, n_segments, ctypes.byref(self.totalSamples))
            assert_pico_ok(status)
            status=ps.ps3000aSetNoOfCaptures(self.chandle, n_segments)
    

    def initialze(self):
        chana, chanb, chand = self.measure(True)
        bad = np.min(chana)>=0
        self._good = not bad 
        self.bped = np.mean(chanb)
        self.dped = np.mean(chand)
        self._initialized = True # and (self._good)
    
    def close(self):
                
        # Stop the scope
        # handle = chandle
        self.status["stop"] = ps.ps3000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

        # Disconnect the scope
        # handle = chandle
        self.status["close"] = ps.ps3000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

    def calibrate(self):
        """
            Get trigger times.
            Then chop up waveforms. 
            Sum over each waveform, minus the pedestal
            Make distribution. Run fit. 
            Get threshold
        """
        trigger, chanb, chand = self.measure(True)
        #time_sample = np.linspace(0, (self.totalSamples - 1) * self.sampleIntervalNs, self.totalSamples)
        bins = np.linspace(0, 100, 128)
            
        # we drop this down to just a difference in the sign (-2, 0, +2)
        # but shifted down by the threshold 
        # so +2 is crossing up, -2 is crossing down, 0 is staying above/below 
        crossings = np.diff(np.sign(trigger - 2000))
        #  call the crossing-down ones nothing
        crossings[crossings<0] = 0
        # and get the places where we are crossing up. hit times! 
        crossings = np.where(crossings)[0]

        mon_peaks = []
        rec_peaks = []
        for ic in crossings:
            mon_peaks.append(-1*np.min(chanb[ic:ic+35]))
            rec_peaks.append(-1*np.min(chand[ic:ic+35]))

        mon_data = np.histogram(mon_peaks, bins)[0]
        rec_data = np.histogram(rec_peaks, bins)[0]

        self._good = mon_data[-2]>20 and rec_data[-2]>20
        


        out_data = {
            "bins" : bins.tolist(),
            "monitor":mon_data.tolist(),
            "rec":rec_data.tolist()
        }
        
        _obj = open(os.path.join(os.path.dirname(__file__), "charge.json"), 'wt')
        json.dump(out_data, _obj,indent=4)
        _obj.close()
        return out_data

    def rapidblock(self, give_waves=False):
        status = ps.ps3000aRunBlock(self.chandle, 0, self.totalSamples, self._timebase, 1, None, 0, None, None) 
        assert_pico_ok(status)

        ready= ctypes.c_int(0)
        while ready==ctypes.c_int(0):
            status = ps.ps3000aIsReady(self.chandle, ctypes.byref(ready))
            time.sleep(0.04)

        self.bufferAMax*=0
        self.bufferBMax*=0
        self.bufferDMax*=0
        status = ps.ps3000aSetDataBuffer(self.chandle, ps.PS3000A_CHANNEL['PS3000A_CHANNEL_A'], self.bufferAMax,  self.bufferAMax.size, 0, ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(status)
        status = ps.ps3000aSetDataBuffer(self.chandle, ps.PS3000A_CHANNEL['PS3000A_CHANNEL_B'], self.bufferBMax,  self.bufferBMax.size, 0, ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(status)
        status = ps.ps3000aSetDataBuffer(self.chandle, ps.PS3000A_CHANNEL['PS3000A_CHANNEL_D'], self.bufferDMax,  self.bufferDMax.size, 0, ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
        assert_pico_ok(status)

        overflow = (ctypes.c_int16 * 60)()        
        status = ps.ps3000aGetValuesBulk(self.chandle, ctypes.byref(self.totalSamples), 0, 0,  0, ps.PS3000A_RATIO_MODE["PS3000A_RATIO_MODE_NONE"] , ctypes.byref(overflow))
        
        maxADC = ctypes.c_int16()
        adc2mVChAMax = adc2mV(self.bufferAMax, self.channel_range, maxADC)
        adc2mVChBMax = adc2mV(self.bufferBMax, self.ch_range_2, maxADC)
        adc2mVChDMax = adc2mV(self.bufferDMax, self.ch_range_3, maxADC)


        time_sample = np.linspace(0, (self.totalSamples - 1) * self.actualSampleIntervalNs, self.totalSamples)

        ctime = get_cfd_time(time_sample, adc2mVChAMax, 2000,auto_adjust_ped=False, use_rise=True)[0]
        ntrig = len(ctime)

        montime = get_cfd_time(time_sample, -adc2mVChBMax, thresh,auto_adjust_ped= True, use_rise=False)[0]
        is_good, is_bad = get_valid(ctime, montime, False)
        nmon = np.sum(is_good)
        mon_bad = np.sum(is_bad)*self.mon_lt_good/(1-self.mon_lt_good)
    
        rectime = get_cfd_time(time_sample, -adc2mVChDMax, thresh,auto_adjust_ped= True, use_rise=False)[0]
        is_good, is_bad = get_valid(ctime, rectime, True)
        nrec = np.sum(is_good)
        
        rec_bad = np.sum(is_bad)*self.rec_lt_good/(1-self.rec_lt_good)

        t_total += ntrig
        mon_total +=nmon 
        rec_total +=nrec 
        mon_dark += mon_bad 
        rec_dark += rec_bad


    def measure(self, give_waves = False, raw_data=False):
        if (not self._initialized) and not give_waves:
            self.initialze()

        self.bufferAMax*=0
        self.bufferBMax*=0
        self.bufferDMax*=0

        # Begin streaming mode:
        
        sampleUnits = ps.PS3000A_TIME_UNITS['PS3000A_NS']
        # We are not triggering:
        maxPreTriggerSamples = 0
        autoStopOn = 1
        # No downsampling:
        downsampleRatio = 1
        self.bufferCompleteA = np.zeros(shape=self.totalSamples, dtype=np.int16)
        self.bufferCompleteB = np.zeros(shape=self.totalSamples, dtype=np.int16)
        self.bufferCompleteD = np.zeros(shape=self.totalSamples, dtype=np.int16)
        import time 
        loops = 0
        collection_start = time.time()
        nns = 0

        t_total = 0
        mon_total = 0
        rec_total = 0
        mon_dark = 0
        rec_dark = 0

        while True:
            # need to set a lot of this up between calls 
            start = time.time()
            self.status["runStreaming"] = ps.ps3000aRunStreaming(self.chandle,
                                                            ctypes.byref(self.sampleInterval),
                                                            sampleUnits,
                                                            maxPreTriggerSamples,
                                                            self.totalSamples,
                                                            autoStopOn,
                                                            downsampleRatio,
                                                            ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'],
                                                            self.sizeOfOneBuffer)
            assert_pico_ok(self.status["runStreaming"])

            self.actualSampleInterval = self.sampleInterval.value
            self.actualSampleIntervalNs = self.actualSampleInterval *1


            self.nextSample = 0
            self.autoStopOuter = False
            self.wasCalledBack = False
            # We need a big buffer, not registered with the driver, to keep our complete capture in.
            def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
                self.wasCalledBack = True
                destEnd = self.nextSample + noOfSamples
                sourceEnd = startIndex + noOfSamples
                self.bufferCompleteA[self.nextSample:destEnd] = self.bufferAMax[startIndex:sourceEnd]
                self.bufferCompleteB[self.nextSample:destEnd] = self.bufferBMax[startIndex:sourceEnd]
                self.bufferCompleteD[self.nextSample:destEnd] = self.bufferDMax[startIndex:sourceEnd]
                self.nextSample += noOfSamples
                if autoStop:
                    self.autoStopOuter = True


            # Convert the python function into a C function pointer.
            cFuncPtr = ps.StreamingReadyType(streaming_callback)

            # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
            while self.nextSample < self.totalSamples and not self.autoStopOuter:
                self.wasCalledBack = False
                self.status["getStreamingLastestValues"] = ps.ps3000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
                if not self.wasCalledBack:
                    # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
                    # again.
                    time.sleep(0.01)
            assert_pico_ok(self.status["getStreamingLastestValues"])

            # Find maximum ADC count value
            # handle = self.chandle
            # pointer to value = ctypes.byref(maxADC)
            maxADC = ctypes.c_int16()
            self.status["maximumValue"] = ps.ps3000aMaximumValue(self.chandle, ctypes.byref(maxADC))
            assert_pico_ok(self.status["maximumValue"])

            # Convert ADC counts data to mV
            conv_t = time.time()
            if give_waves:
                if raw_data:
                    return self.bufferCompleteA, self.bufferCompleteB, self.bufferCompleteD
                adc2mVChAMax = adc2mV(self.bufferCompleteA, self.channel_range, maxADC)
                adc2mVChBMax = adc2mV(self.bufferCompleteB, self.ch_range_2, maxADC)
                adc2mVChDMax = adc2mV(self.bufferCompleteD, self.ch_range_3, maxADC)
                return adc2mVChAMax, adc2mVChBMax, adc2mVChDMax

            else:
                adc2mVChAMax = adc2mV(self.bufferCompleteA, self.channel_range, maxADC)
                adc2mVChBMax = adc2mV(self.bufferCompleteB, self.ch_range_2, maxADC) - self.bped
                adc2mVChDMax = adc2mV(self.bufferCompleteD, self.ch_range_3, maxADC) - self.dped



        #    adc2mVChAMax = self.bufferCompleteA
        #    adc2mVChBMax = self.bufferCompleteB
        #    adc2mVChDMax = self.bufferCompleteD
            conv_t_end = time.time()
            # Create time data
            time_sample = np.linspace(0, (self.totalSamples - 1) * self.actualSampleIntervalNs, self.totalSamples)

            ctime = get_cfd_time(time_sample, adc2mVChAMax, 2000,auto_adjust_ped=False, use_rise=True)[0]
            ntrig = len(ctime)

            montime = get_cfd_time(time_sample, -adc2mVChBMax, thresh,auto_adjust_ped= True, use_rise=False)[0]
            is_good, is_bad = get_valid(ctime, montime, False)
            nmon = np.sum(is_good)
            mon_bad = np.sum(is_bad)*self.mon_lt_good/(1-self.mon_lt_good)
        
            rectime = get_cfd_time(time_sample, -adc2mVChDMax, thresh,auto_adjust_ped= True, use_rise=False)[0]
            is_good, is_bad = get_valid(ctime, rectime, True)
            nrec = np.sum(is_good)
            
            rec_bad = np.sum(is_bad)*self.rec_lt_good/(1-self.rec_lt_good)

            t_total += ntrig
            mon_total +=nmon 
            rec_total +=nrec 
            mon_dark += mon_bad 
            rec_dark += rec_bad

            if False: #np.abs( 1- (nmon/nrec)/(np.array(mon_total)/np.array(rec_total)))>0.2:
                print("SPIKE")
                all_data = {
                    "time":time_sample,
                    "chana":adc2mVChAMax,
                    "chanb":adc2mVChBMax,
                    "chand":adc2mVChDMax
                }
                dfile = h5.File("waveforms.h5", 'w')
                for key in all_data:
                    dfile.create_dataset(key, data=all_data[key])
                dfile.close()

            end = time.time()

            # the number of those crossing times is the number of pulses! 
                        
            nns += len(adc2mVChAMax)*8
                
            loops +=1
            if (time.time() - collection_start)>self.collection_time:
                break
                
        return t_total, mon_total, rec_total, int(mon_dark), int(rec_dark)

