
from teproteus import TEProteusAdmin as TepAdmin
from teproteus import TEProteusInst as TepInst
import numpy as np
import matplotlib.pyplot as plt
import time


def digitizer_setup(inst, DIG_SCLK, DDC_NCO, time_delay):
    """
    This function sets up the digitizer setting for IQ operation.
    
    INUT:
        inst - the proteus instance
        DIG_SCLK - sampling clock rate of the digitizer (DAC), max value is 2.7e9
        DDC_NCO - the LO of the demodulator (make ideally the same as Source NCO)
        time_delay - delay until the digitizer is to be triggered
    
    OUTPUT:
        None
    
    """

    inst.send_scpi_cmd(':DIG:MODE DUAL')
    inst.send_scpi_cmd(':DIG:CHAN:RANGe HIGH')

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)


    # set the sampling rate for the Digitizer (or ADC)
    inst.send_scpi_cmd(':DIG:FREQ {0}'.format(DIG_SCLK))

    # Set DDC mode to complex
    resp = inst.send_scpi_cmd(':DIG:DDC:MODE COMP')
    print(resp)

    resp = inst.send_scpi_cmd(':DIG:DDC:DEC X16')
    print(resp)

    resp = inst.send_scpi_query(':DIG:DDC:CLKS DIG')  # !!! doesn't work, must be "...CLKS AWG"
    print(resp)

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    ###########################################

    #This is to be used only for mode COMPLEX (not mode REAL)
    # Set center frequency of channel 1 to 100MHz  
    # DDC_NCO = 1e9   # !!!!! use the frequency of you pulse here !!!!!
    inst.send_scpi_cmd(':DIG:DDC:CFR1 {0}'.format(DDC_NCO))

    ###########################################

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    # Enable capturing data from channel 1
    inst.send_scpi_cmd(':DIG:CHAN:SEL 1')
    inst.send_scpi_cmd(':DIG:CHAN:STATE ENAB')

    # # Select the internal-trigger as start-capturing trigger:
    # inst.send_scpi_cmd(':DIG:TRIG:SOURCE CPU') 

    # Select the task trigger as start-capturing trigger:
    inst.send_scpi_cmd(':DIG:TRIG:SOURCE TASK1')

    # Set Trigger AWG delay to 0
    inst.send_scpi_cmd(':DIG:TRIG:AWG:TDEL {0}'.format(time_delay))  ##!!! Don't know if it should be like this

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)
    
    return None

#=============================================================#
    #=============================================================#
    #=============================================================#


def framer(inst, numframes = int, framelen = int):
    
    """
    
    This function defines the number of frames and the length of each frame on would like to use for capturing of the digitized data.
    
    INUT:
        inst - the proteus instance
        numframes - the number of frames 
        framelen - the length in datapoints for each frame
    
    OUTPUT:
        None
    
    """
    
    # Allocate four frames of 4800 samples
    numframes, framelen = 1, 10*4800
    cmd = ':DIG:ACQuire:FRAM:DEF {0},{1}'.format(numframes, framelen)
    inst.send_scpi_cmd(cmd)

    # Select which frames are filled with captured data (all frames in this example)
    inst.send_scpi_cmd(':DIG:ACQ:FRAM:CAPT:ALL');

    # clean memory
    inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')

    resp = inst.send_scpi_cmd(':DIG:DATA:FORM?')
    print (resp)


    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    resp = inst.send_scpi_query(':DIG:DDC:DEC?')  # try with this maybe
    print(resp)
    
    return None

#=============================================================#
    #=============================================================#
    #=============================================================#


def capturer(inst):
    """    
    This function captures the data in the frames preselected.
    
    INUT:
        inst - the proteus instance
    
    OUTPUT:
        None
        
    """
    
    # # Clean memory 
    # inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')  ## !!!! try with and without this, when everything is running OK
    # time.sleep(1)

    # Stop the digitizer's capturing machine (to be on the safe side)
    inst.send_scpi_cmd(':DIG:INIT OFF')
    time.sleep(0.1)

    # Start the digitizer's capturing machine ###################### START CAPTURE
    inst.send_scpi_cmd(':DIG:INIT ON')

    for i in range (1,1000):
        delta_t = 1/100
        time.sleep(delta_t) # if we wait long enough time the machine captures a signal
        resp = inst.send_scpi_query(':DIG:ACQuire:FRAM:STAT?')
        if resp[6:] == '1':  # maybe 1 comes as a float, check it
            print('Response:',resp, 'Time:',delta_t*i)
            break


    # Stop the digitizer's capturing machine (to be on the safe side) ################# STOP CAPTURE
    inst.send_scpi_cmd(':DIG:INIT OFF')

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)
    
    return None

#=============================================================#
    #=============================================================#
    #=============================================================#


def IQ_data_extractor(inst, channel = int, numframes = int, framelen = int):
    
    """    
    This takes the data from the memory, then extracts the I and Q components from it.
    
    INUT:
        inst - the proteus instance
        channel - the channel to take the data from
        numframes
        framelen
    
    OUTPUT:
        I data array
        Q data array
        
    """
    
    # Choose what to read 
    # (only the frame-data without the header in this example)
    inst.send_scpi_cmd(':DIG:DATA:TYPE FRAM')

    # Choose which frames to read (all in this example)
    inst.send_scpi_cmd(':DIG:DATA:SEL ALL')

    # Get the total data size (in bytes)
    resp = inst.send_scpi_query(':DIG:DATA:SIZE?')
    num_bytes = np.uint32(resp)
    print('Total size in bytes: ' + resp)
    print()

    # Read the data that was captured by channel 1:
    inst.send_scpi_cmd(':DIG:CHAN:SEL {0}'.format(channel))

    #wavlen = num_bytes // 2  
    wavlen = num_bytes // 4  # for the DUC mode !!!!!

    #wav1 = np.zeros(wavlen, dtype=np.uint16)
    wav1 = np.zeros(wavlen, dtype=np.uint32) # for the DUC mode !!!!!
    
    # Get the data out of the memory in the proper format
    rc = inst.read_binary_data(':DIG:DATA:READ?', wav1, num_bytes)

    # # Read the data that was captured by channel 2:
    # inst.send_scpi_cmd(':DIG:CHAN:SEL 2')

    # wav2 = np.zeros(wavlen, dtype=np.uint16)
    # rc = inst.read_binary_data(':DIG:DATA:READ?', wav2, num_bytes)

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)
    
    totlen = int(numframes * framelen /2)
    x = range(totlen)

    wave_i = np.zeros(totlen, dtype=np.int32)
    wave_q = np.zeros(totlen, dtype=np.int32)
    
    # They are interleved, thus we need to separate hem
    wave_i = wav1[::2]  
    wave_q = wav1[1::2]
    
    # Make them in format that allows negative and positive values
    wave_i = wave_i.astype('int32')
    wave_q = wave_q.astype('int32')
    
    # 16384 is the 0V point of the digitizer
    wave_i = wave_i - 16384
    wave_q = wave_q - 16384
    
    return wave_i, wave_q