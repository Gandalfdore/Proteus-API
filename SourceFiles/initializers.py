import os
from teproteus import TEProteusAdmin as TepAdmin
from teproteus import TEProteusInst as TepInst
import numpy as np



def connection_func ():
    
    print("\n=========CONNECTING=========")

    # Connect to instrument via PXI
    pid = os.getpid()
    print('process id {0}'.format(pid))
    
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

       
    print("===CONNECTION ESTABLISHED===")
    print("============================")
    
    print("\n===SYSTEM'S INFORMATION===")
    
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
    
    print("==========READY============")
    print("===========================")
    
    return dac_mode, max_dac, sid, data_type, inst


    #=============================================================#
    #=============================================================#
    #=============================================================#

def system_info_func(max_dac, inst):  
    
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

    #=============================================================#
    #=============================================================#
    #=============================================================#

def initialization_func(channel_numb, inst, SCLK):
    
    # Several initializations ..

#     inst.default_paranoia_level = 2

    inst.send_scpi_cmd('*CLS; *RST')   #clear the error list and reset the machine to its default state
    inst.send_scpi_cmd(':SOUR:INT X1')
    inst.send_scpi_cmd(':INST:CHAN {0}'.format(channel_numb)) 
    inst.send_scpi_cmd(':FREQ:RAST {0}'.format(SCLK))  #refer to a channel of your liking 
    inst.send_scpi_cmd(':INIT:CONT ON')
    inst.send_scpi_cmd(':TRAC:DEL:ALL')  # delete all the defined segments on the channel
    resp = inst.send_scpi_query(':SYST:ERR?')
    
    
    print("\n===INITIALIZATION OF CHANNEL {0}===  -->  ===DONE===".format(channel_numb))
    print("ERRORS:", resp)

    return None

    #=============================================================#
    #=============================================================#
    #=============================================================#