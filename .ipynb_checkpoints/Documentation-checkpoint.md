# Proteus P9484M API reference guide

### Author

Boris Nedyalkov, Quantum Computing Lab, IFAE, Barcelona


This text showcases the functionalities of the different tools of the API. These are separated in different libraries, namely:

* initializers - this library contains intialization functions for the Proteus 
* pulse_lib - this library contains all the types of pulses, one can add here a new type of pulse if needed
* tasks - this library contains all the types of basic tasks, new ones can be added if need arises
* helpers - this library contains auxillary functions
* readers - this library contains all the readout functions

## Initializers

**connection_func ()** 

	This function calls the initialization sequence for the Proteus.

INPUTS: 
	None

OUTPUTS: 
	dac_mode - This is the single dataoint resolution mode of the DAC it can be 8 or 16-bit
	max_dac - the total vertical resolution of the DAC
	sid - the slot number of the machine (for connection)
	data_type - 8-bit or 16-bit type of dac mode
	inst - the instance that call the Proteus module

===============================================================

**system_info_func(max_dac = int, inst = instance)**

    This function gives some information about the system.
    
    INPUT:
        max_dac - the total vertical resolution of the DAC
        inst - the instance that calls the Proteus modules

    OUTPUT:
        None

===============================================================

**initialization_func(channel_numb = int, inst = instance, SCLK = int)**

    This fuction intializes or reinitializes if needed, the chosen channel of the Proteus.
    
    INPUT:
        channel_numb - the channel number you want reinitialized
        inst - the instance that calls the Proteus module s
        SCLK - the sampling clock rate [1/sec]

    OUTPUT:
        None

===============================================================
===============================

**initialization_func_IQ(channel_numb, inst, SCLK, SOURCE_NCO)**

        This fuction intializes or reinitializes if needed, the chosen channel of the Proteus for IQ processes.
    
    INPUT:
        channel_numb - the channel number you want reinitialized
        inst - the instance that calls the Proteus module s
        SCLK - the sampling clock rate [1/sec]
        SOURCE_NCO - the NCO frequency of the source [1/sec]
            
    OUTPUTS:
        None

===============================================================
==========================

****

        T

===============================================================
==========================



## Pulse_lib

This library contains a class taht calls on various methods to build waveforms. Ad more methods or modify the existing ones if needed.
This library is independent of the Proteus machinery.

### How to call the class:

**pulse = pulse_lib.Pulse(SCLK = int, DUC_INTERP = int, show_plot = Boolean)**
		
	INPUTS:
		SCLK - the sampling clock rate [1/sec]
            DUC_INTERP - the DUC interpolation mode [x1, x2, x4 or x8]
		show_plot - to show a plot of the wafeform or no [True or False]

	OUTPUTS:
		The instance that will contain all the methods.

===============================================================


**pulse.blank_signal (DC_bias = float)**

        This function gives DC signal. It is by default 0V to represent no 
        signal in the system.
        
        TAKES:
            SCLK - the sampling clock of the proteus
            DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
            Show plot - whether to show a plot of the function or not
            
        RETURNS: 
            The array that represents the signal
            The segment length of the waveform

===============================================================

**pulse.simple_sin (amplitude = float, frequency = int, phase_shift = 0)**

        This method gives a sinus signal.

        TAKES: 
            frequency in [Hz]
            Phase shift in [radians]
            SCLK - the sampling clock of the proteus
            Amplitude b/w [-1,1]
            Show plot - whether to show a plot of the function or not

        RETURNS: 
            The array that represents the signal

===============================================================

**pulse.gaussian_pulse (amplitude = float, sigma = float, width_over_sigma = float, frequency = int)**

        This method preapares a gaussian pulse.
        
        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            sigma - the sigma of the gaussian in [sec]
            width_over_sigma - how many sigmas wide is the pulse [sec] RECOMENDED VALUE == 4 or 5
            frequency - of the signal in [Hz]
        
        OUTPUTS:
            I - component of the signal
            Q - component of the signal
            Magn - the magnitude of the signal
            Gaussian - the envelope function
	  
	  BUGS:
            The amplitude can get above 1 (even at "amplitude = 1"). Needs fixing.

===============================================================

**pulse.gaussian_drag_pulse (amplitude = float, sigma = float, width_over_sigma = float, beta = float, frequency = int)**

        This method preapares a gaussian pulse with DRAG.
        
        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            sigma - the sigma of the gaussian in [sec]
            width_over_sigma - how many sigmas wide is the pulse [sec] RECOMENDED VALUE == 4 or 5
            beta - the DRAG coefficient (adjust accordingly depending on the qubit)
            frequency - of the signal in [Hz]
        
        OUTPUTS:
            I - component of the signal
            Q - component of the signal
            Magn - the magnitude of the signal
            Gaussian - the envelope function
        
        BUGS:
            The amplitude of the complex part gets above 1. Needs fixing.
===============================================================

**pulse.sin_pulse (amplitude = float, width = float, frequency = int)**

        This funtion prepares a sin shaped pulse (the envelope of the pulse has a sinis shape).

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width - of the pulse [sec]
            frequency - of the signal

        OUTPUTS:
            I component of the signal
            Q component of the signal
            Sin_envelope - the envelope of the pulse 

===============================================================

**pulse.trapezoid_pulse (amplitude = float, width_slope = float, width_plateau = float, frequency = int)**

        This funtion prepares a sin shaped pulse.

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width_slope -  width of the slope part of the pulse in [sec]
            width_plateau - width of the plateau part of the pulse in [sec]
            frequency - of the signal in [Hz]

        OUTPUTS:
            I component of the signal
            Q component of the signal
            Rabi_signal - this is just the envelope of the pulse


===============================================================
==========================

**gaussian_I_Q_with_IF (self, IF_frequency = float, amplitude = float, width = float, sigma = float, beta = float, I_to_Q_ratio = 1.0)**

        This method creates envelopes of I and Q signals to be fed to a IQ mixer.
        The I and Q signals are made in such a way that the aplitude of the signal is gaussian
        and its phase is gaussian derrivative.
        A.k.a this implements a DRAG gaussian pulse.

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width -  width of the gaussian in [sec]
            sigma - the sigma of the gaussian [sec]
            beta - The DRAG coefficient / ALPHA   
            I_to_Q_ratio - I/Q ratio, by default '1.0', can take any float value

        OUTPUTS:
            I - envelope I component of the signal
            Q - envelope Q component of the signal
            I_mod - modulated I component of the signal
            Q_mod - modulated Q component of the signal

        NOTES:
            ALPHA  is the anharmonicity = omega12 - omega01, normally about 200-300 MHz
            The DRAG coefficient - should theoretically be 0.5, for optimal phase correction  



===============================================================
==========================

**blank_signal_arbitrary (self, time, DC_bias = 0)**

        This function gives DC signal. It is by default 0V to represent no 
        signal in the system.
        
        TAKES:
            DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
            time - time length of the signal in [sec]
            
        RETURNS: 
            The array that represents the signal
            The segment length of the waveform

===============================================================
==========================

**readout_pulse (self, amplitude, width_slope, width_plateau, frequency)**

        This funtion prepares a trapezoid shaped pulse for readout.

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width_slope -  width of the slope part of the pulse in [sec]
            width_plateau - width of the plateau part of the pulse in [sec]
            frequency - of the signal in [Hz]

        OUTPUTS:
            I component of the signal
            Q component of the signal
            readout_signal - this is just the envelope of the pulse

===============================================================
==========================


## Tasks

This library contains a the class that call method for the creation of tasktable. Which in the quantum computing paradigm can be refered to "pulse sequences".

### How to call the class:

**task = tasks.Task(inst)**
		
	INPUTS:
		inst - the instance of the open instrument command

	OUTPUTS:
		The instance that will contain all the methods.

===============================================================

**task.simple_tasker (tasklen = int, channel = int)**

        Creates a simple test tasktable. The signals are to be referenced by using the segment number they were assigned to.
        Make sure there are the same number of segments as tasklen.

        INPUT:
            Tasklen - how many tasks would your tasktable consist of
            Channel - the reference number of the channel, could take values: [1,2,3,4]

        OUTPUT:
            None

===============================================================
**task.two_pulse_sequence (channel = int, time_delay = int, segment_pulse1 = int, segment_pulse2 = int, segment_time_delay = int)**

        This is simple quantum bit 2 pulse sequance task. It sends one pulse, waits for some time and then sends some other pulse. 
        This is a TEMPLATE tasktable. To be used for more elaborate qubit manipulation sequences.

        INPUTS:
            channel - channel number
            time_delay - time delay between the 1st and 2nd pulse
            !!! The time delay in seconds would be in the format time_delay * 2048/SCLK [sec] !!!

            segment1 - 1st pulse's segment number
            segment2 - 2nd pulse's segment number
            segment_time_delay - this is the segment number of the "blank" (empty) signal.
        

        OUTPUTS:
            None

===============================================================

**task.three_pulse_sequence (channel = int, time_delay1 = int, time_delay2 = int, segment_pulse1 = int, segment_pulse2 = int, segment_pulse3 = int, segment_time_delay = int)**

        This is simple quantum bit 3 pulse sequance task. It sends one pulse, waits for some time and then sends some other pulse. 
        This is a TEMPLATE tasktable. To be used for more elaborate qubit manipulation sequences.

        INPUTS:
            channel - channel number
            time_delay1 - time delay between the 1st and 2nd pulse
            time_delay2 - time delay between the 2nd and 3rd pulse
            !!! The time delay in seconds would be in the format time_delay * 2048/SCLK [sec] !!!

            segment1 - 1st pulse's segment number
            segment2 - 2nd pulse's segment number
            segment3 - 3rd pulse's segment number
            segment_time_delay - this is the segment number of the "blank" (empty) signal.


        OUTPUTS:
            None


===============================================================
========================

**solid_task(self, inst, channel, segment_number = int)**

        This is a TEMPLATE tasktable. It consists of one solid waveform and a trigger (for triggering the digitizer).

        INPUTS:
            inst - the instance of inst
            channel - channel number
            segment_number - this is the refernce number of the segment that includes all the pulses you want to output.

        OUTPUTS:
            None 


===============================================================
========================

## Helpers

**digital_conv_func (array = numpy_array, max_dac = int, data_type = int)**

    This an arbitrary array and transforms its values, so they would fit within the range of the DAC.

    TAKES: 
	array - An array with values between [-1 and 1]
      max_dac - The range of the DAC
	data_type - 8-bit or 16-bit type of dac mode
    
    RETURNS: 
      The transformed array in a binary format

===============================================================

**formatter (num = int)**

    This function take an arbitrary number and returns the closest to it number in the format: ( 64 * (32 + n)).

    TAKES: 
        num - Integer (or float) number

    RETURNS: 
        The formatted number 
        The normalization factor = fomatted number / number

===============================================================

**download_func (inst, wave, channel, segment)**

    This function downloads the waveforms down to the Proteus unit.

    TAKES:
        inst - the instance of the open instrument command
        wave - a binary array with the data of the waveform
        channel - the number of the channel, could take values - [1,2,3,4]
        segment - assigned reference number of the segment in which we put the waveform

    RETURNS: 
        Absolutely nothing :) (Except many good wishes)

===============================================================

**quitter (sid)**

    This function terminates the session with the Proteus.

    INPUT: 
        sid - The SID number

    OUTPUT: 
        None
    
===============================================================

**task_starter (inst, channel)**

    THIS TASK IS BEING DUPLICATED BY "start_task"

    Here we instantiate the channel and all the tasks put in it.

    INPUT:
        inst - the instance of the open instrument command
        channel - the number of the channel, could take values - [1,2,3,4]

    OUTPUT: 
        None
        
        
        
===============================================================
========================

**concatenator (*array)**

    This function takes any number of arrays as arguments.
    
    INPUT:
        Arrays
        
    OUTPUT:
        Concatonated array

===============================================================
==========================

**start_task(inst, channel)**

    This function starts the task at a pointed channel.
    
    INPUT: 
        channel - channel number
    
    OUTPUT: 
        None

===============================================================
==========================

**IQ_interleaver(I_array, Q_array)**

    Intertwines 2 signals, thus preparin them for I, Q modulation.
    At IQ ONE modulation mode (the one used here), the I and Q arrays are stored in one array.
    This array has the every second entry filled with I data and the other ones with Q data.
    
    INPUT:
        I_array - I data array
        Q_array - Q data array
    
    OUTPUT: 
        Intertwinded array

===============================================================
==========================

**formatter_for_sequences(num)**

    This function take an arbitrary number and returns how much more does it need to conform to the format: ( 64 * (32 + n))
    
    TAKES: 
        Integer (or float) number
        
    RETURNS: 
        The remant  

===============================================================
==========================


## Readers

**digitizer_setup(inst, DIG_SCLK, DDC_NCO, time_delay)**

    This function sets up the digitizer setting for IQ operation.
    
    INUT:
        inst - the proteus instance
        DIG_SCLK - sampling clock rate of the digitizer (DAC), max value is 2.7e9
        DDC_NCO - the LO of the demodulator (make ideally the same as Source NCO)
        time_delay - delay until the digitizer is to be triggered
    
    OUTPUT:
        None


===============================================================
========================

**framer(inst, numframes = int, framelen = int)**

    This function defines the number of frames and the length of each frame on would like to use for capturing of the digitized data.
    
    INUT:
        inst - the proteus instance
        numframes - the number of frames 
        framelen - the length in datapoints for each frame
    
    OUTPUT:
        None


===============================================================
========================

**capturer(inst)**

    This function captures the data in the frames preselected.
    
    INUT:
        inst - the proteus instance
    
    OUTPUT:
        None


===============================================================
========================


**IQ_data_extractor(inst, channel = int, numframes = int, framelen = int)**

    This takes the data from the memory, then extracts the I and Q components from it.
    
    INUT:
        inst - the proteus instance
        channel - the channel to take the data from
        numframes
        framelen
    
    OUTPUT:
        I data array
        Q data array
        
  
===============================================================
========================
    




