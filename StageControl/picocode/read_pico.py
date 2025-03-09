nextSample = 0
autoStopOuter = False
wasCalledBack = False

def main():
    import os 
    import ctypes
    import numpy as np
    from picosdk.ps3000a import ps3000a as ps
    import matplotlib.pyplot as plt
    from picosdk.functions import adc2mV, assert_pico_ok
    import time
    from scipy.signal import find_peaks
    from StageControl.picocode.utils import get_valid

    DEBUG = False
    HEIGHT = False

    collection_time = 30
    thresh = 5.0
    bped = -0.55
    dped = -1.0
    channelInputRanges = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]
    t_total = 0
    mon_total = 0
    rec_total = 0

    b_heights = []
    d_heights = []

    def adc2mV(buffer, rang, maxADC):
        """
        Rewrote the picoscode version of this to use vectorized numpy math
        Got some 100x speed improvements 
        """
        return (buffer.astype(float)*channelInputRanges[rang])/maxADC.value 


    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}

    # Open PicoScope 5000 Series device
    status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None)

    try:
        assert_pico_ok(status["openunit"])
    except: # PicoNotOkError:

        powerStatus = status["openunit"]

        if powerStatus == 286:
            status["changePowerSource"] = ps.ps3000aChangePowerSource(chandle, powerStatus)
        elif powerStatus == 282:
            status["changePowerSource"] = ps.ps3000aChangePowerSource(chandle, powerStatus)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])


    enabled = 1
    disabled = 0
    analogue_offset = 0.0

    # Set up channel A
    # handle = chandle
    # channel = PS3000A_CHANNEL_A = 0
    # enabled = 1
    # coupling type = PS3000A_DC = 1
    # range = PS3000A_2V = 7
    # analogue offset = 0 V
    channel_range = ps.PS3000A_RANGE['PS3000A_2V']
    ch_range_2 = ps.PS3000A_RANGE['PS3000A_20MV'] +2
    status["setChA"] = ps.ps3000aSetChannel(chandle,
                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_A'],
                                            enabled,
                                            ps.PS3000A_COUPLING['PS3000A_DC'],
                                            channel_range,
                                            analogue_offset)
    assert_pico_ok(status["setChA"])

    # Set up channel B
    # handle = chandle
    # channel = PS3000A_CHANNEL_B = 1
    # enabled = 1
    # coupling type = PS3000A_DC = 1
    # range = PS3000A_2V = 7
    # analogue offset = 0 V
    status["setChB"] = ps.ps3000aSetChannel(chandle,
                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_B'],
                                            enabled,
                                            ps.PS3000A_COUPLING['PS3000A_DC'],
                                            ch_range_2,
                                            analogue_offset)
    assert_pico_ok(status["setChB"])

    status["setChD"] = ps.ps3000aSetChannel(chandle,
                                            ps.PS3000A_CHANNEL['PS3000A_CHANNEL_D'],
                                            enabled,
                                            ps.PS3000A_COUPLING['PS3000A_DC'],
                                            ch_range_2,
                                            analogue_offset)
    assert_pico_ok(status["setChB"])


    # Size of capture
    # we want a lot of these. The more the better. Eventually reached diminishing returns 
    sizeOfOneBuffer = 500 # 0000
    if not DEBUG:
        sizeOfOneBuffer *= 10000

    numBuffersToCapture = 10

    totalSamples = sizeOfOneBuffer * numBuffersToCapture

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    bufferDMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    memory_segment = 0

    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = PS3000A_CHANNEL_A = 0
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS3000A_RATIO_MODE_NONE = 0
    status["setDataBuffersA"] = ps.ps3000aSetDataBuffers(chandle,
                                                         ps.PS3000A_CHANNEL['PS3000A_CHANNEL_A'],
                                                         bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                         None,
                                                         sizeOfOneBuffer,
                                                         memory_segment,
                                                         ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersA"])

    # Set data buffer location for data collection from channel B
    # handle = chandle
    # source = PS3000A_CHANNEL_B = 1
    # pointer to buffer max = ctypes.byref(bufferBMax)
    # pointer to buffer min = ctypes.byref(bufferBMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS3000A_RATIO_MODE_NONE = 0
    status["setDataBuffersB"] = ps.ps3000aSetDataBuffers(chandle,
                                                         ps.PS3000A_CHANNEL['PS3000A_CHANNEL_B'],
                                                         bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                         None,
                                                         sizeOfOneBuffer,
                                                         memory_segment,
                                                         ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersB"])

    status["setDataBuffersD"] = ps.ps3000aSetDataBuffers(chandle,
                                                         ps.PS3000A_CHANNEL['PS3000A_CHANNEL_D'],
                                                         bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                         None,
                                                         sizeOfOneBuffer,
                                                         memory_segment,
                                                         ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersD"])

    # Begin streaming mode:
    sampleInterval = ctypes.c_int32(8)
    sampleUnits = ps.PS3000A_TIME_UNITS['PS3000A_NS']
    # We are not triggering:
    maxPreTriggerSamples = 0
    autoStopOn = 1
    # No downsampling:
    downsampleRatio = 1
    bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
    bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
    bufferCompleteD = np.zeros(shape=totalSamples, dtype=np.int16)
    import time 
    loops = 0
    collection_start = time.time()
    nns = 0
    while True:

        # need to set a lot of this up between calls 
        start = time.time()
        status["runStreaming"] = ps.ps3000aRunStreaming(chandle,
                                                        ctypes.byref(sampleInterval),
                                                        sampleUnits,
                                                        maxPreTriggerSamples,
                                                        totalSamples,
                                                        autoStopOn,
                                                        downsampleRatio,
                                                        ps.PS3000A_RATIO_MODE['PS3000A_RATIO_MODE_NONE'],
                                                        sizeOfOneBuffer)
        assert_pico_ok(status["runStreaming"])

        actualSampleInterval = sampleInterval.value
        actualSampleIntervalNs = actualSampleInterval *1


        global nextSample, autoStopOuter, wasCalledBack
        nextSample = 0
        autoStopOuter = False
        wasCalledBack = False
        # We need a big buffer, not registered with the driver, to keep our complete capture in.
        def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
            global nextSample, autoStopOuter, wasCalledBack
            wasCalledBack = True
            destEnd = nextSample + noOfSamples
            sourceEnd = startIndex + noOfSamples
            bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
            bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
            bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
            nextSample += noOfSamples
            if autoStop:
                autoStopOuter = True


        # Convert the python function into a C function pointer.
        cFuncPtr = ps.StreamingReadyType(streaming_callback)

        # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
        while nextSample < totalSamples and not autoStopOuter:
            wasCalledBack = False
            status["getStreamingLastestValues"] = ps.ps3000aGetStreamingLatestValues(chandle, cFuncPtr, None)
            if not wasCalledBack:
                # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
                # again.
                time.sleep(0.01)


        # Find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        maxADC = ctypes.c_int16()
        status["maximumValue"] = ps.ps3000aMaximumValue(chandle, ctypes.byref(maxADC))
        assert_pico_ok(status["maximumValue"])

        # Convert ADC counts data to mV
        conv_t = time.time()
        adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
        adc2mVChBMax = adc2mV(bufferCompleteB, ch_range_2, maxADC) -bped
        adc2mVChDMax = adc2mV(bufferCompleteD, ch_range_2, maxADC)-dped

    #    adc2mVChAMax = bufferCompleteA
    #    adc2mVChBMax = bufferCompleteB
    #    adc2mVChDMax = bufferCompleteD
        conv_t_end = time.time()
        # Create time data
        time_sample = np.linspace(0, (totalSamples - 1) * actualSampleIntervalNs, totalSamples)
        
        # we drop this down to just a difference in the sign (-2, 0, +2)
        # but shifted down by the threshold 
        # so +2 is crossing up, -2 is crossing down, 0 is staying above/below 
        crossings = np.diff(np.sign(adc2mVChAMax - 2000))
        #  call the crossing-down ones nothing
        crossings[crossings<0] = 0
        # and get the places where we are crossing up. hit times! 
        crossings = np.where(crossings)
        ctime = time_sample[crossings[0]]

        ntrig = len(ctime)

        # repeat for all channels  
        crossings = np.diff(np.sign(-adc2mVChBMax - thresh))
        crossings[crossings>0]=0
        crossings = np.where(crossings)

        rectime = time_sample[crossings[0]]
        is_good = get_valid(ctime, rectime, False).astype(int)
        
        nmon = np.sum(is_good)
       
        crossings = np.diff(np.sign(-adc2mVChDMax - thresh))
        crossings[crossings>0]=0
        crossings = np.where(crossings)

        montime = time_sample[crossings[0]]
        is_good = get_valid(ctime, montime, True).astype(int)
        
        nrec = np.sum(is_good)

        t_total += ntrig
        mon_total +=nmon
        rec_total +=nrec

        end = time.time()

        # the number of those crossing times is the number of pulses! 
                    
        nns += len(adc2mVChAMax)*8
            
        loops +=1
        if (time.time() - collection_start)>collection_time:
            break

    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps3000aStop(chandle)
    assert_pico_ok(status["stop"])

    # Disconnect the scope
    # handle = chandle
    status["close"] = ps.ps3000aCloseUnit(chandle)
    assert_pico_ok(status["close"])

    return t_total, mon_total, rec_total

if __name__=="__main__":
    t, m, r = main()


