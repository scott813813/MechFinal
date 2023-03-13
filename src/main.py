"""!
@file main.py
    This file that runs the turret   . The motors
    are run using the code developed in the previous ME 405 labs.
    
@author mecha12
@date   11-Mar-2023
"""

import gc # Memory allocation garbage collector
import pyb # Micropython library
import utime # Micropython version of time library
import cotask # Run cooperatively scheduled tasks in a multitasking system
import task_share # Tasks share data
from machine import Pin

from closed_loop_control import clCont # The closed loop control method from closed_loop_control.py
from motor_driver import MotorDriver # The method to drive the motor from motor_drive.py
from encoder_reader import EncoderReader # Read encoder method from encoder_reader.py
from mlx_cam import MLX_Cam # Take values from IR camera
    
def buttonLogic(pin):
    print('button press')
    global buttonCounts
    buttonCounts += 1
    print(buttonCounts)



def masterTask(shares):
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    masterState = 0
    #yawStartPos = 13272 # 180 degrees, ie 3.32 rotations with a gear ratio of 15
    #pitchStartPos = 0 # Keep steady heading
    while True:
        print('button', buttonCounts)
        print('master')
        while buttonCounts == 1:
            if masterState == 0: # Initilization state
                masterState = 1
                print('Master: S1')
                yield
                
            elif masterState == 1: # Go to aiming position  
                s_YawPos.put(yawStartPos)
                s_PitchPos.put(pitchStartPos)
                #masterState = 2
                print('Master: S2')
                yield
            """
            elif masterState == 2: # Wait four seconds until time to track, and then five to fire
                timeElapse = utime.ticks_ms() - zeroPoint # Time since button pressed
                
                if timeElapse >= idlePeriod: # Stop firing
                    s_StopShooting.put(True)
                    
                elif timeElapse >= firePeriod: # Begin firing
                    s_TimeToFire.put(True)
                    
                elif timeElapse >= trackPeriod: # Begin tracking
                    s_TimeToTrack.put(True)
              """
            print('yield 2')
            yield
        print('yield 1')
        yield

                
            
def yawTask(shares):
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    while True:
        print('yaw')
        if buttonCounts == 1:
            '''Control Loop Setup'''
            Kp = 0.06				#0.1 excessive oscillation,  0.005 good performance, 0.002 underdamped
            cll = clCont(0, Kp) # Set proportional constant gain for yaw motor
            print('Set Yaw Motor constant')
            while buttonCounts == 1:
                p = encY.read() # Current position of yaw motor
                lvl = cll.run(s_YawPos.get(), p) # Run closed loop controller
                moeY.set_duty_cycle(lvl) # Set the duty cycle
                print('Yaw Motor')
                # send new value high, 
                # scrub current reading, and set it to 0
                # go to new reading, and set new value reading low
                yield
            yield
        yield
                

def pitchTask(shares): 
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    while True:
        print('pitch')
        if buttonCounts == 1:
            '''Control Loop Setup'''
            Kp = 0.07				#0.1 excessive oscillation,  0.005 good performance, 0.002 underdamped
            cll = clCont(0, Kp) # Set proportional constant gain for yaw motor
            print('Set Yaw Motor constant')
            while buttonCounts == 1:
                p = encP.read() # Current position of pitch motor 
                lvl = cll.run(s_PitchPos.get(), p) # Run closed loop controller
                moeP.set_duty_cycle(lvl) # Set the duty cycle
                print('Pitch Motor')
                # send new value high, 
                # scrub current reading, and set it to 0
                # go to new reading, and set new value reading low
                yield
            yield
        yield
'''
def pictureTask(shares):
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
        
    # take picture
    # find brightest spot
    # determine yawDif and pitchDif
    
    while buttonGo == True:
        if s_TimeToTrack.get() == True: # Only aim if given flag to aim
            if yawDif <= 30:
                s_YawOnTarg.put(True)
            else:
                s_YawOnTarg.put(False)
                yawPos = yawDif + yawStartPos
                s_YawPos.put(yawPos)
                
            if pitchDif <= 30:
                s_PitchOnTarg.put(True)
            else:
                s_PitchOnTarg.put(False)
                pitchPos = pitchDif + pitchStartPos
                s_PitchPos.put(pitchPos)
'''
'''    
def fireTask(shares):
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    
    while buttonGo == True:
        if fireState == 0: # Initialization state
            fireState = 1
            
        elif fireState == 1: # Wait until flag to track
            if s_TimeToTrack.get() == True:
                fireState = 2
                
        elif fireState == 2: # Tracking state, spin up flywheels
            pinFlywheel.high() # Spin up flywheels
            
            if s_TimeToFire.get() == True: # Once five seconds have passed, fire
                fireState = 3
            
        elif fireState == 3:
            if s_StopShooting.get() == True: # After ten second shooting window
                fireState = 4
                        
            # set code to actuate servo
            elif s_YawOnTarg.get() == True and s_PitchOnTarg.get() == True:
                pass
                # fire
            
        elif fireState == 4: # Idle state, after ten seconds of shooting
            pinFlywheel.low()
            s_TimeToFire.put(False)
            s_TimeToTrack.put(False)

            # stop firing
    else:
        pinFlywheel.low() # turn the flywheel off
        # turn off firing mechanism
 '''           

buttonInt = pyb.ExtInt(pyb.Pin.board.PC13, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, buttonLogic)


if __name__ == "__main__":

    
    ''' Yaw Setup Below'''
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    tim2 = 5
    moeY = MotorDriver(pinC1,pinA0,pinA1,tim2)
    
    ''' Yaw Encoder Setup Below'''
    pinB6 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.IN)
    pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN)
    encY = EncoderReader(pinB6, pinB7, 4)
    encY.zero()
    
    ''' Pitch Setup Below'''
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    tim1 = 3
    moeP = MotorDriver(pinA10,pinB4,pinB5,tim1)
    
    ''' Pitch Encoder Setup Below'''
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.IN)
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.IN)
    encP = EncoderReader(pinC6, pinC7, 8)
    encP.zero()
    
    # Initialized values
    masterState = 0 # Initialized state of FSM
    fireState = 0 # Initialized state of FSM
    
    zeroPoint = utime.ticks_ms() # Set inital time of the program
    trackPeriod = 4000 # ms, the time between the start and tracking
    firePeriod = 5000 # ms, the time between the start and firing
    idlePeriod = 15000 # ms, the time between the start and the end of firing
    
    pinFlywheel = pyb.Pin(pyb.Pin.board.PC0, pyb.Pin.OUT_PP) # Flywheel port
    
    yawStartPos = 13272 # 180 degrees, ie 3.32 rotations with a gear ratio of 15
    
    pitchStartPos = 2000 # Keep steady heading
    #global buttonGo
    #buttonGo = False
    global buttonCounts
    buttonCounts = 0

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    print('We here 1')
    
    
    # Create a set of shares detailing the statuse of the pitch and firing states
    s_YawPos = task_share.Share('i', thread_protect=False, name="Yaw Position")
    s_PitchPos = task_share.Share('i', thread_protect=False, name="Pitch Position")
    s_YawOnTarg = task_share.Share('b', thread_protect=False, name="Yaw On Target")
    s_PitchOnTarg = task_share.Share('b', thread_protect=False, name="Pitch On Target")
    s_TimeToTrack = task_share.Share('b', thread_protect=False, name="Time To Track")
    s_TimeToFire = task_share.Share('b', thread_protect=False, name="Time To Fire")
    s_StopShooting = task_share.Share('b', thread_protect=False, name="Stop Shooting")
    
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(masterTask, name="Master Task", priority=1, period=10,
                        profile=True, trace=True, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task2 = cotask.Task(yawTask, name="Yaw Task", priority=2, period=40,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task3 = cotask.Task(pitchTask, name="Pitch Task", priority=3, period=40,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    '''
    task4 = cotask.Task(pictureTask, name="Picture Task", priority=5, period=40,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task5 = cotask.Task(fireTask, name="Fire Task", priority=4, period=100,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
                        '''
    
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    '''
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)
    '''
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()
    print('here 2')
    
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
