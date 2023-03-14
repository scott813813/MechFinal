"""!
@file encoder_reader.py
This file contains code which computes the reading from the encoder in order to evaluate the speed of the motor

@author mecha12
@date   13-Feb-2023
"""

import pyb # Micropython library

class EncoderReader:
    """!
    Compute the value of the encoder reading
    @returns The encoder reading
    """
    absolute_position = 0
    former_position = 0

    def __init__(self, pinA, pinB, timerNum):
        """!
        Sets the channels and timer for the motor that is running
        """
        self.timer = pyb.Timer(timerNum, prescaler=0, period=0xFFFF)
        ch1 = self.timer.channel(1, pyb.Timer.ENC_A, pin=pinA)
        ch2 = self.timer.channel(2, pyb.Timer.ENC_B, pin=pinB)

    def read(self):
        """!
        @returns The position of the motor from the zero point
        """
        current_position = self.timer.counter()
        if current_position - self.former_position > 30000:
            difference = current_position - 65535 + self.former_position
            print(current_position)
            print(self.former_position)
            print("cur, for")
        elif current_position - self.former_position < -30000:
            difference = current_position + 65535 - self.former_position
        else:
            difference = current_position - self.former_position
        self.former_position = current_position
        self.absolute_position += difference
        return self.absolute_position

    def zero(self):
        """!
        Sets the time counter to 0
        """
        self.absolute_position = 0
        self.former_position = 0
        self.timer.counter(0)

if __name__ == "__main__":
    # Section for testing code
    pinB6 = pyb.Pin (pyb.Pin.board.PB6, pyb.Pin.IN)
    pinB7 = pyb.Pin (pyb.Pin.board.PB7, pyb.Pin.IN)
    test = EncoderReader(pinB6, pinB7, 4)
    test.zero()
    while True:
        print(test.read())
        pyb.delay(100)
