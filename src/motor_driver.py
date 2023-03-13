"""!
@file motor_driver.py
This file contains code to run the motor 

@author mecha12
@date   31-jan
"""

import pyb # The module for the microcontroller

class MotorDriver:
    """! 
    This class implements a motor driver for an ME405 kit. 
    """
    
    def __init__ (self, en_pin, in1pin, in2pin, timer):
        """! 
        Creates a motor driver by initializing GPIO
        pins and turning off the motor for safety. 
        @param en_pin Represents the pin for enabling and 
               disabling the motor
        @param in1pin Is 1 of 2 pins used for controlling the 
               magnitude and direction of the motor
        @param in2pin Is 1 of 2 pins used for controlling the 
               magnitude and direction of the motor
        @param timer Is a variable representing the Timer used
               for the motor
        """
        # If enpin is high motor/vice versa
        en_pin.low()
        self.en_pin = en_pin
        # Setup Timer was freq = 20000,  prescaler=0, period=0xFFFF
        tim = pyb.Timer(timer, freq = 20000)
        #tim.prescalar(0)
        self.tim = tim
        # Setup Channel
        ch1 = tim.channel(1, pyb.Timer.PWM, pin=in1pin)
        self.ch1 = ch1
        ch2 = tim.channel(2, pyb.Timer.PWM, pin=in2pin)
        self.ch2 = ch2
        #return(ch1,ch2,tim)
        print ("Creating a motor driver")

    def set_duty_cycle (self, level):
        """!
        This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
               cycle of the voltage sent to the motor 
        @param ch1 A variable representing timer channel 1 
               to be called for PWM command
        @param ch2 A variable representing timer channel 2 
               to be called for PWM command
        """
        self.en_pin.high()
        if level >= 0:
            self.ch1.pulse_width_percent(level)
            self.ch2.pulse_width_percent(0)
        else:
            level = level/(-1)
            self.ch2.pulse_width_percent(level)
            self.ch1.pulse_width_percent(0)
        #print (f"Setting duty cycle to {level}")