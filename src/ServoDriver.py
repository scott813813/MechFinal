"""
@author GI Ahern @c March 2023
"""
import utime
import pyb

class ServoDriver:
    """! 
    This class implements a servo motor driver for the term project. 
    """

    def __init__(self,in1pin,timer):

        # If enpin is high motor/vice versa
        '''en_pin.low()
        self.en_pin = en_pin'''
        # Setup Timer
        tim = pyb.Timer(timer, prescaler = 79, period = 19999) 
        self.tim = tim
        # Setup Channel
        ch2 = tim.channel(2, pyb.Timer.PWM, pin=in1pin)
        self.ch2 = ch2
        '''ch2 = tim.channel(2, pyb.Timer.PWM, pin=in2pin)
        self.ch2 = ch2'''
        #return(ch1,ch2,tim)
        print ("Creating a motor driver")

    def runServo(self, level):
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
        self.ch2.pulse_width(level)

        '''self.en_pin.high()
        if level >= 0:
            self.ch1.pulse_width(level)
            self.ch2.pulse_width(0)
        else:
            level = level/(-1)
            self.ch1.pulse_width(level)
            self.ch1.pulse_width(0)
        print (f"Setting duty cycle to {level}")'''

if __name__ == "__main__":

    pinA8 = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.OUT_PP)
    tim = 1
    
    trig = ServoDriver(pinA8, tim)
    try:
        trig.runServo(800) # 800=rest, 1500 = fire!
    except KeyboardInterrupt:
        print("Interupted")

