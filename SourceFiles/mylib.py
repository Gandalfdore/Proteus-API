# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 16:44:53 2023

@author: Moon_Penguin
"""

from teproteus import TEProteusAdmin as TepAdmin
from teproteus import TEProteusInst as TepInst
import numpy as np
import matplotlib.pyplot as plt

def connection_func ():
    
    print("\n===CONNECTING===")

        # Connect to instrument via PXI
    admin = TepAdmin()   

    # Get list of available PXI slots
    slot_ids = admin.get_slot_ids()

    # Assume that at least one slot was found
    sid = slot_ids[0]  # this is the system ID, the port trough which we access the Proteus

    # Open a single-slot instrument:
    inst = admin.open_instrument(slot_id=sid)
    
    inst.default_paranoia_level = 2

    # Get the instrument's *IDN
    resp = inst.send_scpi_query('*IDN?')
    print('Connected to: ' + resp)

    # Get the model name
    model = inst.send_scpi_query(":SYST:iNF:MODel?")
    print("Model: " + model)

    # Infer the natural DAC waveform format
    if 'P9082' in model:
        dac_mode = 8
    else:
        dac_mode = 16
    print("DAC waveform format: {0} bits-per-point".format(dac_mode))

    if dac_mode == 16:
        max_dac = 65535  # = (2**16 - 1)  ,because the momory slots are 16bit ones (have 16bit vertical resolution) 
        data_type = np.uint16
    else:
        max_dac = 255
        data_type = np.uint8

    half_dac = max_dac // 2.0
    
    print("===CONNECTION ESTABLISHED===")
    print("======================")
    
    print("\n===SYSTEM'S INFORMATION===")

    print('Max DAC wave-point level: {0}'.format(max_dac))
    print('Half DAC wave-point level: {0}'.format(half_dac))

    # Get number of channels
    resp = inst.send_scpi_query(":INST:CHAN? MAX")
    print("Number of channels: " + resp)
    num_channels = int(resp)

    # Get the maximal number of segments
    resp = inst.send_scpi_query(":TRACe:SELect:SEGMent? MAX")
    print("Max segment number: " + resp)
    max_seg_number = int(resp)

    # Get the available memory in bytes of wavform-data (per DDR):
    resp = inst.send_scpi_query(":TRACe:FREE?")
    arbmem_capacity = int(resp)
    print("Available memory per DDR: {0:,} wave-bytes".format(arbmem_capacity))
    
    print("======================")
    
    return dac_mode, max_dac, sid, data_type


#####################################################################################

def system_info_func(max_dac, sid):  
    admin = TepAdmin()  ### decalring a shortcut to send SCPY commands to the machine
    inst = admin.open_instrument(slot_id=sid)  ### decalring a shortcut to send SCPY commands to the machine
    
    half_dac = max_dac // 2.0
    
    print("\n===SYSTEM'S INFORMATION===")

    print('Max DAC wave-point level: {0}'.format(max_dac))
    print('Half DAC wave-point level: {0}'.format(half_dac))

    # Get number of channels
    resp = inst.send_scpi_query(":INST:CHAN? MAX")
    print("Number of channels: " + resp)
    num_channels = int(resp)

    # Get the maximal number of segments
    resp = inst.send_scpi_query(":TRACe:SELect:SEGMent? MAX")
    print("Max segment number: " + resp)
    max_seg_number = int(resp)

    # Get the available memory in bytes of wavform-data (per DDR):
    resp = inst.send_scpi_query(":TRACe:FREE?")
    arbmem_capacity = int(resp)
    print("Available memory per DDR: {0:,} wave-bytes".format(arbmem_capacity))
    
    print("======================")
    

    return None

#####################################################################################

def initialization_func(channel_numb, sid, SCLK):
    admin = TepAdmin()
    inst = admin.open_instrument(slot_id=sid)
    
    # Several initializations ..

    inst.default_paranoia_level = 2

    inst.send_scpi_cmd('*CLS; *RST')   #clear the error list and reset the machine to its default state
    inst.send_scpi_cmd(':INST:CHAN {0}'.format(channel_numb)) 
    inst.send_scpi_cmd(':FREQ:RAST {0}'.format(SCLK))  #refer to a channel of your liking 
    inst.send_scpi_cmd(':INIT:CONT ON')
    inst.send_scpi_cmd(':TRAC:DEL:ALL')  # delete all the defined segments on the channel
    resp = inst.send_scpi_query(':SYST:ERR?')
    
    
    print("\n===INITIALIZATION OF CHANNEL {0} DONE===".format(channel_numb))
    print("ERRORS:", resp)

    return None

#####################################################################################


def sin_func (frequency, phase_shift, SCLK, amplitude = 1, show_plot = True):
    """This function gives a sinus signal.
    TAKES: frequency in [Hz]
        Phase shift in radians
        Amplitude b/w [-1,1]
        SCLK - the sampling clock of the proteus
        Show plot - whether to show a plot of the function or not
    RETURNS: The array that represents the signal
        The segment length of the waveform
    """
    SCLK = SCLK/2.5
    
    seglen = SCLK/frequency ### how many DAC events needed to form one period of this function
    print ("original seglen:", seglen)
    seglen = int( formatter (seglen) [0] )
    print ("formated seglen:", seglen)
    
    x = np.linspace(start=0, stop=2 * np.pi, num=seglen, endpoint=False) 
    
    y = amplitude * np.sin(x + phase_shift)
    
    if show_plot == True:
        plt.plot(x,y)
        plt.xlabel('Radians') 
        plt.ylabel('Amplitude') 
        plt.title('Sinus')
    
    return y, seglen

#####################################################################################


def blank_func (SCLK, DC_bias = 0, show_plot = False):
    """This function gives DC signal. It is by default 0V to represent no signal in the system.
    TAKES: frequency in [Hz]
        SCLK - the sampling clock of the proteus
        DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
        Show plot - whether to show a plot of the function or not
    RETURNS: The array that represents the signal
        The segment length of the waveform
    """
    
    seglen = 2048  ### this is about 82 [ns]
    
    x = np.linspace(start=0, stop=1, num=seglen, endpoint=False)
    y= DC_bias*x
    
    if show_plot == True:
        plt.plot(x,y)
    
    return y, seglen

#####################################################################################

def digital_conv_func (array, max_dac, data_type):
    """This an arbitrary array and transforms its values, so they would fit within the range of the DAC.
    TAKES: An array with values between [-1 and 1]
           The range of the DAC
    RETURNS: The transformed array in a binary format"""
    
    half_dac = max_dac // 2
    
    array = (array + 1.0) * half_dac
    array = np.round(array)
    array = np.clip(array, 0, max_dac)
    wave = array.astype(data_type)
    
    return wave

#####################################################################################

def prepare_gaussian_pulse (sigma, width_over_sigma, frequency, SCLK, DUC_INTERP, max_dac, show_plot = True):
    
    SCLK = SCLK/2.5
    
    half_dac = max_dac // 2

    period = 1/frequency
    delta_t = 1/SCLK ### how much time between each two sequential signal points
    sigma_numerical = sigma/delta_t  ### how many datapoints between each two sequential signal points

    print ("period = {0}[ns]".format(period*1e9))
    print ("sigma = {0}[ns]".format(sigma*1e9))
    print ("sigma_num = {0} datapoints ".format(sigma_numerical))

    width = width_over_sigma*sigma_numerical # time width of the gaussian pulse, the width of the pulse terminates at 5*sigma, this is made by convention, it can be change to be (arbitrary number*sigma)
    print (width_over_sigma, sigma_numerical, width)
    seglen_gauss = int(width)
    print("Gaussian Segement length = {0} datapoints\n".format(seglen_gauss))
    print("Gaussian Segement length (in time) = {0} [ns]]".format(width_over_sigma*sigma*1e9))

################# WARNINGS AND CHECKS #######################

    if 5*period > sigma:
        print ("\n!WARNING! Sigma is comparable to the period of the oscillation\n")
    
    seglen_gauss, normalization_factor = formatter(seglen_gauss)

#     seglen_gauss_old = seglen_gauss
#     n = -32.0 + seglen_gauss/64.
    
#     if seglen_gauss < 2048:
        
#         print ("\n!WARNING! The segment of the defined signal ({0} points) is less then the minium necessary length for a Proteus signal (2048 points)".format(seglen_gauss))
#         print ("-----------Will edit the signal automatically to reach 2048 points (~82[ns])-----------\n")
        
#         seglen_gauss *= int(2048 / seglen_gauss)
#         seglen_gauss += int(2048 % seglen_gauss)
#         normalization_factor = seglen_gauss/seglen_gauss_old #to make the gausian from [0 to x] to [0 to 1] 
        
#         print("\nGaussian Segement length (after correction) = {0} datapoints".format(seglen_gauss))
        
#     if n.is_integer() == False:
        
#         print ("\n!WARNING! The segment of the defined signal ({0} points) does not comply with the format of the possible data chunk for a signal, which is datalength = ( 64 * (32 + n)), where n is an integer ".format(seglen_gauss))
#         print ("-----------Will edit the signal automatically to suit the # of points-----------\n")
        
#         n = int(n)
#         seglen_gauss = 64 * (32 + n)
#         normalization_factor = seglen_gauss/seglen_gauss_old #to make the gausian from [0 to x] to [0 to 1] 
#         print("\nGaussian Segement length (after correction) = {0} datapoints".format(seglen_gauss))
        
#     else:
#         normalization_factor = 1


        
############################################################
    
###########################################################

    t = np.linspace(-1, 1, seglen_gauss, endpoint=False)
    
    ss = sigma_numerical / seglen_gauss

    GAUS_FC = frequency * seglen_gauss * DUC_INTERP /2 / SCLK
    
    print('Gaussian frequency = {0}[Mhz]'.format(SCLK * 2 * GAUS_FC / seglen_gauss / 1e6/ DUC_INTERP))  # the actual frequency of the sin wave in the gaussian

    ####################
    sin = np.sin(2*np.pi*t*GAUS_FC)
    cos = np.cos(2*np.pi*t*GAUS_FC)
    gaussian = (1/ss/np.sqrt(2*np.pi)/2) * np.exp(-(t**2)/2/(ss**2)) / normalization_factor
    (i) = sin*gaussian
    (q) = cos*gaussian
    ####################
    
    if show_plot == True:
        plt.plot(t, (i), '-',t, (q), '-')
        plt.legend(['I','Q'])



    
    return (i), (q), seglen_gauss


###########################################################

def download_signal(segnum, seglen, channb, wave, sid):
    """This function downloads the waveforms down to the Proteus unit.
    TAKES:
        Segnum - assigned reference number of the segment in which we put the waveform
        Seglen - number of segments of the memory to assign for the waveform
        Chanb - the number of the channel, could take values - [1,2,3,4]
        Wave - a binary array with the data of the waveform
        
    RETURNS: Absolutely nothing :)
    """
    
    admin = TepAdmin()   
    inst = admin.open_instrument(slot_id=sid)

    # Select channel
    cmd = ':INST:CHAN {0}'.format(channb)
    inst.send_scpi_cmd(cmd)

    # Define segment
    cmd = ':TRAC:DEF {0}, {1}'.format(segnum, seglen)   # here we define the segment length so we don't need to put a header at TRAC:DATA ????
    inst.send_scpi_cmd(cmd)

    # Select the segment
    cmd = ':TRAC:SEL {0}'.format(segnum)
    inst.send_scpi_cmd(cmd)

    # Send the binary-data:
    inst.write_binary_data(':TRAC:DATA', wave)

    resp = inst.send_scpi_query(':SYST:ERR?')
    resp = resp.rstrip()
    if not resp.startswith('0'):
        print('ERROR: "{0}" after writing binary values'.format(resp))

    # Play the specified segment at the selected channel:
    cmd = ':SOUR:FUNC:MODE:SEGM {0}'.format(segnum)
    inst.send_scpi_cmd(cmd)

    # Turn on the output of the selected channel:
    inst.send_scpi_cmd(':OUTP ON')

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp, "{0} downloaded".format(segnum))
    
    del wave
    
    return None


###############################################################

def formatter (num):
    """This function take an arbitrary number and returns the closest to it number in the format: ( 64 * (32 + n)), also the minumum number is 20.
    TAKES: number
    RETURNS: the formatted number 
             the normalization factor = fomatted number / number"""
    
    num_old = num
    n = -32.0 + num/64.
        
    if n.is_integer() == False or n < 0:
        
        print ("\n!WARNING! The segment of the defined signal ({0} points) does not comply with the format of the possible data chunk for a signal, which is ||| datalength = ( 64 * (32 + n)) |||, where n is an integer.".format(num))
        print ("-----------Will edit the signal automatically to suit the # of points-----------\n")
        
        n = int(n)
        num = 64 * (32 + n)
        normalization_factor = num/num_old #to make the gausian from [0 to x] to [0 to 1] 
        
    else:
        normalization_factor = 1
        
    return (num, normalization_factor)
