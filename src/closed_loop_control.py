"""!
@file closed_loop_control.py
This file contains code which controls the motors position by taking the
proportional gain constant, Kp, and finds the difference between the desired
motor position and actual position.

@author mecha12
@date   13-Feb-2023
"""

import array # Allows for the creation of arrays to export over the serial port

class clCont:
    """
    Implements a closed loop control scheme
    """
    
    def __init__(self, initSet, initKp):
        """!
        Stores variables set in main.py
        @param initSet The target position of the motor
        @param initKp The proportional gain constant
        """
        self.setpoint = initSet
        self.Kp = initKp
        
    def run(self, setpoint, actual):
        """!
        Sets the PWM of the motor in order to position the motor
        @param setpoint The target position of the motor
        @param actual The current position of the motor
        @returns The pulse width modulation of the motor
        """
        PWM = self.Kp * (setpoint - actual)
        if PWM > 100: # Caps the PWM at 100% if PWM is over 100
            PWM = 100
        elif PWM < -100: # Caps the PWM -100% if the PWM is less than -100
            PWM = -100
    
        return PWM

    def set_setpoint(self, newSetpoint):
        """!
        Sets a new target position
        @param newSetpoint The new target position of the motor
        """
        self.setpoint = newSetpoint

    def set_Kp(self, newKp):
        """!
        Sets a new proportional gain constant
        @param newKp The new proportional gain constant
        """
        self.Kp = newKp