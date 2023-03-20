import os
from teproteus import TEProteusAdmin as TepAdmin
from teproteus import TEProteusInst as TepInst
import numpy as np

"""This library stores all the task tables for various qunatum pulse sequences."""

class Task():
    
    def __init__(self, inst):
        """Inst - the instance of the open instrument command"""
        self.inst = inst
        
            #=============================================================#
    #=============================================================#
    #=============================================================#
        
    def simple_tasker (self, tasklen, channel):
        """
        Creates a simple test tasktable. The signals are to be referenced by using the segment number they were assigned to.
        Make sure there are the same number of segments as tasklen.

        INPUT:
            Tasklen - how many tasks would your tasktable consist of
            Channel - the reference number of the channel, could take values: [1,2,3,4]

        OUTPUT:
            None
        """


        cmd = ':INST:CHAN {0}'.format(channel)
        self.inst.send_scpi_cmd(cmd )

        cmd = ':TASK:COMP:LENG {0}'.format(tasklen)
        self.inst.send_scpi_cmd(cmd )


        for i in range(tasklen):
            curr_task = i + 1
            segnb = i + 1
            print("Current task:",curr_task)

            cmd = ':TASK:COMP:SEL {0}'.format(curr_task)
            self.inst.send_scpi_cmd(cmd)
            cmd = ':TASK:COMP:DTRigger ON'
            self.inst.send_scpi_cmd(cmd)

            # conditional statements to create closed loop task
            if curr_task == 1: 
                cmd = ':TASK:COMP:ENAB CPU'

            if curr_task==tasklen:
                cmd = ':TASK:COMP:NEXT1 {0}'.format(1)
                self.inst.send_scpi_cmd(cmd)
                print("Next task will be task:",1)
            else:
                cmd = ':TASK:COMP:NEXT1 {0}'.format(curr_task+1)
                self.inst.send_scpi_cmd(cmd)
                print("Next task will be task:",curr_task+1)

            cmd = ':TASK:COMP:TYPE SING'
            self.inst.send_scpi_cmd(cmd)

            # define the number of loops for the specific task
            cmd = ':TASK:COMP:LOOP {0}'.format(1)
            self.inst.send_scpi_cmd(cmd)

            # name the segment of memory to take the signal to be tasked with the aformentioned parameters from
            cmd = ':TASK:COMP:SEGM {0}'.format(segnb)
            self.inst.send_scpi_cmd(cmd)


        # write task to the machine
        cmd = ':TASK:COMP:WRIT'
        self.inst.send_scpi_cmd(cmd)
        print('Downloading Task table to channel {0}'.format(channel))

        # point to the channel
        cmd = ':INST:CHAN {0}'.format(channel)
        self.inst.send_scpi_cmd(cmd)

        # start the output
        cmd = ':OUTP ON'
        self.inst.send_scpi_cmd(cmd)

        # define the operation mode
        cmd = 'FUNC:MODE TASK'
        self.inst.send_scpi_cmd(cmd)


        # see if any errors came up
        resp = self.inst.send_scpi_query(':SYST:ERR?')
        print(resp)
        
        
        
            #=============================================================#
    #=============================================================#
    #=============================================================#
    
    
    
    def two_pulse_sequence (channel, time_delay, segment_pulse1 = int, segment_pulse2 = int, segment_time_delay = int):

        """
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
        """

        cmd = ':INST:CHAN {0}'.format(channel)
        self.inst.send_scpi_cmd(cmd )

        # what is the length of this task sequence
        cmd = ':TASK:COMP:LENG {0}'.format(3) ### SET TO 3, because of the 3 segments !!! INCREASE IF NEEDED !!!
        self.inst.send_scpi_cmd(cmd )

        ############################################### SUBROUTINE #####################################

        def subroutine (curr_task, segnb, tasklen, loops):

                cmd = ':TASK:COMP:SEL {0}'.format(curr_task)
                self.inst.send_scpi_cmd(cmd)
                # cmd = ':TASK:COMP:DTRigger ON'
                # self.inst.send_scpi_cmd(cmd)
                
                if curr_task == 1: 
                    cmd = ':TASK:COMP:DTRigger ON'
                    self.inst.send_scpi_cmd(cmd)

                if curr_task==tasklen:  # this loops the tasktable, later we may take it away
                    cmd = ':TASK:COMP:NEXT1 {0}'.format(1)
                    self.inst.send_scpi_cmd(cmd)
                else:
                    cmd = ':TASK:COMP:NEXT1 {0}'.format(curr_task+1)
                    print("Next task:",curr_task)
                    self.inst.send_scpi_cmd(cmd)

                # # Trigger Digitizer  
                # cmd = ':TASK:COMP:DTR ON'
                # self.inst.send_scpi_cmd(cmd)

                cmd = ':TASK:COMP:TYPE SING'
                self.inst.send_scpi_cmd(cmd)

                # define the number of loops for the specific task
                cmd = ':TASK:COMP:LOOP {0}'.format(loops)
                self.inst.send_scpi_cmd(cmd)

                # name the segment of memory to take the signal to be tasked with the aformentioned parameters from
                cmd = ':TASK:COMP:SEGM {0}'.format(segnb)
                self.inst.send_scpi_cmd(cmd)

        ################################################################################################


        subroutine (curr_task = 1, segnb = segment_pulse1, tasklen = 3, loops = 1)
        subroutine (curr_task = 2, segnb = segment_time_delay, tasklen = 3, loops = time_delay)
        subroutine (curr_task = 3, segnb = segment_pulse2, tasklen = 3, loops = 1)


        # write task to the machine
        cmd = ':TASK:COMP:WRIT'
        self.inst.send_scpi_cmd(cmd)
        print('Downloading Task table to channel {0}'.format(channel))

        # see if any errors came up
        resp = self.inst.send_scpi_query(':SYST:ERR?')
        print(resp)


        
    #==========================================================#
    #=============================================================#
    #=============================================================#
    
    
    
        def three_pulse_sequence (channel, time_delay1, time_delay2, segment_pulse1 = int, segment_pulse2 = int, segment_pulse3 = int, segment_time_delay = int):

            """
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
            """

            cmd = ':INST:CHAN {0}'.format(channel)
            self.inst.send_scpi_cmd(cmd )

            # what is the length of this task sequence
            cmd = ':TASK:COMP:LENG {0}'.format(3) ### SET TO 3, because of the 3 segments !!! INCREASE IF NEEDED !!!
            self.inst.send_scpi_cmd(cmd )

            ############################################### SUBROUTINE #####################################

            def subroutine (curr_task, segnb, tasklen, loops):

                    cmd = ':TASK:COMP:SEL {0}'.format(curr_task)
                    self.inst.send_scpi_cmd(cmd)
                    # cmd = ':TASK:COMP:DTRigger ON'
                    # self.inst.send_scpi_cmd(cmd)

                    if curr_task == 1: 
                        cmd = ':TASK:COMP:DTRigger ON'
                        self.inst.send_scpi_cmd(cmd)

                    if curr_task==tasklen:  # this loops the tasktable, later we may take it away
                        cmd = ':TASK:COMP:NEXT1 {0}'.format(1)
                        self.inst.send_scpi_cmd(cmd)
                    else:
                        cmd = ':TASK:COMP:NEXT1 {0}'.format(curr_task+1)
                        print("Next task:",curr_task)
                        self.inst.send_scpi_cmd(cmd)

                    # # Trigger Digitizer  
                    # cmd = ':TASK:COMP:DTR ON'
                    # self.inst.send_scpi_cmd(cmd)

                    cmd = ':TASK:COMP:TYPE SING'
                    self.inst.send_scpi_cmd(cmd)

                    # define the number of loops for the specific task
                    cmd = ':TASK:COMP:LOOP {0}'.format(loops)
                    self.inst.send_scpi_cmd(cmd)

                    # name the segment of memory to take the signal to be tasked with the aformentioned parameters from
                    cmd = ':TASK:COMP:SEGM {0}'.format(segnb)
                    self.inst.send_scpi_cmd(cmd)

            ################################################################################################


            subroutine (curr_task = 1, segnb = segment_pulse1, tasklen = 3, loops = 1)
            subroutine (curr_task = 2, segnb = segment_time_delay, tasklen = 3, loops = time_delay1)
            subroutine (curr_task = 3, segnb = segment_pulse2, tasklen = 3, loops = 1)
            subroutine (curr_task = 4, segnb = segment_time_delay, tasklen = 3, loops = time_delay2)
            subroutine (curr_task = 5, segnb = segment_pulse3, tasklen = 3, loops = 1)


            # write task to the machine
            cmd = ':TASK:COMP:WRIT'
            self.inst.send_scpi_cmd(cmd)
            print('Downloading Task table to channel {0}'.format(channel))

            # see if any errors came up
            resp = self.inst.send_scpi_query(':SYST:ERR?')
            print(resp)



        #=============================================================#
        #=============================================================#
        #=============================================================#


    