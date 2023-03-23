import os
from teproteus import TEProteusAdmin as TepAdmin
from teproteus import TEProteusInst as TepInst
import numpy as np
import matplotlib.pyplot as plt


    #=============================================================#
    #=============================================================#
    #=============================================================#


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



    #=============================================================#
    #=============================================================#
    #=============================================================#

    
    
def formatter (num):
    """This function take an arbitrary number and returns the closest to it number in the format: ( 64 * (32 + n)), also the minumum number is 20.
    TAKES: 
        Integer (or float) number
    RETURNS: 
        The formatted number 
        The normalization factor = fomatted number / number
    """
    
    num_old = num
    n = -32.0 + num/64.
        
    if n.is_integer() == False or n < 0:
        
        print ("\n!WARNING! The segment of the defined signal ({0} points) does not comply with the format of the possible data chunk for a signal, which is ||| datalength = ( 64 * (32 + n)) |||, where         n is an integer.".format(num))
        print ("-----------Will edit the signal automatically to suit the # of points-----------\n")
        
        n = int(n)
        num = 64 * (32 + n)
        normalization_factor = num/num_old #to make the gausian from [0 to x] to [0 to 1] 
        
    else:
        normalization_factor = 1
        
    return (num, normalization_factor)



    #=============================================================#
    #=============================================================#
    #=============================================================#




def quitter (sid):
    """This function terminates the session with the Proteus.
    INPUT: 
        #The 'inst' instance 
        The sID number
    OUTPUT: 
        None
    """
    
    # Disconnect
    admin = TepAdmin()
    inst = admin.open_instrument(slot_id=sid)

    inst.close_instrument()
    admin.close_inst_admin()
    
    return None




    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
def download_func (inst, wave, channel, segment):

    """This function downloads the waveforms down to the Proteus unit.
    TAKES:
        inst - the instance of the open instrument command
        Wave - a binary array with the data of the waveform
        Channel - the number of the channel, could take values - [1,2,3,4]
        Segment - assigned reference number of the segment in which we put the waveform

    RETURNS: 
        Absolutely nothing :) (Except many good wishes)
    """

    # download it to segment 1 of channel 1
    inst.send_scpi_cmd(':INST:CHAN {0}'.format(channel))
    inst.send_scpi_cmd(':TRAC:DEF {0},'.format(segment) + str(wave.size))
    inst.send_scpi_cmd(':TRAC:SEL {0}'.format(segment))   # we are saying here basically "create for me a segment of memory with such and such length"

    print('wave size: {0}'.format(wave.size))
    # download the waveform to the selected segment
    inst.write_binary_data(':TRAC:DATA', wave)  # put your wave there

    inst.send_scpi_cmd(':SOUR:FUNC:MODE:SEGM {0}'.format(segment))
    # inst.send_scpi_cmd(':SOUR:VOLT 0.5')  ### set voltage 
    inst.send_scpi_cmd(':OUTP ON')

    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    del wave

    return None




    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    
def task_starter (inst, channel):
    """Here we instantiate the channel and all the tasks put in it.

    INPUT:
        inst - the instance of the open instrument command
        channel - the number of the channel, could take values - [1,2,3,4]

    OUTPUT: 
        None
    """

    # define the operation mode
    cmd = 'FUNC:MODE TASK'
    inst.send_scpi_cmd(cmd)

    # point to the channel
    cmd = ':INST:CHAN {0}'.format(channel)
    inst.send_scpi_cmd(cmd)

    # start the output
    cmd = ':OUTP ON'
    inst.send_scpi_cmd(cmd)

    # see if any errors came up
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    
    
    