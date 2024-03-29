
import os
import numpy as np
import matplotlib.pyplot as plt
import helpers

class Pulse():
    """This is a class containing all the pulses one may wish for."""
    
    def __init__ (self, SCLK, DUC_INTERP, show_plot = False):
        
        self.SCLK = SCLK
        self.DUC_INTERP = DUC_INTERP
        self.show_plot = show_plot
        
    def blank_signal (self, DC_bias = 0):
        
        """
        This function gives DC signal. It is by default 0V to represent no 
        signal in the system.
        
        TAKES:
            SCLK - the sampling clock of the proteus
            DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
            Show plot - whether to show a plot of the function or not
            
        RETURNS: 
            The array that represents the signal
            The segment length of the waveform
        """
            
        seglen = 2048  # the smallest available signal length in the proteus
        
        print ("The blank singnal is with time width:",seglen/self.SCLK)

        x = np.linspace(start=0, stop=1, num=seglen, endpoint=False)
        y= DC_bias*x

        if self.show_plot == True:
            plt.plot(x,y)

        return y
    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    def simple_sin (self, amplitude, frequency, phase_shift = 0):
        """
        This method gives a sinus signal.

        TAKES: 
            frequency in [Hz]
            Phase shift in [radians]
            SCLK - the sampling clock of the proteus
            Amplitude b/w [-1,1]
            Show plot - whether to show a plot of the function or not

        RETURNS: 
            The array that represents the signal
        """
        
        seglen = self.SCLK/frequency ### how many DAC events needed to form one period of this function
        print ("original seglen:", seglen)
        
        seglen = int(helpers.formatter(seglen)[0])
        print ("formated seglen:", seglen)

        x = np.linspace(start=0, stop=2 * np.pi, num=seglen, endpoint=False) 

        y = amplitude * np.sin(x + phase_shift)

        if self.show_plot == True:
            plt.plot(x,y)
            plt.xlabel('Radians') 
            plt.ylabel('Amplitude') 
            plt.title('Sinus')

        return y


    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    def gaussian_pulse (self, amplitude, sigma, width_over_sigma, frequency):
        """
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
        """

        frequency = frequency / self.DUC_INTERP  ### see if this holds !!!!
        # self.SCLK = self.SCLK/2.5


        period = 1/frequency
        delta_t = 1/self.SCLK ### how much time between each two sequential signal points
        sigma_numerical = sigma/delta_t  ### how many datapoints within a sigma

        print ("period = {0}[ns]".format(period*1e9))
        print ("sigma = {0}[ns]".format(sigma*1e9))
        print ("sigma_num = {0} datapoints ".format(sigma_numerical))

        width = width_over_sigma*sigma_numerical # time width of the gaussian pulse, the width of the pulse terminates at 5*sigma, this is made by convention, it can be change to be (arbitrary number*sigma)
        print (width_over_sigma, sigma_numerical, width)
        seglen_gauss = int(width)
        print("Gaussian Segement length = {0} datapoints\n".format(seglen_gauss))
        print("Gaussian Segement length (in time) = {0} [ns]]".format(width_over_sigma*sigma*1e9))

    ################# WARNINGS AND CHECKS #######################

        if self.DUC_INTERP != 1:
            print ('Attention the DUC Interpreter has a value different then 1, mainly {0}. This will divide the frequency by {0}'.format(self.DUC_INTERP))


        if 5*period > sigma:
            print ("\n!WARNING! Sigma is comparable to the period of the oscillation\n")

        seglen_gauss, normalization_factor = helpers.formatter(seglen_gauss)

    ###########################################################

        t = np.linspace(-1, 1, seglen_gauss, endpoint=False)

        ss = sigma_numerical / seglen_gauss

        GAUS_FC = frequency * seglen_gauss * self.DUC_INTERP /2 / self.SCLK

    #     print('Gaussian frequency = {0}[Mhz]'.format(SCLK * 2 * GAUS_FC / seglen_gauss / 1e6/ DUC_INTERP))  # the actual frequency of the sin wave in the gaussian
        print('Gaussian frequency = {0}[Mhz]'.format(self.SCLK * 2 * GAUS_FC / seglen_gauss / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin = np.sin(2*np.pi*t*GAUS_FC)
        cos = np.cos(2*np.pi*t*GAUS_FC)
        gaussian = amplitude * (1/ss/np.sqrt(2*np.pi)/2) * np.exp(-(t**2)/2/(ss**2)) / normalization_factor
        (i) = sin*gaussian
        (q) = cos*gaussian
        magn = (i) + (q)
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])




        return (i), (q), magn, gaussian

    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    def gaussian_drag_pulse (self, amplitude, sigma, width_over_sigma, beta, frequency):
        """
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
        """

        frequency = frequency / self.DUC_INTERP  ### see if this holds !!!!
        # self.SCLK = self.SCLK/2.5


        period = 1/frequency
        delta_t = 1/self.SCLK ### how much time between each two sequential signal points
        sigma_numerical = sigma/delta_t  ### how many datapoints within a sigma

        print ("period = {0}[ns]".format(period*1e9))
        print ("sigma = {0}[ns]".format(sigma*1e9))
        print ("sigma_num = {0} datapoints ".format(sigma_numerical))

        width = width_over_sigma*sigma_numerical # time width of the gaussian pulse, the width of the pulse terminates at 5*sigma, this is made by convention, it can be change to be (arbitrary number*sigma)
        print (width_over_sigma, sigma_numerical, width)
        seglen_gauss = int(width)
        print("Gaussian Segement length = {0} datapoints\n".format(seglen_gauss))
        print("Gaussian Segement length (in time) = {0} [ns]]".format(width_over_sigma*sigma*1e9))

    ################# WARNINGS AND CHECKS #######################

        if self.DUC_INTERP != 1:
            print ('Attention the DUC Interpreter has a value different then 1, mainly {0}. This will divide the frequency by {0}'.format(self.DUC_INTERP))


        if 5*period > sigma:
            print ("\n!WARNING! Sigma is comparable to the period of the oscillation\n")

        seglen_gauss, normalization_factor = helpers.formatter(seglen_gauss)

    ###########################################################

        t = np.linspace(-1, 1, seglen_gauss, endpoint=False)

        ss = sigma_numerical / seglen_gauss

        GAUS_FC = frequency * seglen_gauss * self.DUC_INTERP /2 / self.SCLK

    #     print('Gaussian frequency = {0}[Mhz]'.format(SCLK * 2 * GAUS_FC / seglen_gauss / 1e6/ DUC_INTERP))  # the actual frequency of the sin wave in the gaussian
        print('Gaussian frequency = {0}[Mhz]'.format(self.SCLK * 2 * GAUS_FC / seglen_gauss / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin = np.sin(2*np.pi*t*GAUS_FC)
        cos = np.cos(2*np.pi*t*GAUS_FC)
        gaussian = amplitude * (1/ss/np.sqrt(2*np.pi)/2) * np.exp(-(t**2)/2/(ss**2)) / normalization_factor
        gaussian_dragged = amplitude * (1 - beta*t/ss*2) * (1/ss/np.sqrt(2*np.pi)/2) * np.exp(-(t**2)/2/(ss**2)) / normalization_factor
        (i) = sin*gaussian
        (q) = cos*gaussian_dragged
        magn = (i) + (q)
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])




        return (i), (q), magn, gaussian


    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    def sin_pulse (self, amplitude, width, frequency):
        """
        This funtion prepares a sin shaped pulse (the envelope of the pulse has a sinis shape).

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width - of the pulse [sec]
            frequency - of the signal

        OUTPUTS:
            I component of the signal
            Q component of the signal
            Sin_envelope - the envelope of the pulse 
            """

        if self.DUC_INTERP != 1:
            print ('====Attention the DUC Interpreter has a value different then 1!===='.format(self.DUC_INTERP))

        frequency = frequency / self.DUC_INTERP
        # SCLK = SCLK/2.5

        period = 1/frequency
        delta_t = 1/self.SCLK ### how much time between each two sequential signal points

        print ("period = {0}[ns]".format(period*1e9))

        width_seglen = width / delta_t 
        seglen_pulse = int(width_seglen)
        print("Sine segement length = {0} datapoints\n".format(seglen_pulse))
        print("Sine segement length (in time) = {0} [ns]]".format(width*1e9))

        seglen_pulse, normalization_factor = helpers.formatter(seglen_pulse)

        t = np.linspace(start= 0, stop= 1, num= seglen_pulse, endpoint= False) 
        x = np.linspace(start= 0, stop= np.pi, num= seglen_pulse, endpoint= False) 

        FC = 5 * frequency * seglen_pulse * self.DUC_INTERP /2 / self.SCLK

        print('Signal frequency = {0}[Mhz]'.format(frequency / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin_envelope = amplitude * np.sin(x)
        sin = np.sin(2*np.pi*t*FC)
        cos = np.cos(2*np.pi*t*FC)

        (i) = sin*sin_envelope
        (q) = cos*sin_envelope
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])


        return (i), (q), sin_envelope


    #=============================================================#
    #=============================================================#
    #=============================================================#

    def trapezoid_pulse (self, amplitude, width_slope, width_plateau, frequency):
        """
        This funtion prepares a trapezoid shaped pulse.

        INPUTS:
            amplitude - the amplitude scaler of the signal, takes value [0 to 1]
            width_slope -  width of the slope part of the pulse in [sec]
            width_plateau - width of the plateau part of the pulse in [sec]
            frequency - of the signal in [Hz]

        OUTPUTS:
            I component of the signal
            Q component of the signal
            Trapezoid_signal - this is just the envelope of the pulse
        """

        if self.DUC_INTERP != 1:
            print ('====Attention the DUC Interpreter has a value different then 1!===='.format(self.DUC_INTERP))

        frequency = frequency / self.DUC_INTERP
        # SCLK = SCLK/2.5

        period = 1/frequency
        delta_t = 1/self.SCLK ### how much time between each two sequential signal points

        print ("period = {0}[ns]".format(period*1e9))

        delta_bytes_slope = width_slope*self.SCLK
        delta_bytes_plateau = width_plateau*self.SCLK

        delta_bytes_slope, normalization_factor = helpers.formatter(delta_bytes_slope) ### to give the data segments an acceptable by the machine length
        delta_bytes_plateau, normalization_factor = helpers.formatter(delta_bytes_plateau) # ----//----

        tot_seglen = 2*delta_bytes_slope + delta_bytes_plateau

        print("Trapezoid pulse segement length = {0} datapoints\n".format(tot_seglen))
        print("Trapezoid pulse segement length (in time) = {0} [ns]]".format((2*width_slope + width_plateau)*1e9))

        t = np.linspace(start= 0, stop= 1, num = tot_seglen, endpoint= False) 

        ############## The envelope generation ##############
        upward_slope = np.linspace (0, np.pi/2, delta_bytes_slope)
        upward_slope = np.sin (upward_slope)

        downward_slope = np.flip (upward_slope)

        plateau = np.linspace (1, 1, delta_bytes_plateau)

        trapezoid_signal = np.concatenate ((upward_slope, plateau, downward_slope), axis = 0)
        trapezoid_signal = amplitude * trapezoid_signal

        print ('sin:',len(t),'trapezoid_signal:',len(trapezoid_signal))

        #########################################

        FC = 5 * frequency * tot_seglen * self.DUC_INTERP /2 / self.SCLK

        print('Signal frequency = {0}[Mhz]'.format(frequency / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin = np.sin(2*np.pi*t*FC)
        cos = np.cos(2*np.pi*t*FC)

        (i) = sin*trapezoid_signal
        (q) = cos*trapezoid_signal
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])


        return (i), (q), trapezoid_signal
    
    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#


    def gaussian_I_Q_with_IF (self, IF_frequency = float, amplitude = float, width = float, sigma = float, beta = float, I_to_Q_ratio = 1.0):

        """
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

        """

        delta_t = self.DUC_INTERP/self.SCLK # how much time is there b/w 2 consecutive datapoints

        ################ THE ENVELOPE ############

        segment_length = width / delta_t # how many dataponts we would need to express the signal
        segment_length = int(segment_length) # round it up

        how_many_sigmas_wide = width/sigma

        x = np.linspace (-width/2, width/2, segment_length)

        A = amplitude * np.exp(-(x**2)/2/(sigma**2)) # Amplitude
        phase = (beta*x/(sigma**2)) * np.exp(-(x**2)/2/(sigma**2)) # Phase

        I = A * np.cos(phase)  
        Q = A * (1/I_to_Q_ratio) * np.sin(phase)

        ################# THE IF SINGAL ########

        y = np.linspace (-(np.pi*IF_frequency*width), (np.pi*IF_frequency*width), segment_length)
        print (segment_length)

        I_mod = I*np.cos(y) + Q*np.sin(y)
        Q_mod = Q*np.cos(y) - I*np.sin(y)

        if self.show_plot == True:
            plt.plot(x, I, '-', x, Q, '-')
            plt.legend(['I envelope','Q envelope'])

        return I, Q, I_mod, Q_mod


        #=============================================================#
        #=============================================================#
        #=============================================================#
        
    def blank_signal_arbitrary (self, time, DC_bias = 0):
        
        # print ('blabla')
        """
        This function gives DC signal. It is by default 0V to represent no 
        signal in the system.
        
        TAKES:
            DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
            time - time length of the signal in [sec]
            
        RETURNS: 
            The array that represents the signal
            The segment length of the waveform
        """
        
        delta_t = 1/self.SCLK
        
        seglen = time/delta_t 
        
        print ("The blank singnal is with time width:",time, "[sec]")
        print ("\nThe blank singnal is with segment length:",seglen)
        
        if float.is_integer(seglen) == False:
            
            seglen = int(seglen)
            print("\nSegment length was not an integer number, thus it will be rounded to the closest integer.")
            print("\nThe closest time width that the format allows is {0} sec".format(delta_t*seglen))
        
        else:
            seglen = int(seglen)
            

        x = np.linspace(start=1, stop=1, num=seglen, endpoint=False)
        y= DC_bias*x

        if self.show_plot == True:
            plt.plot(x,y)

        return y
    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#


    
    def readout_pulse (self, amplitude, width_slope, width_plateau, frequency):
        """
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
        """

        if self.DUC_INTERP != 1:
            print ('====Attention the DUC Interpreter has a value different then 1!===='.format(self.DUC_INTERP))

        frequency = frequency / self.DUC_INTERP
        # SCLK = SCLK/2.5

        period = 1/frequency
        delta_t = 1/self.SCLK ### how much time between each two sequential signal points

        print ("period = {0}[ns]".format(period*1e9))

        delta_bytes_slope = int(width_slope*self.SCLK)
        delta_bytes_plateau = int(width_plateau*self.SCLK)

        tot_seglen = 2*delta_bytes_slope + delta_bytes_plateau

        print("readout pulse segement length = {0} datapoints\n".format(tot_seglen))
        print("readout pulse segement length (in time) = {0} [ns]]".format((2*width_slope + width_plateau)*1e9))

        t = np.linspace(start= 0, stop= 1, num = tot_seglen, endpoint= False) 

        ############## The envelope generation ##############
        upward_slope = np.linspace (0, np.pi/2, delta_bytes_slope)
        upward_slope = np.sin (upward_slope)

        downward_slope = np.flip (upward_slope)

        plateau = np.linspace (1, 1, delta_bytes_plateau)

        readout_signal = np.concatenate ((upward_slope, plateau, downward_slope), axis = 0)
        readout_signal = amplitude * readout_signal

        print ('sin:',len(t),'readout_signal:',len(readout_signal))

        #########################################

        FC = 5 * frequency * tot_seglen * self.DUC_INTERP /2 / self.SCLK

        print('Signal frequency = {0}[Mhz]'.format(frequency / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin = np.sin(2*np.pi*t*FC)
        cos = np.cos(2*np.pi*t*FC)

        (i) = sin*readout_signal
        (q) = cos*readout_signal
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])


        return (i), (q), readout_signal
    
    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#