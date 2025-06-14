#!/usr/bin/python
# coding: utf-8

"""
#############################################################################################################
# Andrea Favero 15 March 2024
#
# This script relates to CUBOTino micro, an extremely small and simple Rubik's cube solver robot 3D printed
# CUBOTino micro is the smallest version of the CUBOTino series.
# This specific script controls two servos based on the movements string from Cubotino_m.py
# 
# Possible moves with this robot
# 1) Spins the complete cube ("S") laying on the bottom face: 1 means CW 90deg turns, while 3 means 90CCW turn
# 2) Flips the complete cube ("F") by "moving" the Front face to Bottom face: Only positive values are possible
# 3) Rotates the bottom layer ("R") while costraining the 2nd and 3rd layer.
# 4) The order of S, F has to be strictly followed
# 5) Example 'F1R1S3' means: 1x cube Flip, 1x (90deg) CW rotation of the 1st (Down) layer, 1x (90deg) CCW cube Spin
#
# For Rotations, the bottom servo makes a little extra rotation than target, before coming back to target; This
# is needed to recover the gaps between cube_hoder - cube - top_cover, and still getting a decent cube layers alignment.
#
#
# Developped on:
#  - Raspberry Pi Zero2 
#  - Raspberry Pi OS (Legacy) A port of Debian Buster with security updates and desktop environment
#    (Linux raspberry 5.10.103-v7+ #1529 SMP Tue 8 12:21:37 GMT 2022 armv71 GNU/Linux)
#
#############################################################################################################
"""



from Cubotino_m_settings_manager import settings as settings   # custom library managing the settings from<>to the settings files


##################    imports for the display part   ################################
from Cubotino_m_display import display as s_disp
s_disp.set_backlight(0)                           # display backlight is set off
s_disp.show_cubotino()      # show cubotino logo on display, when this script is imported
s_disp.set_backlight(1)                             # activates the display backlight
# ##################################################################################





##################    imports and servo_settings for Servos and LED   ####################
import time                                       # import time library
import RPi.GPIO as GPIO                           # import RPi GPIO library
GPIO.setmode(GPIO.BCM)                            # setting GPIO pins as "Broadcom SOC channel" number, these are the numbers after "GPIO"
GPIO.setwarnings(False)                           # setting GPIO to don't return allarms
from gpiozero import Servo, PWMLED                # import modules for the PWM part
from gpiozero.pins.pigpio import PiGPIOFactory    # pigpio library is used, to use hardare timers on PWM (to avoid servo jitter)
factory = PiGPIOFactory()                         # pin factory setting to use hardware timers, to avoid servo jitter

# servo_settings for the led on top cover, to ensure sufficient light while the PiCamera is reading
top_cover_led_pin = 19                            # GPIO pin used to control the LED on/off

# NOTE: High frequency on the led PWM is needed to prevent the camera to see the led flickering
top_cover_led = PWMLED(top_cover_led_pin, active_high=True, initial_value=0, frequency=5000000, pin_factory=factory)

# overall servo_settings for the GPIO and the PWM
t_servo_pin = 13                  # GPIO pin used for the top servo
b_servo_pin = 12                  # GPIO pin used for the bottom servo
# ##################################################################################



##################    general servo_settings    ####################################
robot_init_status=False         # boolean to track the servos inititialization status
stop_servos=True                # boolean to stop the servos during solving proces: It is set true at the start, servos cannot operate
b_servo_operable=False          # variable to block/allow bottom servo operation
fun_status=False                # boolean to track the robot fun status, it is True after solving the cube :-)
s_debug=False                   # boolean to print out info when debugging
flip_to_close_one_step = False  # f_to_close steps (steps from flip up to close) is set false (=2 steps)
# ##################################################################################





def init_servo(print_out=s_debug, start_pos=0, f_to_close_mode=False):
    """ Function to initialize the robot (servos position) and some global variables, do be called once, at the start.
        Parameters are imported from a json file, to make easier to list/document/change the variables
        that are expected to vary on each robot.
        These servo_settings are under a function, instead of root, to don't be executed when this script is used from CLI
        with arguments; In this other case the aim is to help setting the servo to their mid position."""
    
    global t_servo, t_min_pulse_width, t_max_pulse_width, t_top_cover                       # top servo, pulse width, status
    global t_servo_close, t_servo_open, t_servo_read, t_servo_flip, t_servo_rel             # top servo related angles and status
    global t_flip_to_close_time, t_close_to_flip_time, t_flip_open_time, t_open_close_time, t_rel_time  # top servo timers
    
    global b_servo, b_min_pulse_width, b_max_pulse_width                                    # bottom servo and pulse width
    global b_servo_CCW, b_servo_CW, b_home, b_rel_CW, b_rel_CCW, b_extra_home_CW, b_extra_home_CCW   # bottom servo angles
    global b_servo_CCW_rel, b_servo_CW_rel, b_home_from_CCW, b_home_from_CW                 # bottom servo calculated angles
    global b_servo_home, b_servo_stopped, b_servo_CW_pos, b_servo_CCW_pos                   # bottom servo status 
    global b_spin_time, b_rotate_time, b_rel_time                                           # bottom servo timers 
    
    global flip_to_close_one_step, robot_init_status, fun_status, led_init_status           # robot related
    
    
    if not robot_init_status:                        # case the inititialization status of the servos false
        if f_to_close_mode:                          # case the init got the f_to_close_mode as true
            flip_to_close_one_step = True            # flip_to_close_one_step is set true
        
        servo_settings = settings.get_servos_settings()  # settings are retrieved from the settings Class

        if print_out:                                # case print_out variable is set true
            fname = settings.get_servo_settings_fname() # settings filename is retrieved
            print('\nImporting servos settings from the text file:', fname)    # feedback is printed to the terminal
            print('\nImported parameters: ')         # feedback is printed to the terminal
            for param, s in servo_settings.items():  # iteration over the settings dict
                print(param,': ', s)                 # feedback is printed to the terminal
            print()
              
        try:
            t_min_pulse_width = servo_settings['t_min_pulse_width']        # defines the min Pulse With the top servo reacts to
            t_max_pulse_width = servo_settings['t_max_pulse_width']        # defines the max Pulse With the top servo reacts to
            t_servo_close = servo_settings['t_servo_close']                # Top_cover close position, in gpiozero format
            t_servo_open = servo_settings['t_servo_open']                  # Top_cover open position, in gpiozero format
            t_servo_read = servo_settings['t_servo_read']                  # Top_cover camera read position, in gpiozero format
            t_servo_flip = servo_settings['t_servo_flip']                  # Top_cover flip position, in gpiozero format
            t_servo_rel_delta = servo_settings['t_servo_rel_delta']        # Top_cover release angle movement from the close position to release tension
            t_flip_to_close_time = servo_settings['t_flip_to_close_time']  # time for Top_cover from flip to close position
            t_close_to_flip_time = servo_settings['t_close_to_flip_time']  # time for Top_cover from close to flip position 
            t_flip_open_time = servo_settings['t_flip_open_time']          # time for Top_cover from open to flip position, and viceversa  
            t_open_close_time = servo_settings['t_open_close_time']        # time for Top_cover from open to close position, and viceversa
            t_rel_time = servo_settings['t_rel_time']                      # time for Top_cover to release tension from close position

            b_min_pulse_width = servo_settings['b_min_pulse_width']        # defines the min Pulse With the bottom servo reacts to
            b_max_pulse_width = servo_settings['b_max_pulse_width']        # defines the max Pulse With the bottom servo reacts to
            b_servo_CCW = servo_settings['b_servo_CCW']                    # Cube_holder max CCW angle position
            b_servo_CW = servo_settings['b_servo_CW']                      # Cube_holder max CW angle position
            b_home = servo_settings['b_home']                              # Cube_holder home angle position
            b_rel_CCW = servo_settings['b_rel_CCW']                        # Cube_holder release angle from CCW angle positions, to release tension
            b_rel_CW = servo_settings['b_rel_CW']                          # Cube_holder release angle from CW angle positions, to release tension
            b_extra_home_CW = servo_settings['b_extra_home_CW']            # Cube_holder release angle from home angle positions, to release tension
            b_extra_home_CCW = servo_settings['b_extra_home_CCW']          # Cube_holder release angle from home angle positions, to release tension
            b_spin_time = servo_settings['b_spin_time']                    # time for Cube_holder to spin 90 deg (cune not contrained)
            b_rotate_time = servo_settings['b_rotate_time']                # time for Cube_holder to rotate 90 deg (cube constrained)
            b_rel_time = servo_settings['b_rel_time']                      # time for Cube_holder to release tension at home, CCW and CW positions
        
        
        except:   # exception will be raised if json keys differs, or parameters cannot be converted to float
            print('Error on converting to float the imported parameters (at Cubotino_m_servos.py)')   # feedback is printed to the terminal                                  
            return robot_init_status                                        # return robot_init_status variable, that is False
        
        if start_pos==0:                    # case the servos initial position equals zero (very first setting)
            t_servo = t_servo_create(t_min_pulse_width, t_max_pulse_width)  # t_servo servo object creation
            b_servo = b_servo_create(b_min_pulse_width, b_max_pulse_width)  # b_servo servo object creation                 

        else:                               # case the servos initial position differes from zero
            t_servo = t_servo_create(t_min_pulse_width, t_max_pulse_width, t_servo_open)  # t_servo servo object creation
            b_servo = b_servo_create(b_min_pulse_width, b_max_pulse_width, b_home)        # b_servo servo object creation

            t_top_cover = start_pos                               # variable to track the top cover/lifter position              
            b_servo_home=True                                     # boolean of bottom servo at home
            b_servo_stopped = True                                # boolean of bottom servo at location the lifter can be operated
            b_servo_CW_pos=False                                  # boolean of bottom servo at full CW position
            b_servo_CCW_pos=False                                 # boolean of bottom servo at full CCW position


            # bottom servo derived positions
            b_servo_CCW_rel = round(b_servo_CCW + b_rel_CCW,3)    # bottom servo position to rel tensions when fully CW
            b_servo_CW_rel = round(b_servo_CW - b_rel_CW,3)       # bottom servo position to rel tensions when fully CCW
            b_home_from_CW = round(b_home - b_extra_home_CW,3)    # bottom servo extra home position, when moving back from full CW
            b_home_from_CCW = round(b_home + b_extra_home_CCW,3)  # bottom servo extra home position, when moving back from full CCW
            
            # top servo derived position
            t_servo_rel = round(t_servo_close - t_servo_rel_delta,3)     # top servo position to release tension

            robot_init_status = True          # boolean to track the inititialization status of the servos is set true
            if print_out:                     # case the print_out variable is set true
                print("servo init done")      # feedback is printed to the terminal
        
            servo_start_pos(start_pos)        # servos are positioned to the start position    
            fun_status=False                  # boolean to track the robot fun status, it is True after solving the cube :-)
            cam_led_test()                    # makes a very short led test
            cam_led_Off()                     # forces the led off
    
    return robot_init_status







def t_servo_create(t_min_pulse_width, t_max_pulse_width, initial_pos=0):
    """top servo object creation."""
    global t_servo_pin, factory, t_servo
    
    try:                          # tentative
        t_servo                   # name of t_servo
        t_servo.close()
    except NameError:             # case a name error exception is raised
        pass
    
    t_servo = Servo(t_servo_pin,                                 # GPIO pin associated to the top servo
                    initial_value = initial_pos,                 # Top_cover positioned to initial_pos
                    min_pulse_width = t_min_pulse_width/1000,    # min Pulse Width the top servo reacts to
                    max_pulse_width = t_max_pulse_width/1000,    # max Pulse Width the top servo reacts to
                    frame_width=0.020,
                    pin_factory=factory)                         # way to use hardware based timers for the PWM
    
    time.sleep(0.7)          # time to let the servo reaching the initial_value angle
    return t_servo





def b_servo_create(b_min_pulse_width, b_max_pulse_width, initial_pos=0):
    """bottom servo object creation."""
    global b_servo_pin, factory, b_servo

    try:                          # tentative
        b_servo                   # name of b_servo
        b_servo.close()
    except NameError:             # case a name error exception is raised
        pass
    
    b_servo = Servo(b_servo_pin,                                # GPIO pin associated to the bottom servo
                    initial_value = initial_pos,                 # Cube_holder positioned to initial_pos
                    min_pulse_width = b_min_pulse_width/1000,    # min Pulse Width the bottom servo reacts to
                    max_pulse_width = b_max_pulse_width/1000,    # max Pulse Width the bottom servo reacts to
                    frame_width=0.020,
                    pin_factory=factory)                         # way to used hardware based timers for the PWM
    
    time.sleep(0.7)          # time to let the servo reaching the initial_value angle
    return b_servo







def servo_tune_via_gui(debug, start_pos):
    
    global robot_init_status, stop_servos, b_servo_operable, s_debug
    
    robot_init_status=False        # boolean to track the servos inititialization status
    s_debug=debug                  # boolean to print out info when debugging
    robot_init_status = init_servo(s_debug, start_pos)
    stop_servos=False              # boolean to stop the servos during solving proces: It is set true at the start, servos cannot operate
    b_servo_operable=True          # variable to block/allow bottom servo operation
    return robot_init_status
    







def quit_func():
    """ Sets the used GPIO as output, and force them to low. This wants to prevent servos to move after closing the script."""
    
    GPIO.setup(top_cover_led_pin, GPIO.OUT, initial=GPIO.LOW)   # GPIO top_cover_led_pin (Top_cover_Led) is set as output, and force low
    GPIO.setup(t_servo_pin, GPIO.OUT, initial=GPIO.LOW)         # GPIO t_servo_pin (Top_cover servo) is set as output, and force low
    GPIO.setup(b_servo_pin, GPIO.OUT, initial=GPIO.LOW)         # GPIO b_servo_pin (Cube_holder servo) is set as output, and force low






def cam_led_On(value=0.5):
    """ Sets the top_cover led ON, with brightness in arg. Value ranges from 0 to 0.3"""
    top_cover_led.value = value         # top cover led PWM is set to arg value






def cam_led_Off():
    """ Sets the top_cover led OFF."""
    top_cover_led.off()      # top cover led PWM is set to 0






def cam_led_test():
    """ Fade the led On and Off at the init, to show the led worwing."""
    
    for i in range(50,100,4):            # iterates from 0 to 28 in steps of 4 
        top_cover_led.value = i/100    # top cover led PWM is set iterator %
        time.sleep(0.02)               # very short time sleep
    
    for i in range(100,46,-4):          # iterates from 28 to 0 in steps of -4 
        top_cover_led.value = i/100    # top cover led PWM is set iterator %
        time.sleep(0.02)               # very short time sleep
    
    top_cover_led.off()      # top cover led PWM is set to 0






def servo_start_pos(start_pos):
    """Servos are positioned to the intended start position, meaning top_cover on read position and cube_holder on its middle position"""
    
    global t_servo_open, t_top_cover
    global b_servo_operable, b_servo_stopped,  b_servo_home, b_servo_CW_pos, b_servo_CCW_pos
    global stop_servos
    
    stop_servos=False                 # boolean to stop the servos during solving process is set False: servos can be operated
    b_servo_operable=False            # variable to block/allow bottom servo operation
    
    
    t_servo.value = t_servo_open      # top servo is positioned in open position
    time.sleep(t_close_to_flip_time)  # time to allow the top_cover/lifter to reach the open postion   
    t_top_cover = 'open'              # variable to track the top cover/lifter position
    b_servo_operable=True             # variable to block/allow bottom servo operation
    
    
    b_servo.value = b_home            # bottom servo moves to the home position, releasing then the tensions
    time.sleep(b_rotate_time)         # time for the servo to release the tensions
    
    b_servo_stopped = True            # boolean of bottom servo at location the lifter can be operated
    b_servo_home=True                 # boolean of bottom servo at home
    b_servo_CW_pos=False              # boolean of bottom servo at full CW position
    b_servo_CCW_pos=False             # boolean of bottom servo at full CCW position
    
    if start_pos == 'read':           # case the top cover initial position is 'read'
        b_servo_operable=False        # variable to block/allow bottom servo operation
        t_servo.value = t_servo_read  # top servo is positioned in read position at the start
        time.sleep(t_flip_open_time)  # time to allow the top_cover/lifter to reach the read postion
        t_top_cover = 'read'          # variable to track the top cover/lifter position
    
    elif start_pos == 'open':         # case the top cover initial position is 'open'
        t_top_cover = 'open'          # variable to track the top cover/lifter position
        
    
    cam_led_Off()                     # forces the top_cover_led to off






def servo_off():
    """ Function to stop sending the PWM the servos."""
    
    t_servo.detach()             # PWM is stopped at the GPIO pin for top servo
    b_servo.detach()             # PWM is stopped at the GPIO pin for bottom servo
    return







def stopping_servos(print_out=s_debug):
    """ Function to stop the servos."""
    global stop_servos
    
    if print_out:                         # case the print_out variable is set true
        print("\ncalled the servos stopping function\n")   # feedback is printed to the terminal
    stop_servos=True                      # boolean to stop the servos during solving process, is set true: Servos are stopped







def stop_release(print_out=s_debug):
    """ Function to relelease the stop from servos."""
    
    global stop_servos
    
    if print_out:                          # case the print_out variable is set true
        print("\ncalled the stop release function\n")  # feedback is printed to the terminal
    stop_servos=False            # boolean to stop the servos during solving process, is set false: Servo can be operated







def open_pos():
    """ Function to position the top_cover to the open position, without waiting time !!!"""
    global t_top_cover, b_servo_operable, b_servo_stopped
    
    if not stop_servos:                          # case there is not a stop request for servos
        if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False               # variable to block/allow bottom servo operation
            t_servo.value = t_servo_open         # servo is positioned to open
            t_top_cover='open'                   # cover/lifter position variable set to open
            b_servo_operable=True                # variable to block/allow bottom servo operation







def read():
    """ Function to position the top_cover to the read."""
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    if not stop_servos:                          # case there is not a stop request for servos
        if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False               # variable to block/allow bottom servo operation
            if t_top_cover == 'close':           # cover/lifter position variable set to close
                t_servo.value = t_servo_read     # servo is positioned to flip the cube
                time.sleep(t_close_to_flip_time) # time for the servo to reach the flipping position from close position
            elif t_top_cover == 'open':          # cover/lifter position variable set to open
                t_servo.value = t_servo_read     # servo is positioned to flip the cube
                time.sleep(t_flip_open_time)     # time for the servo to reach the flipping position
            elif t_top_cover == 'flip':          # cover/lifter position variable set to flip (only possible when gui_test)
                t_servo.value = t_servo_read     # servo is positioned to flip the cube
                time.sleep(t_flip_open_time)     # time for the servo to reach the flipping position 
            
            t_top_cover='read'                   # cover/lifter position variable set to flip
            return 'read'                        # position of the top_cover is returned







def flip_up():
    """ Function to raise the flipper to the upper position, to flip the cube around its horizontal axis."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    if not stop_servos:                          # case there is not a stop request for servos
        if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False               # variable to block/allow bottom servo operation
            if t_top_cover == 'close':           # cover/lifter position variable set to close
                if not flip_to_close_one_step:   # case the flip to close is not set to one step (the slow way, not requiring perfect tuning)
                    t_servo.value = t_servo_read # servo is positioned to the read position
                    time.sleep(t_close_to_flip_time) # time for the servo to reach the read position from close position
                    t_servo.value = t_servo_flip # servo is positioned to flip the cube
                    time.sleep(t_flip_open_time) # time for the servo to reach the read position from close position
                else:                            # case the flip to close is set to one step (the fast way, requiring good tuning)
                    t_servo.value = t_servo_flip # servo is positioned to flip the cube
                    time.sleep(t_close_to_flip_time) # time for the servo to reach the flipping position from close position
                    
            elif t_top_cover == 'open' :         # cover/lifter position variable set to open positions
                if not flip_to_close_one_step:   # case the flip to close is not set to one step (the slow way, not requiring perfect tuning)
                    t_servo.value = t_servo_read # servo is positioned to the read position
                    time.sleep(t_flip_open_time) # time for the servo to reach the read position from close position
                    t_servo.value = t_servo_flip # servo is positioned to flip the cube
                    time.sleep(t_flip_open_time) # time for the servo to reach the read position from close position
                else:                            # case the flip to close is set to one step (the fast way, requiring good tuning)
                    t_servo.value = t_servo_flip # servo is positioned to flip the cube
                    time.sleep(t_flip_open_time) # time for the servo to reach the flipping position
            
            elif t_top_cover == 'read':          # cover/lifter position variable set to open or read positions
                    t_servo.value = t_servo_flip # servo is positioned to flip the cube
                    time.sleep(t_flip_open_time) # time for the servo to reach the flipping position
            
            t_top_cover='flip'                   # cover/lifter position variable set to flip







def flip_to_read():
    """ Function to raise the top cover to the open position. The cube is not contrained by the top cover or the flipper."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    if not stop_servos:                          # case there is not a stop request for servos
        if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False               # variable to block/allow bottom servo operation
            t_servo.value = t_servo_read         # top servo is positioned in read top cover position, from flip position
            time.sleep(t_flip_open_time)         # time for the top servo to reach the open top cover position
            t_top_cover='open'                   # variable to track the top cover/lifter position
            b_servo_operable=True                # variable to block/allow bottom servo operation






def flip_to_open():
    """ Function to raise the top cover to the open position. The cube is not contrained by the top cover or the flipper."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    if not stop_servos:                          # case there is not a stop request for servos
        if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False               # variable to block/allow bottom servo operation
            t_servo.value = t_servo_open         # top servo is positioned in open top cover position, coming from flip
            time.sleep(t_flip_open_time)         # time for the top servo to reach the open top cover position
            t_top_cover='open'                   # variable to track the top cover/lifter position
            b_servo_operable=True                # variable to block/allow bottom servo operation






def flip_to_close():
    """ Function to lower the flipper to the close position, position that contrains the cube with the top cover."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    if not stop_servos:                            # case there is not a stop request for servos
        if b_servo_stopped==True:                  # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False                 # variable to block/allow bottom servo operation
            
            if not flip_to_close_one_step:        # case the flip to close is not set to one step
                t_servo.value = t_servo_read       # servo is positioned to read position, to let the cube falling onto the holder
                time.sleep(t_flip_to_close_time)   # time for the servo to reach the flipping position
                t_top_cover == 'read'              # variable to track the top cover/lifter position
            
            t_servo.value = t_servo_close          # servo is positioned to constrain the mid and top cube layers
            
            if t_top_cover == 'flip' or t_top_cover == 'read':  # cover/lifter position variable set to flip
                time.sleep(t_flip_to_close_time)   # time for the servo to reach the close position
            
            elif t_top_cover == 'open':            # cover/lifter position variable set to open or read positions
                time.sleep(t_open_close_time)      # time for the servo to reach the flipping position

            if t_servo_rel < t_servo_close:        # case the t_servo_rel_delta is > zero
                t_servo.value = t_servo_rel        # servo is positioned to release the tention from top of the cube (in case of contact)
                time.sleep(t_rel_time)             # time for the servo to release the tension
                
            t_top_cover='close'                    # cover/lifter position variable set to close
            b_servo_operable=True                  # variable to block/allow bottom servo operation






def flip():
    """ Flips the cube during the cube detection phase, and places the top_cover (piCamera) in read position."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    
    flip_up()
    
    if not stop_servos:                        # case there is not a stop request for servos
        if b_servo_stopped==True:              # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False             # variable to block/allow bottom servo operation
            t_servo.value = t_servo_read       # top servo is positioned in top cover read position
            time.sleep(t_flip_open_time+0.1)   # time for the top servo to reach the top cover read position
            t_top_cover='read'                 # variable to track the top cover/lifter position
            b_servo_operable=False             # variable to block/allow bottom servo operation






def flip_toggle(current_pos, t_servo_read, t_servo_flip):
    """ Toggles between Fip and read position (used by the GUI)."""
    
    global t_top_cover
    
    if current_pos != 'flip':              # case the top_cover is not in flip position
        t_servo.value = t_servo_flip       # the top cover is positioned to flip_up position
        t_top_cover='flip'                 # variable to track the top cover/lifter position
        return 'flip'                      # position of the top_cover is returned
    
    elif current_pos == 'flip':            # case the top_cover is in flip position
        t_servo.value = t_servo_read       # top servo is positioned to read position
        t_top_cover = 'read'               # read position is assigned to t_top_cover variable
        return 'read'                      # position of the top_cover is returned








def open_cover(target=0, test=False):
    """ Function to open the top cover from the close position, to release the contrain from the cube."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, t_servo_open

    if not stop_servos:                            # case there is not a stop request for servos
        if b_servo_stopped==True:                  # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False                 # variable to block/allow bottom servo operation
            if test:                               # case the test variable is set True (used by the GUI)
                t_servo_open = target              # thepassed target value is assigned to local variable t_servo_open
            t_servo.value = t_servo_open           # servo is positioned to open
            time.sleep(t_open_close_time)          # time for the servo to reach the open position
            t_top_cover='open'                     # variable to track the top cover/lifter position
            b_servo_operable=True                  # variable to block/allow bottom servo operation
            return 'open'                          # position of the top_cover is returned







def close_cover(target=0, release=0, timer1=0, timer2=0, test=False):
    """ Function to close the top cover, to contrain the cube.
        Parameters in argument are used by the GUI to set/test the servos positions."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, t_servo_close, t_servo_rel
    

    if not stop_servos:                            # case there is not a stop request for servos
        if b_servo_stopped==True:                  # boolean of bottom servo at location the lifter can be operated
            b_servo_operable=False                 # variable to block/allow bottom servo operation
            
            if test:                               # case the test variable is set True (used by the GUI)                 
                t_servo.value = target             # servo is positioned to open
                time.sleep(timer1)                 # time for the servo to reach the open position
                if t_servo_rel < t_servo_close:    # case the t_servo_rel_delta is > zero
                    t_servo.value = target - release   # servo is positioned to release the tention from top of the cube (in case of contact)
                    time.sleep(timer2)             # time for the servo to release the tension
            else:                                  # case the test variable is set False (function not used by the GUI)
                t_servo.value = t_servo_close      # servo is positioned to open
                time.sleep(t_open_close_time)      # time for the servo to reach the open position
                if t_servo_rel < t_servo_close:    # case the t_servo_rel_delta is > zero
                    t_servo.value = t_servo_rel    # servo is positioned to release the tention from top of the cube (in case of contact)
                    time.sleep(t_rel_time)         # time for the servo to release the tension
            
            t_top_cover='close'                    # cover/lifter position variable set to close
            b_servo_operable=True                  # variable to block/allow bottom servo operation
            return 'close'                         # position of the top_cover is returned






def spin_out(direction, target=0, release=0, timer1=0, test=False):
    """ Function that spins the cube holder toward CW or CCW.
        During the spin the cube is not contrained by the top cover.
        The cube holder stops to the intended position, without making extra rotation.
        Parameters in argument are used by the GUI to set/test the servos positions."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, b_servo_CW_pos, b_servo_CCW_pos, b_servo
           
    if not b_servo_operable and t_top_cover=='read':
        flip_to_open()
        
    if not stop_servos:                              # case there is not a stop request for servos
        if b_servo_operable==True:                   # variable to block/allow bottom servo operation
            if b_servo_home==True or test:           # boolean of bottom servo at home
                b_servo_stopped=False                # boolean of bottom servo at location the lifter can be operated
                b_servo_CW_pos=False                 # boolean of bottom servo at full CW position
                b_servo_CCW_pos=False                # boolean of bottom servo at full CCW position
                
                if direction=='CCW':                 # case the set direction is CCW
                    if test:                         # case the variable test is set True
                        b_servo.value = target       # bottom servo moves to the most CCW position
                        time.sleep(timer1)           # time to let the servo reaching the CCW position
                        if release > 0:              # case release variable is > than 0
                            b_servo.value = target + release   # bottom servo moves back of releave value
                    else:                            # case the variable test is set False
                        b_servo.value = b_servo_CCW_rel  # bottom servo moves to almost the max CCW position
                        time.sleep(b_spin_time)      # time for the bottom servo to reach the most CCW position
                        b_servo_CCW_pos=True         # boolean of bottom servo at full CCW position
                
                elif direction=='CW':                # case the set direction is CW
                    if test:                         # case the variable test is set True
                        b_servo.value = target       # bottom servo moves to the most CW position 
                        time.sleep(timer1)           # time to let the servo reaching the CCW position
                        if release > 0:              # case release variable is > than 0
                            b_servo.value = target - release   # bottom servo moves back of releave value
                    else:                            # case the variable test is set False
                        b_servo.value = b_servo_CW_rel   # bottom servo moves to almost the max CW position 
                        time.sleep(b_spin_time)      # time for the bottom servo to reach the most CW position
                        b_servo_CW_pos=True          # boolean of bottom servo at full CW position
                
                b_servo_stopped=True                 # boolean of bottom servo at location the lifter can be operated
                b_servo_home=False                   # boolean of bottom servo at home
                b_servo_stopped=True                 # boolean of bottom servo at location the lifter can be operated
                return direction                     # position of the holder is returned







def spin_home():
    """ Function that spins the cube holder to home position.
        During the spin the cube is not contrained by the top cover.
        The cube holder stops to home position, without making extra rotation."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, b_servo_CW_pos, b_servo_CCW_pos
    
    if not b_servo_operable and t_top_cover=='read':
        flip_to_open()
    
    if not stop_servos:                         # case there is not a stop request for servos
        if b_servo_operable==False:             # variable to block/allow bottom servo operation
            open_cover()                        # top servo is moved to open position
        elif b_servo_operable==True:            # variable to block/allow bottom servo operation
            if b_servo_home==False:             # boolean of bottom servo at home
                b_servo_stopped = False         # boolean of bottom servo at location the lifter can be operated
                b_servo.value = b_home          # bottom servo moves to the home position, releasing then the tensions
                time.sleep(b_spin_time)         # time for the bottom servo to reach the extra home position
                b_servo_stopped=True            # boolean of bottom servo at location the lifter can be operated
                b_servo_home=True               # boolean of bottom servo at home
                b_servo_CW_pos=False            # boolean of bottom servo at full CW position
                b_servo_CCW_pos=False           # boolean of bottom servo at full CCW position
                return 'home'                   # position of the holder is returned







def spin(direction):
    """ Spins the cube during the cube detection phase"""
    
    spin_out(direction)  # calls the spin_out function
    spin_home()          # calls the spin home function






def rotate_out(direction):
    """ Function that rotates the cube holder toward CW or CCW position; During the rotation the cube is contrained by the top cover.
        The cube holder makes first an extra rotation, and later it comes back to the intended position; This approach
        is used for a better facelets alignment to the faces, and to relese the friction (cube holder - cube - top cover)."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, b_servo_CW_pos, b_servo_CCW_pos
    
    if not stop_servos:                                   # case there is not a stop request for servos
        if t_top_cover!='close':                          # case the top cover is not in close position
            close_cover()                                 # top cover is lowered in close position
        
        if b_servo_operable==True:                        # variable to block/allow bottom servo operation
            if b_servo_home==True:                        # boolean of bottom servo at home=
                b_servo_stopped=False                     # boolean of bottom servo at location the lifter can be operated
                
                if direction=='CCW':                      # case the set direction is CCW
                    b_servo.value = b_servo_CCW           # bottom servo moves to the most CCW position
                    time.sleep(b_rotate_time)             # time for the bottom servo to reach the most CCW position
                    b_servo.value = b_servo_CCW_rel       # bottom servo moves slightly to release the tensions
                    time.sleep(b_rel_time)                # time for the servo to release the tensions
                    b_servo_CCW_pos=True                  # boolean of bottom servo at full CCW position
                    
                elif direction=='CW':                     # case the set direction is CW
                    b_servo.value = b_servo_CW            # bottom servo moves to the most CCW position
                    time.sleep(b_rotate_time)             # time for the bottom servo to reach the most CCW position
                    b_servo.value = b_servo_CW_rel        # bottom servo moves slightly to release the tensions
                    time.sleep(b_rel_time)                # time for the servo to release the tensions
                    b_servo_CW_pos=True                   # boolean of bottom servo at full CW position
                    
                b_servo_stopped=True                      # boolean of bottom servo at location the lifter can be operated
                b_servo_home=False                        # boolean of bottom servo at home
                
                if t_top_cover=='close':                  # case the top cover is in close position
                    open_cover()                          # top cover is raised in open position
                
                return 'direction'                   # position of the holder is returned








def rotate_home(direction, home=0, release=0, timer1=0, test=False):
    """ Function that rotates the cube holder to home position; During the rotation the cube is contrained by the top cover.
        The cube holder makes first an extra rotation, and later it comes back to the home position; This approach
        is used for a better facelets alignment to the faces, and to relese the friction (cube holder - cube - top cover).
        Release and test parameters are used by the GUI to set/test the servos positions."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, b_servo_CW_pos, b_servo_CCW_pos, b_home
    
    if not stop_servos:                                # case there is not a stop request for servos
        if b_servo_operable==True:                     # variable to block/allow bottom servo operation
            if b_servo_home==False:                    # boolean of bottom servo at home
                
                if not test:                           # case the test variable is set False (no GUI iteraction)
                    if (t_top_cover!='close'):         # case the top cover is not in close position
                        close_cover()                  # top cover is lowered in close position
                    if direction=='CCW':               # case the set direction is CCW
                        if b_servo_CW_pos==True:       # boolean of bottom servo at full CW position
                            b_servo.value = b_home_from_CW   # bottom servo moves to the extra home position, from CW
                    elif direction=='CW':              # case the set direction is CW
                        if b_servo_CCW_pos==True:      # boolean of bottom servo at full CW position
                            b_servo.value = b_home_from_CCW  # bottom servo moves to the extra home position, from CCW
                    time.sleep(b_rotate_time)          # time for the bottom servo to reach the extra home position
                    b_servo.value = b_home                 # bottom servo moves to the home position, releasing then the tensions
                    time.sleep(b_rel_time)                 # time for the servo to release the tensions
                    b_servo_stopped=True                   # boolean of bottom servo at location the lifter can be operated
                    b_servo_home=True                      # boolean of bottom servo at home
                    b_servo_CW_pos=False                   # boolean of bottom servo at full CW position
                    b_servo_CCW_pos=False                  # boolean of bottom servo at full CCW position
                    
                    if not test:
                        open_cover()                       # top cover is raised in open position
                
                
                elif test:                             # case the test variable is set True (GUI iteraction)
                    b_home = home                      # the passed home variable is assigned to the local b_home      
                    if direction=='CCW':               # case the set direction is CCW
                        b_servo.value = b_home - release   # bottom servo moves to the extra home position, from CW
                    elif direction=='CW':              # case the set direction is CW
                        b_servo.value = b_home + release   # bottom servo moves to the extra home position, from CCW
                    time.sleep(timer1)                 # time for the bottom servo to reach the extra home position
                    b_servo.value = b_home             # bottom servo moves to the home position, releasing then the tensions
                    return 'home'







def servo_to_pos(servo, pos, rel=''):
    """function that sets the the'ref' servo to the position 'val'.
        This function is used by the GUI sliders to set/test the servos positions"""
    
    if pos>= -1 and pos<= 1:               # case the pos variable in argument is within the range from -1 to 1 included
        try:                               # tentative
            if servo == 'top':             # case the servo variable in argument equals to 'top'
                t_servo.value = pos        # top servo is set to position pos
                time.sleep(1)              # short sleeping time
                if rel != '':              # case the rel variable (release position) in argument is not an empty string
                    t_servo.value = rel    # top servo is set to rel pos
                
            elif servo == 'bottom':        # case the servo variable in argument equals to 'bottom'
                b_servo.value = pos        # bottom servo is set to position pos
                time.sleep(1)              # short sleeping time
                if rel != '':              # case the rel variable (release position) in argument is not an empty string
                    b_servo.value = rel    # bottom servo is set to rel pos
            
            else:                          # case the servo variable in argument is not recognized
                print("wrong servo name at servo_to_pos function")  # feedback is printed to the terminal
                
        except:                            # case an exception is raised
            print("exceptioin raised at servo_to_pos function")  # feedback is printed to the terminal
    
    else:                                  # case the pos variable in argument is not in range from -1 to 1 included
        print("accepted values are from -1.0 to 1.0")  # feedback is printed to the terminal








def check_moves(moves, print_out=s_debug):
    """ Function that counts the total servo moves, based on the received moves string.
        This function also verifies if the move string is compatible with servo contrained within 180 deg range (from -90 to 90 deg):
        Not possible to rotate twice +90deg (or -90deg) from the center, nor 3 times +90deg (or -90deg) from one of the two extremes."""
    
    servo_angle=0                                         # initial angle is set to zero, as this is the starting condition at string receival
    servo_angle_ok=True                                   # boolean to track the check result
    tot_moves=0                                           # counter for the total amount of servo moves (1x complete flip, 1x each 90 deg cube spin or 1st layer rotation)
    
    for i in range(len(moves)):                           # iteration over all the string characters
        if moves[i]=='1':                                 # case direction is CW 
            if moves[i-1] == 'R' or moves[i-1] == 'S':    # case the direction refers to cube spin or layer rotation
                servo_angle+=90                           # positive 90deg angle are added to the angle counter
                tot_moves+=1                              # counter is increased

        elif moves[i]=='3':                               # case direction is CW 
            if moves[i-1] == 'R' or moves[i-1] == 'S':    # case the direction refers to cube spin or layer rotation
                servo_angle-=90                           # negative 90deg angle are subtracted from the angle counter
                tot_moves+=1                              # counter is increased

        elif moves[i]=='F':                               # case there is a flip on the move string
            tot_moves+=int(moves[i+1])                    # counter is increased
        
        if servo_angle<-90 or servo_angle>180:            # case the angle counter is out of range
            if print_out:                                 # case the print_out variable is set true
                print(f'servo_angle out of range at string pos:{i}')  # info are printed
            servo_angle_ok=False                          # bolean of results is updated
            break                                         # for loop is interrupted
    
    if servo_angle_ok==True:                              # case the coolean is still positive
        if print_out:                                     # case the print_out variable is set true
            print('servo_angle within range')             # positive result is printed
    
    remaining_moves={}                                            # empty dict to store the left moves 
    left_moves=tot_moves                                          # initial remaining moves are all the moves
    for i in range(len(moves)):                                   # iteration over all the string characters
        if moves[i]=='R' or moves[i]=='S':                        # case the move is cube spin or layer rotation               
            left_moves-=1                                         # counter is decreased by one
            remaining_moves[i]=int(100*(1-left_moves/tot_moves))  # solving percentage associated to the move index key
        elif moves[i]=='F':                                       # case there is a flip on the move string
            left_moves-=int(moves[i+1])                           # counter is decreased by the amount of flips
            remaining_moves[i]=int(100*(1-left_moves/tot_moves))  # solving percentage associated to the move index key   
        
    return servo_angle_ok, tot_moves, remaining_moves






def fun(print_out=s_debug):
    """ Cube holder spins, to make some vittory noise once the cube is solved."""

    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home, b_servo_CW_pos, b_servo_CCW_pos
    
    if print_out:                                    # case the print_out variable is set true
        print("fun function")                        # feedback is printed to the terminal
    
    if t_top_cover != 'open':                        # variable to track the top cover/lifter position
        if not stop_servos:                          # case there is not a stop request for servos
            if b_servo_stopped==True:                # boolean of bottom servo at location the lifter can be operated
                b_servo_operable=False               # variable to block/allow bottom servo operation
                t_servo.value = t_servo_open         # top servo is positioned in open top cover position, from close position
                time.sleep(t_flip_open_time)         # time for the top servo to reach the open top cover position
                t_top_cover='open'                   # variable to track the top cover/lifter position
                b_servo_operable=True                # variable to block/allow bottom servo operation
        
    if b_servo_home==False:                          # case bottom servo is not home
        if not stop_servos:                          # case there is not a stop request for servos
            if b_servo_operable==True:               # variable to block/allow bottom servo operation
                if b_servo_CW_pos==True:             # boolean of bottom servo at full CW position
                    b_servo.value = b_home_from_CW   # bottom servo moves to the extra home position, from CCW
            
                elif b_servo_CCW_pos==True:          # boolean of bottom servo at full CCW position
                    b_servo.value = b_home_from_CCW  # bottom servo moves to the extra home position, from CW
                
                time.sleep(b_spin_time)              # time for the bottom servo to reach the extra home position
                b_servo_home=True                    # boolean bottom servo is home

    
    time.sleep(0.25)                                 # little delay, to timely separate from previous robot movements
    runs=8                                           # number of sections
    b_delta = (b_servo_CW-b_home)/runs               # PWM amplitute per section
    t_delta = 1.3*b_spin_time/runs                   # time amplitude per section
    k=1                                              # coefficient that treats differently the first rotation, as it start from home
    
    for i in range(4,runs):                          # iteration over the sections, starting somehome from the middle
        b_target_CCW=b_home+b_delta*(runs-i)         # PWM target calculation for CCW postion
        delay_time=t_delta*(runs-i)                  # time calculation for the servo movement
        if not stop_servos:                          # case there is not a stop request for servos
            b_servo_stopped=False                    # boolean of bottom servo at location the lifter can be operated
            b_servo.value = b_target_CCW             # bottom servo moves to the target_CCW position
            time.sleep(k*(delay_time+i*0.01))        # time for the bottom servo to reach the target position
            k=2                                      # coefficient to double the time, at each move do not start from home anymore
            b_target_CW=b_home-b_delta*(runs-i)      # PWM target calculation for CW postion
            delay_time=t_delta*(runs-i)              # time calculation for the servo movement
        if not stop_servos:                          # case there is not a stop request for servos
            b_servo_operable=False                   # variable to block/allow bottom servo operation
            b_servo.value = b_target_CW              # bottom servo moves to the target_CW position
            time.sleep(k*(delay_time+i*0.01))        # time for the bottom servo to reach the target position
            b_servo_stopped=True                     # boolean of bottom servo at location the lifter can be operated
    
    if not stop_servos:                              # case there is not a stop request for servos
        b_servo_stopped=False                        # boolean of bottom servo at location the lifter can be operated
        b_servo.value = b_home                       # bottom servo moves to home position
        time.sleep(k*(delay_time+i*0.010))           # time for the bottom servo to reach home position
        b_servo_stopped=True                         # boolean of bottom servo at location the lifter can be operated
        b_servo_home=True                            # boolean bottom servo is home

    stopping_servos(print_out=s_debug)
    
    return True







def servo_solve_cube(moves, scrambling=False, print_out=s_debug, test=False):
    """ Function that translates the received string of moves, into servos sequence activations.
        This is substantially the main function."""
    
    global t_top_cover, b_servo_operable, b_servo_stopped, b_servo_home
    
    start_time=time.time()                         # start time is assigned
    
    # the received string is analyzed if compatible with servo rotation contraints, and amount of movements
    servo_angle_ok, tot_moves, remaining_moves = check_moves(moves, print_out=s_debug)
    
    if not servo_angle_ok:
        print("Error on servo moves algorithm")    # feedback to terminal
        robot_status_='Robot_stopped'              # string variable indicating how the servo_solve_cube function has ended
        robot_time_=(time.time()-start_time)       # robot time is calculated
        return robot_status_, robot_time_          # function returns the cube status and the robot time
        
    if print_out:                                  # case the print_out variable is set true
        print(f'total amount of servo movements: {tot_moves}\n')   # feedback is printed to the terminal   
    
    string_len=len(moves)                          # number of characters in the moves string
    for i in range(string_len):                    # iteration over the characters of the moves string
        if test:                                   # case test is set True (function is called for test by CLI or GUI)
            if stop_btn1.is_pressed or stop_btn2.is_pressed: # case one of the disply buttons is pressed
                stopping_servos()                  # servos are stopped
                break                              # for loop is interrupted
        
        if stop_servos:                            # case there is a stop request for servos
            break                                  # the foor loop in interrupted
        
        if i%2==0 and not stop_servos:             # string index having robot movements
            # calls the display progress bar function. SCRAMBLING is displayed when that fuction is used
            s_disp.display_progress_bar(remaining_moves[i], scrambling)
        
        if moves[i]=='F':                          # case there is a flip on the move string
            flips=int(moves[i+1])                  # number of flips
            if print_out:                          # case the print_out variable is set true
                print(f'To do F{flips}')           # for print_out
            
            for f in range(flips):                 # iterates over the number of requested flips        
                if test:                           # case test is set True (function is called for test by CLI or GUI)
                    if stop_btn1.is_pressed or stop_btn2.is_pressed: # case one of the disply buttons is pressed
                        stopping_servos()          # servos are stopped
                        break                      # for loop is interrupted
                
                if stop_servos:                    # case there is a stop request for servos
                    break                          # the foor loop in interrupted
                
                flip_up()                          # lifter is operated to flip the cube

                if f<(flips-1):                    # case there are further flippings to do
                    flip_to_read()                 # lifter is lowered stopping the top cover in read position (cube not constrained)

                if f==(flips-1) and string_len-(i+2)>0:   # case it's the last flip and there is a following command on the move string
                    if moves[i+2]=='R':            # case the next action is a 1st layer cube rotation
                        flip_to_close()            # top cover is lowered to close position
                    elif moves[i+2]=='S':          # case the next action is a cube spin
                        flip_to_open()             # top cover is lowered to open position 


        elif moves[i]=='S':                        # case there is a cube spin on the move string
            direction=int(moves[i+1])              # rotation direction is retrived
            if print_out:                          # case the print_out variable is set true
                print(f'To do S{direction}')       # for print_out

            if direction==3:                       # case the direction is CCW
                set_dir='CCW'                      # CCW directio is assigned to the variable
            else:                                  # case the direction is CW
                set_dir='CW'                       # CW directio is assigned to the variable
            
            if b_servo_home==True:                 # case bottom servo is at home
                spin_out(set_dir)                  # call to function to spin the full cube to full CW or CCW
            
            else:                                  # case the bottom servo is at full CW or CCW position
                spin_home()                        # call to function to spin the full cube toward home position


        elif moves[i]=='R':                        # case there is a cube 1st layer rotation
            direction=int(moves[i+1])              # rotation direction is retrived   
            if print_out:                          # case the print_out variable is set true
                print(f'To do R{direction}')       # for print_out

            if direction==3:                       # case the direction is CCW
                set_dir='CCW'                      # CCW directio is assigned to the variable
            else:                                  # case the direction is CW
                set_dir='CW'                       # CW directio is assigned to the variable
            
            if b_servo_home==True:                 # case bottom servo is at home
                rotate_out(set_dir)                # call to function to rotate cube 1st layer on the set direction, moving out from home              
            
            elif b_servo_CW_pos==True:             # case the bottom servo is at full CW position
                if set_dir=='CCW':                 # case the set direction is CCW
                    rotate_home(set_dir)           # call to function to spin the full cube toward home position
                
            elif b_servo_CCW_pos==True:            # case the bottom servo is at full CCW position
                if set_dir=='CW':                  # case the set direction is CW
                    rotate_home(set_dir)           # call to function to spin the full cube toward home position
    
    if stop_servos:                                # case there is a stop request for servos 
        if print_out:                              # case the print_out variable is set true
            print("\nRobot stopped")               # feedback is printed to the terminal
        robot_status_='Robot_stopped'              # string variable indicating how the servo_solve_cube function has ended
        stopping_servos(s_debug)                   # call the stop servo function
        
    elif not stop_servos:                          # case there is not a stop request for servos
        robot_status_='Cube_solved'                # string variable indicating how the servo_solve_cube function has ended
        if print_out:                              # case the print_out variable is set true
            if tot_moves!=0:                       # case the robot was supposed to have movements
                print("\nCompleted all the servo movements")  # feedback is printed to the terminal
            else:                                  # case the robot had no movements to perform (i.e. cube already solved)
                print("\nno servo movements needed") #feedback is printed to the terminal

    robot_time_=(time.time()-start_time)           # robot time is calculated
    
    return robot_status_, robot_time_              # function returns the cube status and the robot time



     
     

def set_servos_pos(target):
        """ Function to set both servos to target angle, wherein the target is from -1.00 to 1.00"""
        
        target=round(float(target),2)                                      # target argument is rounded to two decimals
        if target < -1:                                                    # case the received target is smaller than -1
            target = -1.0                                                  # target is set to -1
            print('accepted values are from -1.00 to 1.00: used -1.00')    # feedback is printed to the terminal
        elif target > 1:                                                   # case the received target is bigger than 1
            target = 1.0                                                   # target is set to 1
            print('accepted values are from -1.00 to 1.00: used 1.00')     # feedback is printed to the terminal
        elif target == 0:                                                  # case the received target equals zero
            print('servos to: MID POSITION')                               # feedback is printed to the terminal
        else:                                                              # case the received target is between -1 and 1 included, but not zero
            print('servos to:', target)                                    # feedback is printed to the terminal
        t_servo.value = target                                             # top servo is set to the target
        b_servo.value = target                                             # bottom servo is set to the target







def update_parameters():
    """update the dict with servos parameters when tested/set via --tune argument."""
    
    parameters = {'t_min_pulse_width':t_min_pulse_width, 't_max_pulse_width':t_max_pulse_width,
                  't_servo_close_':t_servo_close, 't_servo_rel_delta_':t_servo_rel,'t_servo_open_':t_servo_open,
                  't_servo_read_':t_servo_read, 't_servo_flip_':t_servo_flip,
                  
                  'b_min_pulse_width':b_min_pulse_width, 'b_max_pulse_width': b_max_pulse_width,
                  'b_home_':b_home, 'b_extra_home_CW_':b_extra_home_CW, 'b_extra_home_CCW_':b_extra_home_CCW,
                  'b_servo_ccw_':b_servo_CCW, 'b_servo_cw_':b_servo_CW,
                  'b_rel_CCW_':b_rel_CCW, 'b_rel_CW_':b_rel_CW}  # dict of (--tune) parameters
    
    return parameters







def print_info():
    # info are printed to terminal on how to use this function
    print('\n Code to check the individual servos positions.')
    print(' It is possible to recall the values stored at the Cubotino_m_servo_settings.txt ,')
    print(' or to manually enter different values (float from -1.000 to 1.000)')
    print('\n Top servo name is t_servo,  Bottom servo name is b_servo.')
    print('\n Top servo positions: t_servo_close, t_servo_open, t_servo_read, t_servo_flip')
    print(' Bottom servo positions: b_home, b_servo_CCW, b_servo_CW')
    print(' When t_servo_close, b_home, b_servo_CW and b_servo_CCW the release rotation is also applied') 
    print('\n Min variation leading to servo movement is (+/-)0.02 or 0.03, depending on the servos.')
    print(' Smaller values lead to servo CCW rotation, by considering the servo point of view !!!')
    print('\n ATTENTION: Check the cube holder is free to rotate BEFORE moving the bottom servo from home.')
    print('\n Example 1: t_servo = t_servo_close --> to recall the top cover close position')
    print(' Example 2: t_servo = 0.04 --> to test value 0.04, different from the default 0')
    print(' Example 3: b_servo = b_servo_CW --> to recall the cube holder CW position')
    print("\n Enter  'init'   to reload the settings from the last saved Cubotino_m_servo_settings.txt")
    print(" Enter  'info'   to get this info printed again to the terminal")
    print(" Enter  'print'  to reload and printout the last saved settings")
    print(" Enter  'test'   to verify the servos tuning with a predefined sequence of movements")
    print(" Enter  'q'      to quit")
    print(" Use arrows to recall previously entered commands, and easy editing")







def test_servos_positions():
    """function to indivially check servo positions, by recalling the settings at json file of by entering the target value """
    
    global b_servo, t_servo, robot_init_status   # global variables being updated by this function
    
    
    print_info()                  # tuning info are printed to the terminal
    init_servo(print_out=s_debug, start_pos='read')     # servos are initialized
    t_servo.value = t_servo_open  # top servo is rotated to open position (as defined at the json file)
    parameters = update_parameters()  # parameters for --tune are updated

    while True:                                         # infinite loop
        ui = input('\n\nEnter command: ')               # user input string is assigned to a variable
        ui = ui.strip()                                 # whitespaces removal
        if ui == "q" or ui == 'Q' or ui == 'exit':      # cases the inputs are for script quitting
            print('Quitting Cubotino_m_servos.py\n\n')  # feedback is printed to terminal
            break                                       # infinite loop is interrupted
        
        elif ui == "info":                              # case the input is 'info'
            try:                                        # tentative
                print ("\033c")                         # clears the terminal
            except:                                     # in case of exeptions
                pass                                    # do nothing
            print_info()                                # tuning info are printed to the terminal
            
        elif ui == "print":                             # case the input is 'print'
            del t_servo                                 # object is deleted, to prevent issue on re-generating it
            del b_servo                                 # object is deleted, to prevent issue on re-generating it
            robot_init_status=False                     # boolean to track the servos inititialization status
            init_servo(print_out=s_debug, start_pos='open')  # servos are initialized, with parameters from the json files
            t_servo.value = t_servo_open                # top servo is rotated to open position (as defined at the json file)
            parameters = update_parameters()            # parameters for --tune are updated
            print('\nRe-loaded Cubotino_m_servo_settings.txt settings')  # feedback is printed to terminal
            print("Last saved values are:\n")           # feedback is printed to terminal
            for parameter, value in parameters.items():    # iteration over the testable parameters via --tune
                print("  {:<20} {:<10}".format(parameter[:-1], value)) # parameters and values are printed
    
        elif ui == "init":                              # case the input is 'init'
            del t_servo                                 # object is deleted, to prevent issue on re-generating it
            del b_servo                                 # object is deleted, to prevent issue on re-generating it
            robot_init_status=False                     # boolean to track the servos inititialization status
            init_servo(print_out=s_debug, start_pos='open')  # servos are initialized, with parameters from the json files
            t_servo.value = t_servo_open                # top servo is rotated to open position (as defined at the json file)
            parameters = update_parameters()            # parameters for --tune are updated
            print('Re-loaded Cubotino_m_servo_settings.txt settings')  # feedback is printed to terminal
        
        elif ui == 'test':
            del t_servo                                 # object is deleted, to prevent issue on re-generating it
            del b_servo                                 # object is deleted, to prevent issue on re-generating it
            robot_init_status=False                     # boolean to track the servos inititialization status
            init_servo(print_out=s_debug, start_pos='read') # servos are initialized, with parameters from the json files
            test_set_of_movements()                     # call to the function that holds the predefined set of movements
        
        else:                                           # case the input is not for quitting nor for 'init'
            valid_command = True                        # command is assumed to be valid
            valid_argument = True                       # argument is assumed to be valid
            
            try:                                                # tentative
                if '=' not in ui or ui[:7] not in ('t_servo','b_servo'):
                    raise ValueError('Command not recognized')
                else:
                    command = ui[:ui.find('=')]                     # user inpute is sliced to retrive the command part
                    command = command.strip().lower()+'.value'      # whitespaces removal and '.value' string addition to the command

                    if command not in ('t_servo.value', 'b_servo.value'):
                        raise TypeError('Command not recognized')
            
            except:                                             # exception
                print('Command not recognized, double check the command sintax')   # feedback is printed to terminal
                valid_command = False                           # command is set False
            
            
            if valid_command:
                try:
                    argument = ui[ui.find('=')+1:]                       # user inpute is sliced to retrive the argument part
                    argument = argument.strip().lower()                  # whitespaces removal from the argument
                    if len(argument) == 0:
                        print('not a valid argument')                    # feedback is printed to terminal
                        raise ValueError('Empty argument')
                    
                except:                                                  # exception
                    valid_argument = False                               # command is set False
                    
            if valid_command:                                            # case the command is valid
                try:
                    if argument in ('t_servo_close', 't_servo_open', 't_servo_read', 't_servo_flip'): # case the argument is present in tuple
                        print('testing top servo, position: ', argument) # feedback is printed to terminal
                        if argument == 't_servo_close':                  # case the argument is 't_servo_close'
                            t_servo.value = t_servo_close                # servo is set to the close position as set on the json file
                            time.sleep(1)                                # wait time to ensure the servo reaches the position, and to allow user reaction
                            t_servo.value = t_servo_rel                  # servo is rotated back by the release parameter
                            
                        else:                                            # case the argument is not 't_servo_close'
                            t_servo.value =  parameters[str(argument)+'_']    # servo is set to the position recalled from the json file
                        print('done')                                    # feedback is printed to terminal
                    
                    elif argument == 'b_home':                           # case the argument is 'b_home'
                        print('testing bottom servo, position: ', argument)  # feedback is printed to terminal
                        if b_servo.value > b_home:                       # case the last servo target was higher than 'b_home
                            b_servo.value = b_home - b_extra_home_CW     # extra rotation to home is applied to the servo
                        elif b_servo.value < b_home:                     # case the last servo target was smaller than 'b_home
                            b_servo.value = b_home + b_extra_home_CCW    # extra rotation to home is applied to the servo
                        time.sleep(1)                                    # wait time to ensure the servo reaches the position, and to allow user reaction
                        b_servo.value = b_home                           # servo is rotated to home
                        print('done')                                    # feedback is printed to terminal   
                        
                    elif argument in ('b_servo_ccw', 'b_servo_cw'):      # case the argument is in tuple
                        print('testing bottom servo, position: ', argument)  # feedback is printed to terminal
                        if argument == 'b_servo_ccw':                    # case the argument is 'b_home_CCW'
                            b_servo.value = b_servo_CCW                  # servo is rotated to CCW
                            time.sleep(2)                                # wait time to ensure the servo reaches the position, and to allow user reaction
                            b_servo.value = b_servo_CCW + brel_CCW       # servo is rotated back by the release parameter
                        elif argument == 'b_servo_cw':                   # case the argument is 'b_home_CW'
                            b_servo.value = b_servo_CW                   # servo is rotated to CW
                            time.sleep(2)                                # wait time to ensure the servo reaches the position, and to allow user reaction
                            b_servo.value = b_servo_CW - b_rel_CW        # servo is rotated back by the release parameter
                        print('done')                                    # feedback is printed to terminal
                        
                    else:                                                # case the argument is not in previous tuples

                        if argument.lstrip('-').replace('.', '', 1).isdigit():
                            arg = round(float(argument),3)               # provided argument is tranformed in tuple, rounded to 3 decimals
                            if arg >= -1 and arg <= 1:                   # case the argument is a float in range -1 to 1
                                if command.strip() == 't_servo.value':       # case the command is 't_servo.value'
                                    print('testing top servo, argument value:', arg)    # feedback is printed to terminal
                                    t_servo.value = arg                      # argument is assigned to the top servo target rotation 
                                    print('done')                            # feedback is printed to terminal
                                elif command.strip() == 'b_servo.value':     # case the command is 'b_servo.value'
                                    print('testing bottom servo, argument value:', arg) # feedback is printed to terminal
                                    b_servo.value = arg                      # argument is assigned to the bottom servo target rotation 
                                    print('done')                            # feedback is printed to terminal
                                else:                                        # case the argument is not a float or not in range -1 to 1
                                    print('Argument not valid')              # feedback is printed to terminal
                                    raise ValueError('Argument not valid')
                            else:
                                print('Argument not valid')
                                raise ValueError('Argument not in range -1 to 1')
                        else:
                            print('Argument not valid')
                            raise ValueError('Argument not valid')
                            
                    
                except:                                                      # exception
                    print('Accepted argument is a float in range -1 to 1')   # feedback is printed to terminal
                    
                            
        time.sleep(0.1)                                              # little wait time in the infinite while loop
    exit()                                                           # script is closed when the infinite loop is interrupted






def test_set_of_movements():
    """ function to verify the servos while solving a predefined robot movement string:
        'F2R1S3R1S3S3F1R1F2R1S3S3F1R1S3R1F3R1S3R1S3S3F3R1S3F1R1S3R1F3R1S3R1S3F3R1S3R1
        F1R3S1F1R3F1S1R3S3F1R1S3R1F3S1R3F1R1S3S3F3R1S3R1F3R1S3R1S3F1S1R3S1F3R3F1R1S3'
        """
    
    global stop_btn1, stop_btn2, robot_init_status
    
    # buttons at the display board, used as stop buttons when servos setting/testing via GUI
    from gpiozero import Button     # library to manage GPIO
 
    try:                            # tentative
        stop_btn1                   # name of stop button 1 
    except NameError:               # case a name error exception is raised
        stop_btn1 = Button(23)      # stop_btn1 object is created
        
    try:                            # tentative
        stop_btn2                   # name of stop button 1 
    except NameError:               # case a name error exception is raised
        stop_btn2 = Button(24)      # stop_btn2 object is created
    
    
    print('\nDemonstration of the robot servos current settings, by solving a predefined scrambled cube')   
    print('Press the buttons at display to interrupt the test')
        
    movements= 'F2R1S3R1S3S3F1R1F2R1S3S3F1R1S3R1F3R1S3R1S3S3F3R1S3F1R1S3R1F3R1S3R1S3F3R1S3R1'
    movements += 'F1R3S1F1R3F1S1R3S3F1R1S3R1F3S1R3F1R1S3S3F3R1S3R1F3R1S3R1S3F1S1R3S1F3R3F1R1S3'
#     CUBOTino micro takes 46.0 secs (04/03/2023) when 'fast' argument, settings as per How_To_Make doc)
#     CUBOTino micro takes 48.4 secs (04/03/2023) when not 'fast' argument, settings as per How_To_Make doc)
#     "t_min_pulse_width": "0.5",
#     "t_max_pulse_width": "2.5",
#     "t_servo_close": "0.12",
#     "t_servo_open": "-0.22",
#     "t_servo_read": "-0.48",
#     "t_servo_flip": "-0.82",
#     "t_servo_rel_delta": "0.0",
#     "t_flip_to_close_time": "0.14",
#     "t_close_to_flip_time": "0.24",
#     "t_flip_open_time": "0.32",
#     "t_open_close_time": "0.1",
#     "t_rel_time": "0.0",
#     "b_min_pulse_width": "0.42",
#     "b_max_pulse_width": "2.6",
#     "b_servo_CCW": "-0.98",
#     "b_servo_CW": "1.0",
#     "b_home": "0.0",
#     "b_rel_CCW": "0.08",
#     "b_rel_CW": "0.08",
#     "b_extra_home_CW": "0.06",
#     "b_extra_home_CCW": "0.08",
#     "b_spin_time": "0.16",
#     "b_rotate_time": "0.26",
#     "b_rel_time": "0.0"
    
    
    s_disp.set_backlight(1)              # activates the display backlight
    s_debug= False  # True               # boolean for s_debug printouts purpose
    robot_init_status = False            # False to prevent servos to be positioned as per robot start

    if init_servo(print_out=s_debug, start_pos='read'):    # servos are initialized
        
        t_ref = time.time()
        screen1=True
        while time.time()-t_ref < 6:
            if screen1:
                s_disp.show_on_display('FIX SET OF', 'MOVEMENTS', fs1=32, y2=75, fs2=28)  # feedback is printed to the display
                screen1=False
                time.sleep(1)
            else:
                txt = '<  STOP'
                s_disp.show_on_display(txt, txt, x1=0, x2=0, y2=85, fs1=34, fs2=34)   # buttons can be used to interrupt the test
                screen1=True
                time.sleep(.8)
        
        
        robot_status, robot_time = servo_solve_cube(movements, print_out=s_debug, test=True) # robot solver is called

        if robot_status == 'Cube_solved':                       # case the robot solver returns Cube_solved in the robot_status
            print(f"Solving time: {round(robot_time,1)} secs")  # print the solving time as feedback
            s_disp.show_on_display('TEST TIME:', str(round(robot_time,1)) + 's', fs1=32, y2=75, fs2=36)  # feedback is printed to the display
            time.sleep(3)                                       # litle delay for display reading
            robot_init_status=False                             # boolean to track the servos inititialization status
            return 'completed'                                  # string 'completed' is returned
            
        elif robot_status == 'Robot_stopped':                   # case the robot solver returns Robot_stopped in the robot_status
            print(f"Robot has been stopped, after {round(robot_time,1)} secs")  # print the status as feedback
            return 'stopped'                                    # string 'stopped' is returned

#     s_disp.set_backlight(0)                # de-activates the display backlight







if __name__ == "__main__":
    """ This main function (without arguments) to test the servos while solving a predefined robot movement string:
        F2R1S3R1S3S3F1R1F2R1S3S3F1R1S3R1F3R1S3R1S3S3F3R1S3F1R1S3R1F3R1S3R1S3F3R1S3R1
        F1R3S1F1R3F1S1R3S3F1R1S3R1F3S1R3F1R1S3S3F3R1S3R1F3R1S3R1S3F1S1R3S1F3R3F1R1S3'
        
        When argument 'set' from the command line, this function allows to easily set the servos the mid position,
        by passing 0 (zero); Other angles can be tested, by passing values from -1 to 1.
        
        When argument is 'tune' from the command line, this function allows to verify the servos positions on
        their default positions (as per json file) or to play with the position entered as target values (from -1 to 1)."""    
    
    
    try:                  # tentative
        print ("\033c")   # clears the terminal
    except:               # in case of exeptions
        pass              # do nothing
    
    
    ##################### setting the servo to mid angle, or to traget, from the CLI  #############
    import argparse
    parser = argparse.ArgumentParser(description='Servo parameter for middle and other positions') # argument parser object creation
    parser.add_argument("--set", type=float, 
                        help="Set both servos to PWM value (value range from -1.00 to 1.00)")      # argument is added to the parser
    parser.add_argument("--tune", action='store_true',
                        help="Check individual servo default positions, to find the best tune")    # argument is added to the parser
    parser.add_argument("--fast", action='store_true',
                        help="From Flip-Up to close in one step instead of two")    # argument is added to the parser
    args = parser.parse_args()                             # argument parsed assignement
    # #############################################################################################
    
    
    #####################  applying the arguments   ###############################################
    if args.fast == True:                # case the Cubotino_m_servo.py has been launched with 'speed' argument
        flip_to_close_one_step = True   # f_to_close steps (steps from flip up to close) is set True (= 1 step)
        
    if args.set != None:                                   # case the Cubotino_m_servo.py has been launched with 'set' argument
        init_servo(print_out=s_debug, start_pos=0)         # servo objectes are created, and set initially to mid position (by default)
        set_servos_pos(args.set)                           # servos are set according to the value in 'set' argument
        while True:                                        # infinite loop, to give the chance to play with the servos angles
            target = input('\nenter a new PWM value from -1.00 to 1.00 (0 for mid position, any letter to escape): ') # input request with proper info
            try:                                           # tentative 
                target = float(target)                     # user input transformed to float
                set_servos_pos(target)                     # servos are set according to the input value
            except:                                        # exception, in case non-numbers entered
                print('\nQuitting Cubotino_m_servos.py\n\n')  # feedback is printed to terminal
                break                                      # while loop is interrupted
    

    elif args.tune == True:               # case the Cubotino_m_servo.py has been launched with 'tune' argument
        import readline                   # library for easier typing at the CLI
        test_servos_positions()           # calls the function to test the individual servos positions
    # #############################################################################################
         
        
           
    
    ###############  testing the servos as a predefined solving process ###########################
    else:     # case the Cubotino_m_servos.py has been launched without 'set' or 'tune' arguments
        test_set_of_movements()   # call to the function that holds the predefined set of movements
        pass
        
        

