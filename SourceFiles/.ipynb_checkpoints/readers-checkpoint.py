
import numpy as np
import matplotlib.pyplot as plt


def apmplitude_extractor (data_array):
    """
    This function extract the amplitude out of a given array of a signal.
    
    INPUT:
        data_array - the array representing the signal
    
    OUTPUT:
        its amplitude
    """
    
    return (np.max(data_array) - np.min(data_array))


    #=============================================================#
    #=============================================================#
    #=============================================================#



def phase_extractor (data_array, delta_t, period_t):
    """
    This function extract the phase out of a given array of a signal.
    
    INPUT:
    
    OUTPUT:
    
    """
    
    return