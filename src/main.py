"""!
@file main.py
    This file manages the tasks in order to run the turret. The motors
    are run using the code developed in the previous ME 405 labs, while
    the tasks to run the camera and firing mechanism are unique to this
    lab assignment.
    
@author mecha12
@date   20-Mar-2023
"""
import gc # Memory allocation garbage collector
import pyb # Micropython library
import utime # Micropython version of time library
import cotask # Run cooperatively scheduled tasks in a multitasking system
import task_share # Tasks share data
import math

from closed_loop_control import clCont # The closed loop control method from closed_loop_control.py
from motor_driver import MotorDriver # The method to drive the motor from motor_drive.py
from encoder_reader import EncoderReader # Read encoder method from encoder_reader.py
from mlx_cam import MLX_Cam # Take values from IR camera
from machine import Pin, I2C # Used for the ISR command 
    
def buttonLogic(pin):
    """!
    @brief   Establishes global variable detecting button presses for use in FSM 
    @details The global, 'buttoncounts' is initialized and incremented by 1  
    @param   pin, the pin on which the button resides, in this case C13
    """
    print('button press')
    global buttonCounts
    buttonCounts += 1
    print(buttonCounts)

def masterTask(shares):
    """!
    @brief   Establishes the FSM controlling all turret tasks and loops through it 
    @details Implemented as a generator function, the masterTask first initializes
             and clears all logical flags governing actions within the FSM. After
             this, the FSM is run through continuously, branching as necessary to
             the appropriate tasks.
    @param   shares, the function managing the task sharing algorithm
    """
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    s_YawOnTarg.put(False) # Input starting value for s_YawOnTarg flag
    s_PitchOnTarg.put(False) # Input starting value for s_PitchOnTarg flag
    s_TimeToTrack.put(False) # Input starting value for s_TimeToTrack flag
    s_TimeToFire.put(False) # Input starting value for s_TimeToFire flag
    s_StopShooting.put(False) # Input starting value for s_StopShooting flag
    masterState = 0 # State variable for masterTask
    while True:
        while buttonCounts == 1: # If the E-Stop button is pressed only once, run the task
            if masterState == 0: # Initilization state
                zeroPoint = utime.ticks_ms()
                masterState = 1
                yield
                
            elif masterState == 1: # Go to aiming position  
                s_YawPos.put(yawStartPos)
                s_PitchPos.put(pitchStartPos)
                masterState = 2
                
                yield
            
            elif masterState == 2: # Wait four seconds until time to track, and then five to fire
                timeElapse = utime.ticks_ms() - zeroPoint # Time since button pressed
                if timeElapse >= idlePeriod: # Stop firing
                    s_StopShooting.put(True)
                    yield
                    
                elif timeElapse >= firePeriod: # Begin firing
                    s_TimeToFire.put(True)
                    yield
                    
                elif timeElapse >= trackPeriod: # Begin tracking
                    s_TimeToTrack.put(True)
                    yield
                yield
        
            yield
        yield

def yawTask(shares):
    """!
    @brief   Communicates with the closed loop controller responsible for yaw control. 
    @details Implemented as a generator function, the yawTask first initializes
             the closed loop controller with an initial Kp, then reads from the encoder,
             calculates the error, and sends this back to the closed loop controller.
    @param   shares, the function managing the task sharing algorithm
    """
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    '''Control Loop Setup'''
    Kp = 0.06 # Proportional gain value
    cll = clCont(0, Kp, 40) # Set proportional constant gain for yaw motor
    while True:
        while buttonCounts == 1: # If the E-Stop button is pressed only once, run the task
            p = encY.read() # Current position of yaw motor
            if p > 60000 or p < -60000:
                encY.zero()
                p = encY.read()
                
            lvl = cll.run(s_YawPos.get(), p) # Run closed loop controller
            moeY.set_duty_cycle(lvl) # Set the duty cycle
            yield
        yield
    yield
                
def pitchTask(shares): 
    """!
    @brief   Communicates with the closed loop controller responsible for pitch control. 
    @details Implemented as a generator function, the pitchTask first initializes
             the closed loop controller with an initial Kp, then reads from the encoder,
             calculates the error, and sends this back to the closed loop controller.
    @param   shares, the function managing the task sharing algorithm
    """
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    '''Control Loop Setup'''
    Kp = 0.07 # Proportial gain value
    cll = clCont(0, Kp, 80) # Set proportional constant gain for yaw motor
    while True:
        while buttonCounts == 1: # If the E-Stop button is pressed only once, run the task
            p = encP.read() # Current position of pitch motor
            if p > 60000 or p < -60000:
                encY.zero()
                p = encY.read()

            lvl = cll.run(s_PitchPos.get(), p) # Run closed loop controller
            moeP.set_duty_cycle(lvl) # Set the duty cycle
            yield
        yield
    yield

def pictureTask(shares):
    """!
    @brief   Communicates with the closed loop controllers responsible for yaw and pitch control,
             and calculates error in position from a thermal image.
    @details Implemented as a generator function, the pictureTask first takes an image, then uses
             the built-in findhottest() function to get the coordinates of the hottest pixel cluster.
             From this, the error in position of the turret is calculated and fed to the closed-loop
             controllers to move the turret to the desired position.
    @param   shares, the function managing the task sharing algorithm
    """
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    s_TimeToTrack.put(False) # State veriable for pictureTask
    while True:    
        while buttonCounts == 1: # If the E-Stop button is pressed only once, run the task
            if s_TimeToTrack.get() == False: # On startup, set datums at the initial encoder readings
                yawDatum = encY.read()
                pitchDatum = encP.read()
                
            elif s_TimeToTrack.get() == True: # Only aim if given flag to aim
                image = camera.get_image()
                H, V = camera.find_hotSpot(image) # Find current hot spot from camera
                print("Yaw Pos ", H, "Pitch Pos", V)
                
                Ke = 8 # Gain value for yaw axis control
                yawTicks = Ke * math.atan(((H - 16)/4)/18)*4000/3.14 + yawDatum # Determine the number of encoder ticks to reach the target in the yaw axis
                print('ticks', yawTicks)
                pitchTicks = math.atan((V*0.75*3.7/12)/18)*4000/3.14 + pitchDatum # Determine the number of encoder ticks to reach the target in the pitch axis

                yawPosRead = encY.read() # Store the current yaw position
                pitchPosRead = encP.read() # Store the current pitch position
                
                yawDif = yawTicks - yawPosRead # Calculate difference between expected and actual yaw position
                if yawDif < 0: # Account for left bias in the yaw control system
                    yawTicks = yawTicks + 1.1 * yawDif
                pitchDif = pitchPosRead - pitchTicks # Calculate difference between expected and actual pitch position
                
                if abs(yawDif) <= 250: # Determine if the yaw position is under the threshold to be on target
                    s_YawOnTarg.put(True)
                    print('yaw on targ')
                    yield
                    
                else: # If the yaw position is not on target, recalculate the yaw position
                    s_YawOnTarg.put(False)
                    print('datum', yawDatum)
                    print('desired', yawTicks)
                    print('current', yawPosRead)
                    s_YawPos.put(int(yawTicks))
                    yield
                    
                if abs(pitchDif) <= 200: # Determine if the pitch position is under the threshold to be on target
                    s_PitchOnTarg.put(True)
                    print('pitch on targ')
                    yield
                    
                else: # If the pitch position is not on target, recalculate the pitch position
                    s_PitchOnTarg.put(False)
                    pitchPos = pitchDif + pitchDatum
                    s_PitchPos.put(int(pitchPos))
                    yield
            yield
        yield
    yield
   
def fireTask(shares):
    """!
    @brief   Fires the turret by spinning the flywheels and articulating the servo motor.
    @details The task first checks that the button has been pressed, then waits 4.9 seconds
             before taking a picture. The flywheels spin up, and if the aiming error is low
             the servo is actuated to fire the turret.
    @param   shares, the function managing the task sharing algorithm.
    """
    s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting = shares
    fireState = 0 # State variable for fireTask
    while True:
        while buttonCounts == 1: # If the E-Stop button is pressed only once, run the task
            if fireState == 0: # Initialization state
                fireState = 1
                yield
                
            elif fireState == 1: # Wait until flag to track
                print('Track', s_TimeToTrack.get())
                if s_TimeToTrack.get() == True:
                    fireState = 2
                    ch2.pulse_width(800) # Set the servo motor back to the neutral position: 800=rest, 1500 = fire!
                    pinFlywheel.high() # Spin up flywheels
                    yield
                yield
                    
            elif fireState == 2: # Tracking state, spin up flywheels
                if s_TimeToFire.get() == True: # Once five seconds have passed, fire
                    fireState = 3
                    yield
                yield
                
            elif fireState == 3: # Fire state, if ready to fire then fire
                if s_StopShooting.get() == True: # After ten second shooting window
                    fireState = 4
                    yield
                            
                elif s_YawOnTarg.get() == True and s_PitchOnTarg.get() == True: # Turn the servo motor on if on target
                    ch2.pulse_width(1500) # Actuate the servo motor: 800=rest, 1500 = fire!
                    print('Fire')  
                yield
                
            elif fireState == 4: # Idle state, after ten seconds of shooting
                pinFlywheel.low()
                s_TimeToFire.put(False)
                s_TimeToTrack.put(False)
                ch2.pulse_width(800) # 800=rest, 1500 = fire!
                s_YawPos.put(0)
                yield
            yield
            
        else: # stop firing
            pinFlywheel.low() # turn the flywheel off
            yield
        yield
    yield

# Set the interrupt button pin
buttonInt = pyb.ExtInt(pyb.Pin.board.PC13, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, buttonLogic) 

if __name__ == "__main__":
    
    '''I2C Setup'''
    i2c_bus = I2C(1)
    camera = MLX_Cam(i2c_bus)

    '''Yaw Setup Below'''
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    tim2 = 5
    moeY = MotorDriver(pinC1,pinA0,pinA1,tim2)
    
    '''Yaw Encoder Setup Below'''
    pinB6 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.IN)
    pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN)
    encY = EncoderReader(pinB6, pinB7, 4)
    encY.zero()
    print(encY.read())
    
    '''Pitch Setup Below'''
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    tim1 = 3
    moeP = MotorDriver(pinA10,pinB4,pinB5,tim1)
    
    '''Pitch Encoder Setup Below'''
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.IN)
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.IN)
    encP = EncoderReader(pinC6, pinC7, 8)
    encP.zero()
    
    '''Servo Setup'''
    pinB3 = pyb.Pin(pyb.Pin.board.PB3, pyb.Pin.OUT_PP)
    tim = pyb.Timer(2, prescaler = 79, period = 19999)
    ch2 = tim.channel(2, pyb.Timer.PWM, pin=pinB3)
    
    zeroPoint = utime.ticks_ms() # Set inital time of the program
    trackPeriod = 4900 # ms, the time between the start and tracking
    firePeriod = 5000 # ms, the time between the start and firing
    idlePeriod = 15000 # ms, the time between the start and the end of firing
    
    pinFlywheel = pyb.Pin(pyb.Pin.board.PC0, pyb.Pin.OUT_PP) # Flywheel port
    
    pinA8 = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.OUT_PP) # Servo port
    
    yawStartPos = 18200 # 180 degrees, ie 3.32 rotations with a gear ratio of 15, 18200 for 180 degrees clockwise
    
    pitchStartPos = 0 # Keep steady heading, -15000 for tilt from downward to median
    global buttonCounts
    buttonCounts = 0

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
    task1 = cotask.Task(masterTask, name="Master Task", priority=1, period=0,
                        profile=True, trace=True, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task2 = cotask.Task(yawTask, name="Yaw Task", priority=2, period=40,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task3 = cotask.Task(pitchTask, name="Pitch Task", priority=3, period=40,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task4 = cotask.Task(pictureTask, name="Picture Task", priority=5, period=500,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
    task5 = cotask.Task(fireTask, name="Fire Task", priority=4, period=100,
                        profile=True, trace=False, shares=(s_YawPos, s_PitchPos, s_YawOnTarg, s_PitchOnTarg, s_TimeToTrack, s_TimeToFire, s_StopShooting))
                        
    # Create the cotask list which will be run later in the program
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()
    
    '''Run Tasks'''
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break