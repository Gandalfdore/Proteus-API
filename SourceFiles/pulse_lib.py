
import numpy as np
import matplotlib.pyplot as plt
import helpers

class Pulse():
    """This is a class containing all the pulses one may wish for."""
    
    def __init__ (self, SCLK, DUC_INTERP, show_plot = False):
        """
            SCLK - sampling clock rate [integer]
            DUC_INTERP - the interpolation  [integer]
            show_plot - to show a plot of the waveform or not [Boolean value]
        """
        
        self.SCLK = SCLK
        self.DUC_INTERP = DUC_INTERP
        self.show_plot = show_plot
        
    def blank_signal (self, DC_bias = 0):
        
        # print ('blabla')
        """This function gives DC signal. It is by default 0V to represent no 
        signal in the system.
        
        TAKES:
            DC bias - if you want to give a DC bias to the line signal, takes values from [-1 to 1]
            
        RETURNS: 
            The array that represents the signal
            The segment length of the waveform"""
            
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
            Amplitude b/w [-1,1]
            frequency in [Hz]
            phase_shift - in [radians]

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
    
    
    
    def gaussian_pulse (self, I, Q, amplitude, sigma, width_over_sigma, frequency):
        """
        This method preapares a gaussian pulse.
        
        INPUTS:
            I - 1st quadrature amplitude
            Q - 2nd quadrature amplitude
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
        (i) = I*sin*gaussian
        (q) = Q*cos*gaussian
        
        # phase_shift = np.arctan(I/Q)
        # magn = np.sqrt(I**2 + Q**2)*np.sin(2*np.pi*t*GAUS_FC + phase_shift)*gaussian
        magn = (i) + (q)
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])




        return (i), (q), magn, gaussian

    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    def gaussian_drag_pulse (self, I, Q, amplitude, sigma, width_over_sigma, beta, frequency):
        """
        This method preapares a gaussian pulse with DRAG.
        
        INPUTS:
            I - 1st quadrature amplitude
            Q - 2nd quadrature amplitude
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
        (i) = I*sin*gaussian
        (q) = Q*cos*gaussian_dragged
        
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
            Sin_envelope - the envelope of the pulse """

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

    def rabi_pulse (self, amplitude, width_slope, width_plateau, frequency):
        """
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

        print("Rabi pulse segement length = {0} datapoints\n".format(tot_seglen))
        print("Rabi pulse segement length (in time) = {0} [ns]]".format((2*width_slope + width_plateau)*1e9))

        t = np.linspace(start= 0, stop= 1, num = tot_seglen, endpoint= False) 

        ############## The envelope generation ##############
        upward_slope = np.linspace (0, np.pi/2, delta_bytes_slope)
        upward_slope = np.sin (upward_slope)

        downward_slope = np.flip (upward_slope)

        plateau = np.linspace (1, 1, delta_bytes_plateau)

        rabi_signal = np.concatenate ((upward_slope, plateau, downward_slope), axis = 0)
        rabi_signal = amplitude * rabi_signal

        print ('sin:',len(t),'rabi_signal:',len(rabi_signal))

        #########################################

        FC = 5 * frequency * tot_seglen * self.DUC_INTERP /2 / self.SCLK

        print('Signal frequency = {0}[Mhz]'.format(frequency / 1e6))  # the actual frequency of the sin wave in the gaussian

        ####################
        sin = np.sin(2*np.pi*t*FC)
        cos = np.cos(2*np.pi*t*FC)

        (i) = sin*rabi_signal
        (q) = cos*rabi_signal
        ####################

        if self.show_plot == True:
            plt.plot(t, (i), '-',t, (q), '-')
            plt.legend(['I','Q'])


        return (i), (q), rabi_signal
    
    
    
    #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    def readout_pulse (self, amplitude, frequency, num_of_periods, phase_shift = 0):
        """
        This method gives a readout pulse. It is a simple sinusoid.'''.

        TAKES: 
            Amplitude b/w [-1,1]
            frequency in [Hz]
            num_of_periods - how many periods long to be the readout
            phase_shift - in [radians]

        RETURNS: 
            seglen_tot - The array that represents the signal
            distance_1stpeak_marker_in_time - time distance between the marker's tip and the 1st crest [sec]
            distance_bw_2_peaks_in_time - time distance between two crests in time [sec]
        """
        
        seglen = self.SCLK/frequency ### how many DAC events needed to form one period of this function
        print ("original seglen:", seglen)
        
        seglen = int(helpers.formatter(seglen)[0])
        # print ("formated seglen:", seglen)
        
        seglen = seglen * num_of_periods
        print ("formated seglen:", seglen)

        x = np.linspace(start= 0, stop=2 * np.pi * num_of_periods, num=seglen, endpoint=False) 

        y = amplitude * np.sin(x + phase_shift)

        # if self.show_plot == True:
        #     plt.plot(x,y)
        #     plt.xlabel('Radians') 
        #     plt.ylabel('Amplitude') 
        #     plt.title('Sinus')
            
        #===============Indexes of the sin peaks========================#
        
        
        phase_shift_bytes = int((phase_shift/2/np.pi)*(seglen/num_of_periods))
        
        arg = seglen/4/num_of_periods - phase_shift_bytes
        int_arg = int(arg)
        # int_arg2 = int_arg + seglen/num_of_periods
        
        # print('bytes of phase shift:', phase_shift_bytes)
        # print('index of the peak:', int_arg, 'y value of the arg', y[int_arg])
        # print('index of the 2nd peak:', int_arg2, 'y value of 2nd peak', y[int(int_arg2)])
        
        #=====================================================================#
        
        
        #===============Create the marker bump (triangle shaped)========================#
        
        seglen_triangle = 2048 # the smallest chunck available for waveform in the DDR memory
        tr1 = np.linspace (start = 0, stop = 1, num = int(seglen_triangle/2), endpoint =False)
        tr2 = np.linspace (start = 1, stop = 0, num = int(seglen_triangle/2), endpoint =False)
        tr = np.concatenate((tr1, tr2), axis=None)
        tr = amplitude * tr
        #=====================================================================#
        
        
        #===============Create some space between them (not mandatory)========================#
        
        seglen_space = 10*2048 # the smallest chunck available for waveform in the DDR memory
        space = np.linspace (start = 0, stop = 0, num = seglen_space, endpoint =False)
        space = amplitude * space
        #=====================================================================#
        
        
        signal_tot = np.concatenate ((y, space, tr), axis=None)  # put everything together
        
        
        #===============Find the distances between the marker and the peaks========================#
        
        
        distance = len(signal_tot) - seglen_triangle/2 - int_arg
        distance_1stpeak_marker_in_time = distance/self.SCLK
        distance_bw_2_peaks_in_time = seglen/num_of_periods/self.SCLK
        print ('byte distance between the markers tip and the 1st crest :', distance)
        print ('time distance between the markers tip and the 1st crest :', distance/self.SCLK)
        # print ('time distance between two crests in bytes:', seglen/num_of_periods)
        # print ('time distance between two crests in time [sec]:', seglen/num_of_periods/self.SCLK)
        

        #=====================================================================#
        
        
        #===============PLOT========================#
        
        if self.show_plot == True:
            
            fig1, (ax1) = plt.subplots(1, 1, figsize = (5, 3.5), dpi = 100)   ## define a plot
            fig1, (ax2) = plt.subplots(1, 1, figsize = (5, 3.5), dpi = 100)   ## define a plot

            ax1.plot(x,y,'-', color='#ffe24e',linewidth=1.5, label='The readout signal')
            ax1.set_xlabel('Radians', fontsize=12)      ## Axis labels
            ax1.set_ylabel('Amplitude', fontsize=12)
            
            ax2.plot(signal_tot,'-', color='b',linewidth=1.5, label='Signal + Marker')
            ax2.set_xlabel('bytes', fontsize=12)      ## Axis labels
            ax2.set_ylabel('Amplitude', fontsize=12)
            
            plt.tight_layout()  
            
            plt.legend()    
            plt.show()
        
        #=====================================================================#
            

        return signal_tot, distance_1stpeak_marker_in_time, distance_bw_2_peaks_in_time


