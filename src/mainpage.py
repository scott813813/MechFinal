##
# \file mainpage.py
# \mainpage ME405 Term Project
# \author mecha12
#  
# \section Design Software Design
# The dueling robot uses a set of tasks to run and target an opponent 
# succesfully. The robot uses MicroPython to control two motors and adjust the
# pitch and yaw axis in order to follow the target found in the provided
# thermal camera. Once the target is located and tracked, the motor engages
# the flywheels and servo motor to propel a dart forward.
#
# Reference:
# \image html Task_Diagram.jpg width=800px
# 
# \subsection Master_Task Master Task
# The master task shares the current turret status with all other tasks. When
# the master task is initilized it moves into the it's state 1, where it sends
# the pitch and yaw motors to move to their initial positions. It next waits until
# 4.9 seconds, in which it will then send a signal to the motors to begin following
# the target based on the position data sent by the camera task, and for the
# flywheels to begin spinning up. Once 5 seconds has been reached, if the yaw
# and pitch motors are both on target, fire the dart by articulating the
# servo motor. Once the ten second firing window passes, powerdown the
# flywheels and send the yaw motor back to its starting position.
#
# Reference: 
# \image html Master_Task_FSM.jpg width=800px
# 

