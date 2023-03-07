#!/usr/bin/env python
# coding: utf-8

"""
######################################################################################################################
# Andrea Favero 07 March 2023
# 
# GUI helping tuninig CUBOTino servos positions.
# This script relates to CUBOTino micro, an extremely small and simple Rubik's cube solver robot 3D printed
# CUBOTino micro is the smallest version of the CUBOTino versions
#
######################################################################################################################
"""



# ################################## Imports  ########################################################################

# python libraries, normally distributed with python
import tkinter as tk                 # GUI library
from tkinter import ttk              # GUI library
import datetime as dt                # date and time library used as timestamp on a few situations (i.e. data log)
import time                          # import time library  
import glob, os.path, pathlib         # os is imported to ensure the file presence, check/make
import json                          # libraries needed for the json, and parameter import
from getmac import get_mac_address   # library to get the device MAC ddress

# project specific libraries  
import Cubotino_m_servos as servo    # custom library controlling Cubotino servos and led module
from Cubotino_m_display import display as disp   # custom library controlling Cubotino disply module
######################################################################################################################




# #################### functions to manage the GUI closing ###########################################################
def on_closing():
    disp.show_cubotino()
    root.destroy()
######################################################################################################################
    
    
    

# #################### functions to manage settings from/to files   ##################################################
def read_settings_file(fname=''):
    """ Function to assign the servo settings to a dictionary, after testing their data type."""   
    
    import os.path, pathlib, json                                    # libraries needed for the json, and parameter import
    # convenient choice for Andrea Favero, to upload the settings fitting his robot based on mac address check                
    from getmac import get_mac_address                               # library to get the device MAC ddress
    
    if len(fname) == 0:                                              # case fname equals empty string
        folder = pathlib.Path().resolve()                            # active folder (should be home/pi/cube)  
        eth_mac = get_mac_address()                                  # mac address is retrieved
        if eth_mac == AF_mac:                                        # case the script is running on AF (Andrea Favero) robot
            fname = os.path.join(folder,'Cubotino_m_servo_settings_AF.txt')   # AF robot settings (optimized settings for AF bot)
        else:                                                        # case the script is not running on AF (Andrea Favero) robot
            fname = os.path.join(folder,'Cubotino_m_servo_settings.txt') # folder and file name for the settings, to be tuned
    
    settings = {}
    if os.path.exists(fname):                                        # case the servo_settings file exists
        with open(fname, "r") as f:                                  # servo_settings file is opened in reading mode
            servo_settings = json.load(f)                            # json file is parsed to a local dict variable
        
        try:           
            # dict with all the servos settings from the txt file
            # from the dict obtained via json.load the settings dict adds individual data type check
            settings['t_min_pulse_width'] = float(servo_settings['t_min_pulse_width'])   # defines the min Pulse With the top servo reacts to
            settings['t_max_pulse_width'] = float(servo_settings['t_max_pulse_width'])   # defines the max Pulse With the top servo reacts to
            settings['t_servo_close'] = float(servo_settings['t_servo_close'])           # Top_cover close position, in gpiozero format
            settings['t_servo_open'] = float(servo_settings['t_servo_open'])             # Top_cover open position, in gpiozero format
            settings['t_servo_read'] = float(servo_settings['t_servo_read'])             # Top_cover camera read position, in gpiozero format
            settings['t_servo_flip'] = float(servo_settings['t_servo_flip'])             # Top_cover flip position, in gpiozero format
            settings['t_servo_rel_delta'] = float(servo_settings['t_servo_rel_delta'])   # Top_cover release angle movement from the close position to release tension
            settings['t_flip_to_close_time'] = float(servo_settings['t_flip_to_close_time'])  # time for Top_cover from flip to close position
            settings['t_close_to_flip_time'] = float(servo_settings['t_close_to_flip_time'])  # time for Top_cover from close to flip position 
            settings['t_flip_open_time'] = float(servo_settings['t_flip_open_time'])     # time for Top_cover from open to flip position, and viceversa
            settings['t_open_close_time'] = float(servo_settings['t_open_close_time'])   # time for Top_cover from open to close position, and viceversa
            settings['t_rel_time'] = float(servo_settings['t_rel_time'])                 # time for Top_cover to release tension from close position
    
            settings['b_min_pulse_width'] = float(servo_settings['b_min_pulse_width'])   # defines the min Pulse With the bottom servo reacts to
            settings['b_max_pulse_width'] = float(servo_settings['b_max_pulse_width'])   # defines the max Pulse With the bottom servo reacts to
            settings['b_servo_CCW'] = float(servo_settings['b_servo_CCW'])               # Cube_holder max CCW angle position
            settings['b_servo_CW'] = float(servo_settings['b_servo_CW'])                 # Cube_holder max CW angle position
            settings['b_home'] = float(servo_settings['b_home'])                         # Cube_holder home angle position
            settings['b_rel_CCW'] = float(servo_settings['b_rel_CCW'])                   # Cube_holder release angle at CCW angle positions, to release tension
            settings['b_rel_CW'] = float(servo_settings['b_rel_CW'])                     # Cube_holder release angle at CW angle positions, to release tension
            settings['b_extra_home_CW'] = float(servo_settings['b_extra_home_CW'])       # Cube_holder release angle from CW to home positions to release tension
            settings['b_extra_home_CCW'] = float(servo_settings['b_extra_home_CCW'])     # Cube_holder release angle from CCW to home positions to release tension
            settings['b_spin_time'] = float(servo_settings['b_spin_time'])               # time for Cube_holder to spin 90 deg (cune not contrained)
            settings['b_rotate_time'] = float(servo_settings['b_rotate_time'])           # time for Cube_holder to rotate 90 deg (cube constrained)
            settings['b_rel_time'] = float(servo_settings['b_rel_time'])                 # time for Cube_holder to release tension at home, CCW and CW positions
            
            return(settings)
            
        except:   # exception will be raised if json keys differs, or parameters cannot be converted to float
            print('error on converting to proper format the imported parameters')   # feedback is printed to the terminal                                  
            return settings                                        # return (empty) settings
    
    else:                                                          # case the servo_settings file does not exists, or name differs
        print('could not find Cubotino_m_servo_settings.txt')      # feedback is printed to the terminal                                  
        return settings                                            # return settingsf








def upload_settings(settings):
    """ Function to assign the servo settings from the dictionary to individual global variables.""" 
    
    global t_min_pulse_width, t_max_pulse_width, t_servo_close, t_servo_open
    global t_servo_read, t_servo_flip, t_servo_rel_delta
    global t_flip_to_close_time, t_close_to_flip_time, t_flip_open_time, t_open_close_time, t_rel_time
    
    global b_min_pulse_width, b_max_pulse_width, b_servo_CCW, b_servo_CW, b_home
    global b_rel_CCW, b_rel_CW, b_extra_home_CW, b_extra_home_CCW
    global b_spin_time, b_rotate_time, b_rel_time

    t_min_pulse_width = robot_settings['t_min_pulse_width']        # defines the min Pulse With the top servo reacts to
    t_max_pulse_width = robot_settings['t_max_pulse_width']        # defines the max Pulse With the top servo reacts to
    t_servo_close = robot_settings['t_servo_close']                # Top_cover close position, in gpiozero format
    t_servo_open = robot_settings['t_servo_open']                  # Top_cover open position, in gpiozero format
    t_servo_read = robot_settings['t_servo_read']                  # Top_cover camera read position, in gpiozero format
    t_servo_flip = robot_settings['t_servo_flip']                  # Top_cover flip position, in gpiozero format
    t_servo_rel_delta = robot_settings['t_servo_rel_delta']        # Top_cover release angle movement from the close position to release tension
    t_flip_to_close_time = robot_settings['t_flip_to_close_time']  # time for Top_cover from flip to close position
    t_close_to_flip_time = robot_settings['t_close_to_flip_time']  # time for Top_cover from close to flip position 
    t_flip_open_time = robot_settings['t_flip_open_time']          # time for Top_cover from open to flip position, and viceversa  
    t_open_close_time = robot_settings['t_open_close_time']        # time for Top_cover from open to close position, and viceversa
    t_rel_time = robot_settings['t_rel_time']                      # time for Top_cover to release tension from close position

    b_min_pulse_width = robot_settings['b_min_pulse_width']        # defines the min Pulse With the bottom servo reacts to
    b_max_pulse_width = robot_settings['b_max_pulse_width']        # defines the max Pulse With the bottom servo reacts to
    b_servo_CCW = robot_settings['b_servo_CCW']                    # Cube_holder max CCW angle position
    b_servo_CW = robot_settings['b_servo_CW']                      # Cube_holder max CW angle position
    b_home = robot_settings['b_home']                              # Cube_holder home angle position
    b_rel_CCW = robot_settings['b_rel_CCW']                        # Cube_holder release angle from CCW angle positions, to release tension
    b_rel_CW = robot_settings['b_rel_CW']                          # Cube_holder release angle from CW angle positions, to release tension
    b_extra_home_CW = robot_settings['b_extra_home_CW']            # Cube_holder release angle from home angle positions, to release tension
    b_extra_home_CCW = robot_settings['b_extra_home_CCW']          # Cube_holder release angle from home angle positions, to release tension
    b_spin_time = robot_settings['b_spin_time']                    # time for Cube_holder to spin 90 deg (cune not contrained)
    b_rotate_time = robot_settings['b_rotate_time']                # time for Cube_holder to rotate 90 deg (cube constrained)
    b_rel_time = robot_settings['b_rel_time']                      # time for Cube_holder to release tension at home, CCW and CW positions







def update_settings_dict():
    """ Function to update the servo settings dictionary based on the global variables.""" 
    
    robot_settings['t_min_pulse_width'] = t_min_pulse_width        # defines the min Pulse With the top servo reacts to
    robot_settings['t_max_pulse_width'] = t_max_pulse_width        # defines the max Pulse With the top servo reacts to
    robot_settings['t_servo_close'] = t_servo_close                # Top_cover close position, in gpiozero format
    robot_settings['t_servo_open'] = t_servo_open                  # Top_cover open position, in gpiozero format
    robot_settings['t_servo_read'] = t_servo_read                  # Top_cover camera read position, in gpiozero format
    robot_settings['t_servo_flip'] = t_servo_flip                  # Top_cover flip position, in gpiozero format
    robot_settings['t_servo_rel_delta'] = t_servo_rel_delta        # Top_cover release angle movement from the close position to release tension
    robot_settings['t_flip_to_close_time'] = t_flip_to_close_time  # time for Top_cover from flip to close position
    robot_settings['t_close_to_flip_time'] = t_close_to_flip_time  # time for Top_cover from close to flip position 
    robot_settings['t_flip_open_time'] = t_flip_open_time          # time for Top_cover from open to flip position, and viceversa  
    robot_settings['t_open_close_time'] = t_open_close_time        # time for Top_cover from open to close position, and viceversa
    robot_settings['t_rel_time'] = t_rel_time                      # time for Top_cover to release tension from close to close position
    
    robot_settings['b_min_pulse_width'] = b_min_pulse_width        # defines the min Pulse With the bottom servo reacts to
    robot_settings['b_max_pulse_width'] = b_max_pulse_width        # defines the max Pulse With the bottom servo reacts to
    robot_settings['b_servo_CCW'] = b_servo_CCW                    # Cube_holder max CCW angle position
    robot_settings['b_servo_CW'] = b_servo_CW                      # Cube_holder max CW angle position
    robot_settings['b_home'] = b_home                              # Cube_holder home angle position
    robot_settings['b_rel_CCW'] = b_rel_CCW                        # Cube_holder release angle from CCW angle positions, to release tension
    robot_settings['b_rel_CW'] = b_rel_CW                          # Cube_holder release angle from CW angle positions, to release tension
    robot_settings['b_extra_home_CW'] = b_extra_home_CW            # Cube_holder release angle from home angle positions, to release tension
    robot_settings['b_extra_home_CCW'] = b_extra_home_CCW          # Cube_holder release angle from home angle positions, to release tension
    robot_settings['b_spin_time'] = b_spin_time                    # time for Cube_holder to spin 90 deg (cune not contrained)
    robot_settings['b_rotate_time'] = b_rotate_time                # time for Cube_holder to rotate 90 deg (cube constrained)
    robot_settings['b_rel_time'] = b_rel_time                      # time for Cube_holder to release tension at home, CCW and CW positions
    
    return robot_settings






def load_previous_settings():
    """ Function load the servo settings from latest json backup file saved.""" 
    
    global robot_settings
    
    folder = pathlib.Path().resolve()                          # active folder (should be home/pi/cube)  
    eth_mac = get_mac_address()                                # mac address is retrieved
    if eth_mac == AF_mac:                                      # case the script is running on AF (Andrea Favero) robot
        fname = os.path.join(folder,'Cubotino_m_servo_settings_AF.txt')   # AF robot settings (optimized settings for AF bot)
    else:                                                      # case the script is not running on AF (Andrea Favero) robot
        fname = os.path.join(folder,'Cubotino_m_servo_settings.txt')   # folder and file name for the settings, to be tuned
    
    backup_fname = fname[:-4] + '_backup*.txt'
    backup_files = sorted(glob.iglob(backup_fname), key=os.path.getmtime, reverse=True) # ordered list of backuped settings files 
    if len(backup_files) > 0:                                  # case there are backup setting files
        if len(backup_files) > 10:                             # case there are more than 10 backup files
            while len(backup_files) > 10:                      # iteration until there will only be 10 backup files
                os.remove(backup_files[-1])                    # the oldes backup file is deleted
                backup_files = sorted(glob.iglob(backup_fname), key=os.path.getctime, reverse=True) # ordered list of backuped settings files     
        latest_backup = backup_files[0]                        # latest settings files backed up
        robot_settings = read_settings_file(latest_backup)     # settings are read from the latest_backup file
        print(f"Uploaded settings from latest_backup:  {latest_backup}")  # feedback is printed to the terminal
    else:                                                      # case there are backup setting files
        robot_settings = read_settings_file(fname)             # settings are read from the fname file
        print(f"Not found backup files, uploaded settings from file: {fname}")
    
    upload_settings(robot_settings)                            # settings are uploaded (to global variables)
    update_sliders()                                           # sliders are updated
    
    
    
    
    
    
def save_new_settings():
    """ Function to write the servo settings dictionary to json file.
        Before overwriting the file, a backup copy is made.""" 
    global robot_settings
    
    folder = pathlib.Path().resolve()                              # active folder (should be home/pi/cube)  
    eth_mac = get_mac_address()                                    # mac address is retrieved
    if eth_mac == AF_mac:                                          # case the script is running on AF (Andrea Favero) robot
        fname = os.path.join(folder,'Cubotino_m_servo_settings_AF.txt')   # AF robot settings (optimized settings for AF bot)
    else:                                                          # case the script is not running on AF (Andrea Favero) robot
        fname = os.path.join(folder,'Cubotino_m_servo_settings.txt') # folder and file name for the settings, to be tuned
    
    if os.path.exists(fname):                                      # case the servo_settings file exists
        
        datetime = dt.datetime.now().strftime('%Y%m%d_%H%M%S')     # date_time variable is assigned, for file name
        backup_fname = fname[:-4] + '_backup_' + datetime + '.txt' # backup file name
        with open(backup_fname, "w") as f:                         # original servo_settings are saved to a backup file with datetime ref
            f.write(json.dumps(robot_settings, indent=0))          # content of the setting file is saved
            print("saving previous settings to backup file:", backup_fname)
        
        backup_fname = fname[:-4] + '_backup*.txt'                 # common name prefix for the backup files
        backup_files = sorted(glob.iglob(backup_fname), key=os.path.getmtime, reverse=True) # ordered list of backuped settings files 
        if len(backup_files) > 10:                                 # case there are more than 10 backup files
            while len(backup_files) > 10:                          # iteration until there will only be 10 backup files
                os.remove(backup_files[-1])                        # the oldes backup file is deleted
                backup_files = sorted(glob.iglob(backup_fname), key=os.path.getctime, reverse=True) # ordered list of backuped settings files 
        
        robot_settings = update_settings_dict()                    # settings updated to sliders values
        with open(fname, "w") as f:                                # servo_settings file is opened in reading mode
            f.write(json.dumps(robot_settings, indent=0))          # content of the setting file is saved
            print("saving settings to:", fname)
    else:                                                          # case the servo_settings file exists
        print("fname does not exists at save_new_settings function")








def update_sliders():
    """function to update the sliders according to the (global) variable."""
    
    # t_min_pulse_width
    # t_max_pulse_width
    s_top_srv_close.set(t_servo_close)
    s_top_srv_rel_delta.set(t_servo_rel_delta)
    s_top_srv_open.set(t_servo_open)
    s_top_srv_read.set(t_servo_read)
    s_top_srv_flip.set(t_servo_flip)
    s_top_srv_flip_to_close_time.set(t_flip_to_close_time)
    s_top_srv_close_to_flip_time.set(t_close_to_flip_time)
    s_top_srv_flip_open_time.set(t_flip_open_time)
    s_top_srv_open_close_time.set(t_open_close_time)
    s_top_srv_rel_time.set(t_rel_time)
    
    s_btn_srv_min_pulse.set(b_min_pulse_width)
    s_btn_srv_max_pulse.set(b_max_pulse_width)
    s_btn_srv_CCW.set(b_servo_CCW)
    s_btn_srv_home.set(b_home)
    s_btn_srv_CW.set(b_servo_CW)
    s_btn_srv_rel_CCW.set(b_rel_CCW)
    s_btn_srv_rel_CW.set(b_rel_CW)
    s_extra_home_CW.set(b_extra_home_CW)
    s_extra_home_CCW.set(b_extra_home_CCW)
    s_btn_srv_spin_time.set(b_spin_time)
    s_btn_srv_rotate_time.set(b_rotate_time)
    s_btn_srv_rel_time.set(b_rel_time)

######################################################################################################################







# ################################### functions to get the slider values  ############################################
def servo_close(val):
    global t_servo_close, t_servo_rel_delta, t_servo_pos
    t_servo_close = round(float(s_top_srv_close.get()),3)        # top servo pos to constrain the top cover on cube mid and top layer
    t_servo_rel = round(t_servo_close - float(s_top_srv_rel_delta.get()),3)
    disp.show_on_display('t_srv CLOSE', str(t_servo_close), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('top', t_servo_close)  # top servo is positioned to the slider value
    time.sleep(t_open_close_time)
    servo.servo_to_pos('top', t_servo_rel)    # top servo is positioned to the slider value
    time.sleep(t_rel_time)
    disp.show_on_display('t_srv CLOSE', f'{t_servo_close} ({t_servo_rel})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    t_servo_pos = 'close'                     # string variable to track the last top_cover position
    btm_srv_widgets_status()                  # updates the bottom servo related widgests status


def servo_release(val):
    global t_servo_rel_delta, t_servo_pos
    t_servo_rel_delta = round(float(s_top_srv_rel_delta.get()),3)  # top servo release position after closing toward the cube
    disp.show_on_display('t_srv RELEASE', f'({t_servo_rel_delta})', fs1=25, y2=75, fs2=30)  # feedback is printed to the display
    t_servo_pos = 'close'                     # string variable to track the last top_cover position
    btm_srv_widgets_status()                  # updates the bottom servo related widgests status


def servo_open(val):
    global t_servo_open, t_servo_pos
    t_servo_open = round(float(s_top_srv_open.get()),3)  # top servo pos to free up the top cover from the cube
    disp.show_on_display('t_srv OPEN', str(t_servo_open), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('top', t_servo_open)   # top servo is positioned to the slider value
    t_servo_pos = 'open'                      # string variable to track the last top_cover position
    btm_srv_widgets_status()                  # updates the bottom servo related widgests status
    

def servo_read(val):
    global t_servo_read, t_servo_pos
    t_servo_read = round(float(s_top_srv_read.get()),3)  # top servo pos for camera reading
    disp.show_on_display('t_srv READ', str(t_servo_read), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('top', t_servo_read)   # top servo is positioned to the slider value
    t_servo_pos = 'read'                      # string variable to track the last top_cover position
    btm_srv_widgets_status()                  # updates the bottom servo related widgests status


def servo_flip(val):
    global t_servo_flip, t_servo_pos
    t_servo_flip = round(float(s_top_srv_flip.get()),3)  # top servo pos to flip the cube on one of its horizontal axis
    disp.show_on_display('t_srv FLIP', str(t_servo_flip), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('top', t_servo_flip)   # top servo is positioned to the slider value
    t_servo_pos = 'flip'                      # string variable to track the last top_cover position
    btm_srv_widgets_status()                  # updates the bottom servo related widgests status
    
    
def flip_to_close_time(val):
    global t_flip_to_close_time
    t_flip_to_close_time = round(float(s_top_srv_flip_to_close_time.get()),3)  # time to lower the cover/flipper from flip to close position


def servo_rel_close(val):
    global t_rel_time
    t_rel_time = round(float(s_top_srv_rel_time.get()),3)   # time to release tension at top_cover close position

    
def close_to_flip_time(val):
    global t_close_to_flip_time
    t_close_to_flip_time = round(float(s_top_srv_close_to_flip_time.get()),3)  # time to raise the cover/flipper from close to flip position


def flip_open_time(val):
    global t_flip_open_time
    t_flip_open_time = round(float(s_top_srv_flip_open_time.get()),3)    # time to raise/lower the flipper between open and flip positions


def open_close_time(val):
    global t_open_close_time
    t_open_close_time = round(float(s_top_srv_open_close_time.get()),3)  # time to raise/lower the flipper between open and close positions


def last_btn_srv_pos():
    global b_servo_pos
    
    if b_servo_pos == 'CCW':
        return b_servo_CCW
    elif b_servo_pos == 'CW':
        return b_servo_CW
    else:
        return b_home
    
    
def btn_srv_min_pulse(val):
    global b_min_pulse_width, b_servo_pos
    b_min_pulse_width = round(float(s_btn_srv_min_pulse.get()),3)  # bottom servo min pulse width
    disp.show_on_display('b_srv MIN PLS', str(b_min_pulse_width), fs1=26, y2=75, fs2=30)  # feedback is printed to the display
    pos = last_btn_srv_pos()
    servo.b_servo_create(b_min_pulse_width, b_max_pulse_width, pos)


def btn_srv_max_pulse(val):
    global b_max_pulse_width, b_servo_pos
    b_max_pulse_width = round(float(s_btn_srv_max_pulse.get()),3)  # bottom servo max pulse width
    disp.show_on_display('b_srv MAX PLS', str(b_max_pulse_width), fs1=26, y2=75, fs2=30)  # feedback is printed to the display
    pos = last_btn_srv_pos()
    servo.b_servo_create(b_min_pulse_width, b_max_pulse_width, pos)


def servo_CCW(val):
    global b_servo_CCW, b_servo_pos
    if t_servo_pos in ('close', 'open'):
        b_servo_CCW = round(float(s_btn_srv_CCW.get()),3)    # bottom servo position when fully CCW
        disp.show_on_display('b_srv CCW', str(b_servo_CCW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        servo.servo_to_pos('bottom', b_servo_CCW)            # bottom servo is positioned to the slider value
        b_servo_pos = 'CCW'                                  # string variable to track the last holder position
    else:
        disp.show_on_display('t_srv', 'BLOCKING', fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    

def servo_home(val):
    global b_home, b_servo_pos
    if t_servo_pos in ('close', 'open'):
        b_home = round(float(s_btn_srv_home.get()),3)        # bottom servo home position
        disp.show_on_display('b_srv HOME', str(b_home), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        servo.servo_to_pos('bottom', b_home)                 # bottom servo is positioned to the slider value
        b_servo_pos = 'home'                                 # string variable to track the last holder position
    else:
        disp.show_on_display('t_srv', 'BLOCKING', fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def servo_CW(val):
    global b_servo_CW, b_servo_pos
    if t_servo_pos in ('close', 'open'):
        b_servo_CW = round(float(s_btn_srv_CW.get()),3)      # bottom servo position when fully CW
        disp.show_on_display('b_srv CW', str(b_servo_CW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        servo.servo_to_pos('bottom', b_servo_CW)             # bottom servo is positioned to the slider value
        b_servo_pos = 'CW'                                   # string variable to track the last holder position
    else:
        disp.show_on_display('t_srv', 'BLOCKING', fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def servo_rel_CCW(val):
    global b_rel_CCW
    b_rel_CCW = round(float(s_btn_srv_rel_CCW.get()),3)  # bottom servo position small rotation back from CCW, to release tension
    disp.show_on_display('b_rel_CCW', str(b_rel_CCW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def servo_rel_CW(val):
    global b_rel_CW
    b_rel_CW = round(float(s_btn_srv_rel_CW.get()),3)  # bottom servo position small rotation back from CW, to release tension
    disp.show_on_display('b_rel_CW', str(b_rel_CW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def servo_extra_home_CW(val):
    global b_extra_home_CW, b_servo_pos
    b_extra_home_CW = round(float(s_extra_home_CW.get()),3)    # bottom servo position extra rotation at home, to release tension
    disp.show_on_display('b_extra CW', str(b_extra_home_CW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('bottom', b_extra_home_CW)              # bottom servo is positioned to the slider value
    b_servo_pos = 'CW'                                         # string variable to track the last holder position


def servo_extra_home_CCW(val):
    global b_extra_home_CCW, b_servo_pos
    b_extra_home_CCW = round(float(s_extra_home_CCW.get()),3)  # bottom servo position extra rotation at home, to release tension
    disp.show_on_display('b_extra CCW', str(b_extra_home_CCW), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    servo.servo_to_pos('bottom', b_extra_home_CCW)             # bottom servo is positioned to the slider value
    b_servo_pos = 'CW'                                         # string variable to track the last holder position


def servo_rotate_time(val):
    global b_rotate_time
    b_rotate_time = round(float(s_btn_srv_rotate_time.get()),3)  # time needed to the bottom servo to rotate about 90deg

def servo_rel_time(val):
    global b_rel_time
    b_rel_time = round(float(s_btn_srv_rel_time.get()),3)      # time to rotate slightly back, to release tensions

def servo_spin_time(val):
    global b_spin_time
    b_spin_time = round(float(s_btn_srv_spin_time.get()),3)  # time needed to the bottom servo to spin about 90deg

######################################################################################################################







# ################################### functions to test the settings #################################################
def servo_init():
    """servo initialization."""
    global t_servo_pos, b_servo_pos
    
    servo_init=servo.servo_tune_via_gui(debug=False, start_pos = 'open')  # servos are initialized, and set to their starting positions
    if servo_init:                           # case the servo init has successed
        t_servo_pos = 'open'               # string variable to track the last top_cover position
        b_servo_pos = 'home'               # string variable to track the last holder position
#         btm_srv_widgets_status()


def close_top_cover():
    global t_servo_pos
    servo.stop_release()                                        # servos are made activate in case aren't
    if b_servo_pos in ('CCW', 'home', 'CW'):                    # case the holder allows the Lifter to be moved freely
        disp.show_on_display('t_srv CLOSE', str(t_servo_close), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        
        # send the close_cover settings request to the robot
        t_servo_pos = servo.close_cover(t_servo_close, t_servo_rel_delta, t_open_close_time, t_rel_time, test=True)
        disp.show_on_display('t_srv CLOSE', f'{t_servo_close} ({t_servo_rel_delta})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        btm_srv_widgets_status()


def open_top_cover():
    global t_servo_pos
    servo.stop_release()                                        # servos are made activate in case aren't
    if b_servo_pos in ('CCW', 'home', 'CW') and t_servo_pos != 'open':  # case the holder allows the Lifter to be moved freely
        t_servo_pos = servo.open_cover(t_servo_open, test=True) # send the open_cover settings request to the robot
        disp.show_on_display('t_srv OPEN', str(t_servo_open), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        btm_srv_widgets_status()
        


def read_position():
    global t_servo_read, t_servo_pos
    servo.stop_release()                                        # servos are made activate in case aren't
    if b_servo_pos in ('CCW', 'home', 'CW') and t_servo_pos != 'read':  # case the holder allows the Lifter to be moved freely
        t_servo_pos = servo.servo_to_pos('top', t_servo_read)   # send the request of top_cover to read position 
        disp.show_on_display('t_srv READ', str(t_servo_read), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        btm_srv_widgets_status()


def flip_cube():
    global t_servo_pos
    servo.stop_release()                                        # servos are made activate in case aren't
    if b_servo_pos in ('CCW', 'home', 'CW'):                    # case the holder allows the Lifter to be moved freely
        t_servo_pos = servo.flip_toggle(t_servo_pos, t_servo_read, t_servo_flip)      # send the flip_test request to the robot
        if t_servo_pos == 'flip':                               # case the top_cover is in flip position
            disp.show_on_display('t_srv FLIP', str(t_servo_flip), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        if t_servo_pos == 'read':                               # case the top_cover is in read position
            disp.show_on_display('t_srv READ', str(t_servo_read), fs1=30, y2=75, fs2=30)  # feedback is printed to the display
        btm_srv_widgets_status()


def ccw():
    global b_servo_pos
    servo.stop_release()                                              # servos are made activate in case aren't
    
    if t_servo_pos == 'open':
        timer1 = b_spin_time
        if b_servo_pos == 'CW':
            timer1+=timer1
        if t_servo_pos in ('close', 'open') and b_servo_pos != 'CCW': # case the top_cover allows the holder to move freely
            target = round(b_servo_CCW + b_rel_CCW,3)
            b_servo_pos = servo.spin_out('CCW', target, 0, timer1, test=True ) # send the spin/rotate to CCW request to the robot
            disp.show_on_display('b_srv CCW', f'({target})' , fs1=30, y2=75, fs2=30)  # feedback is printed to the display
    elif t_servo_pos == 'close':
        timer1 = b_rotate_time
        if b_servo_pos == 'CW':
            timer1+=timer1
        if t_servo_pos in ('close', 'open') and b_servo_pos != 'CCW': # case the top_cover allows the holder to move freely
            b_servo_pos = servo.spin_out('CCW', b_servo_CCW, b_rel_CCW, timer1, test=True ) # send the spin/rotate to CCW request to the robot
            disp.show_on_display('b_srv CCW', f'{b_servo_CCW} ({round(b_servo_CCW+b_rel_CCW,3)})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display

    
def home():
    global b_servo_pos
    
    if t_servo_pos in ('close', 'open') and b_servo_pos != 'home': # case the top_cover allows the holder to move freely
        servo.stop_release()                                       # servos are made activate in case aren't
        if t_servo_pos == 'open':
            timer1 = b_spin_time
            if b_servo_pos == 'CCW':
                b_servo_pos = servo.rotate_home('CW', b_home, 0, timer1, test=True)    # send the spin/rotate to HOME request to the robot
                disp.show_on_display('t_srv HOME', str(b_home), fs1=30, y2=75, fs2=30) # feedback is printed to the display
            elif b_servo_pos == 'CW':
                b_servo_pos = servo.rotate_home('CCW', b_home, 0, timer1, test=True)   # send the spin/rotate to HOME request to the robot
                disp.show_on_display('t_srv HOME', str(b_home), fs1=30, y2=75, fs2=30) # feedback is printed to the display
    
        elif t_servo_pos == 'close':
            timer1 = b_rotate_time
            if b_servo_pos == 'CCW':
                b_servo_pos = servo.rotate_home('CW', b_home, b_extra_home_CCW, timer1, test=True)  # send the spin/rotate to HOME request to the robot
                disp.show_on_display('t_srv HOME', f'{round(b_home+b_extra_home_CCW,3)} ({b_home})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display
            elif b_servo_pos == 'CW':
                b_servo_pos = servo.rotate_home('CCW', b_home, b_extra_home_CW, timer1, test=True)  # send the spin/rotate to HOME request to the robot
                disp.show_on_display('t_srv HOME', f'{round(b_home-b_extra_home_CW,3)} ({b_home})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def cw():
    global b_servo_pos
    
    if t_servo_pos in ('close', 'open') and b_servo_pos != 'CW':   # case the top_cover allows the holder to move freely
        servo.stop_release()                                       # servos are made activate in case aren't
        if t_servo_pos == 'open':
            timer1 = b_spin_time
            if b_servo_pos == 'CCW':
                timer1+=timer1
            target = round(b_servo_CW - b_rel_CW, 3)
            b_servo_pos = servo.spin_out('CW', target, 0, timer1, test=True) # send the spin/rotate to CW request to the robot
            disp.show_on_display('b_srv CCW', f'({target})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display    
        elif t_servo_pos == 'close':
            timer1 = b_rotate_time
            if b_servo_pos == 'CCW':
                timer1+=timer1
            b_servo_pos = servo.spin_out('CW', b_servo_CW, b_rel_CW, timer1, test=True) # send the spin/rotate to CW request to the robot
            disp.show_on_display('b_srv CCW', f'{b_servo_CW} ({round(b_servo_CW-b_rel_CW,3)})', fs1=30, y2=75, fs2=30)  # feedback is printed to the display


def test():
    """call a fix sequence of robot movement that mimic a complete solving cycle.
        """
    
    for label in (top_srv_label, btn_srv_label, test_label, large_test_label, files_label): # iterations throught the labels in tuple
        disable_widgets(label, relief="sunken")  # widgets are disabled
    root.update()                                # forced a graphic update, upfront a long lasting function
    
    servo.stop_release()                         # servos are made activate in case aren't
    read_position()                              # top_servo positioned to read_position, as meant to be the start position after scanning
    servo.test_set_of_movements()                # function to verify the servos while solving a predefined robot movement string 
    
    for label in (top_srv_label, btn_srv_label): # iterations throught the labels (of sliders) in tuple
        enable_widgets(label, relief="raised")   # widgets are enabled
    
    for label in (test_label, large_test_label, files_label):  # iterations throught the labels (of buttons) in tuple
        enable_widgets(label, relief="raised")   # widgets are enabled





def btm_srv_widgets_status():
    """function to enable/disable the bottom servo related widgets according to the top_servo (lifter) position."""
    global t_servo_pos
    
    if t_servo_pos == 'close' or t_servo_pos == 'open':  # case the lifter prevents the holder rotation 
        ccw_btn["relief"] = "raised"            # button is set back raised
        ccw_btn["state"] = "normal"             # button is set back normal
        home_btn["relief"] = "raised"           # button is set back raised
        home_btn["state"] = "normal"            # button is set back normal
        cw_btn["relief"] = "raised"             # button is set back raised
        cw_btn["state"] = "normal"              # button is set back normal
        
        enable_widgets(btn_srv_label, relief="raised")
    
    
    else:                                       # case the lifter is not blocking the holder rotation
        ccw_btn["relief"] = "sunken"            # button is set sunken
        ccw_btn["state"] = "disabled"           # button is set disabled
        home_btn["relief"] = "sunken"           # button is set sunken
        home_btn["state"] = "disabled"          # button is set disabled
        cw_btn["relief"] = "sunken"             # button is set sunken
        cw_btn["state"] = "disabled"            # button is set disabled
        
        disable_widgets(btn_srv_label, relief="sunken")


def disable_widgets(parent, relief):
    for child in parent.winfo_children():       # iteration through children widgets in parent
            child["relief"] = relief            # slider is set sunken
            child["state"] = "disabled"         # slider is set disabled

def enable_widgets(parent, relief):
    for child in parent.winfo_children():       # iteration through children widgets in parent
            child["relief"] = relief            # slider is set flat
            child["state"] = "normal"           # slider is set normal
    
######################################################################################################################
    





# ####################################################################################################################
# ############################### Starting variables  ################################################################
# ####################################################################################################################

AF_mac = 'e4:5f:01:8d:59:97'                 # mac address of Andrea Favero Cubotino_micro (optimized servos setting for my bot)
disp.show_on_display('SERVOS', 'TUNING', fs1=38, y2=75, fs2=38)  # feedback is printed to the display
disp.set_backlight(1)                        # display backlight is turned on, in case it wasn't
printout = False                             # boolean to print the settings at script startingstart
robot_settings  = read_settings_file()       # servos settings are retrieved from the json settings files
upload_settings(robot_settings)              # servos settings are loaded to global
servo_init()                                 # servos are initialez





# ####################################################################################################################
# ############################### GUI high level part ################################################################
# ####################################################################################################################
root = tk.Tk()                            # initialize tkinter as root 
root.title("CUBOTino servos setting")     # name is assigned to GUI root
root.geometry('+0+0')                     # windows is initially presented at top-left of the screen
######################################################################################################################





# ####################################################################################################################
# ############################### GUI Low level part ################################################################£
# ####################################################################################################################


#### top servo related widgets ####
top_srv_label = tk.LabelFrame(root, text="Top cover - servo settings", labelanchor="nw", font=("Arial", "14"))
top_srv_label.grid(row=0, column=0, rowspan=1, columnspan=3, sticky="n", padx=20, pady=30)


s_top_srv_close = tk.Scale(top_srv_label, label="CLOSE", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=1, to_=-1, resolution=0.02)#, command=servo_close)                           
s_top_srv_close.grid(row=0, column=0, sticky="w", padx=12, pady=5)
s_top_srv_close.set(t_servo_close)
s_top_srv_close.bind("<ButtonRelease-1>", servo_close)


s_top_srv_rel_delta = tk.Scale(top_srv_label, label="RELEASE (at close)", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0, to_=0.2, resolution=0.02)                          
s_top_srv_rel_delta.grid(row=0, column=1, sticky="w", padx=12, pady=5)
s_top_srv_rel_delta.set(t_servo_rel_delta)
s_top_srv_rel_delta.bind("<ButtonRelease-1>", servo_release)


s_top_srv_open = tk.Scale(top_srv_label, label="OPEN", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=1, to_=-1, resolution=0.02)
s_top_srv_open.grid(row=0, column=2, sticky="w", padx=12, pady=5)
s_top_srv_open.set(t_servo_open)
s_top_srv_open.bind("<ButtonRelease-1>", servo_open)


s_top_srv_read = tk.Scale(top_srv_label, label="READ", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=1, to_=-1, resolution=0.02)
s_top_srv_read.grid(row=0, column=3, sticky="w", padx=12, pady=5)
s_top_srv_read.set(t_servo_read)
s_top_srv_read.bind("<ButtonRelease-1>", servo_read)


s_top_srv_flip = tk.Scale(top_srv_label, label="FLIP", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=1, to_=-1, resolution=0.02)
s_top_srv_flip.grid(row=0, column=4, sticky="w", padx=12, pady=5)
s_top_srv_flip.set(t_servo_flip)
s_top_srv_flip.bind("<ButtonRelease-1>", servo_flip)


s_top_srv_rel_time = tk.Scale(top_srv_label, label="RELEASE TIME at close (s)", font=('arial','14'),
                                     orient='horizontal', relief='raised', length=320, from_=0, to_=0.5,
                                     resolution=0.02, command=servo_rel_close)
s_top_srv_rel_time.grid(row=1, column=0, sticky="w", padx=12, pady=15)
s_top_srv_rel_time.set(t_rel_time)


s_top_srv_flip_to_close_time = tk.Scale(top_srv_label, label="TIME: flip > close (s)", font=('arial','14'),
                                        orient='horizontal', relief='raised', length=320, from_=0, to_=1, 
                                        resolution=0.02, command=flip_to_close_time)
s_top_srv_flip_to_close_time.grid(row=1, column=1, sticky="w", padx=12, pady=15)
s_top_srv_flip_to_close_time.set(t_flip_to_close_time)


s_top_srv_close_to_flip_time = tk.Scale(top_srv_label, label="TIME: close > flip (s)", font=('arial','14'),
                                        orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                        resolution=0.02, command=close_to_flip_time)
s_top_srv_close_to_flip_time.grid(row=1, column=2, sticky="w", padx=12, pady=15)
s_top_srv_close_to_flip_time.set(t_close_to_flip_time)


s_top_srv_flip_open_time = tk.Scale(top_srv_label, label="TIME: flip <> open (s)", font=('arial','14'),
                                    orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                    resolution=0.02, command=flip_open_time)
s_top_srv_flip_open_time.grid(row=1, column=3, sticky="w", padx=12, pady=15)
s_top_srv_flip_open_time.set(t_flip_open_time)


s_top_srv_open_close_time = tk.Scale(top_srv_label, label="TIME: open <> close(s)", font=('arial','14'),
                                     orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                     resolution=0.02, command=open_close_time)
s_top_srv_open_close_time.grid(row=1, column=4, sticky="w", padx=12, pady=15)
s_top_srv_open_close_time.set(t_open_close_time)








#### bottom servo related widgets ####
btn_srv_label = tk.LabelFrame(root, text="Cube holder - servo settings",
                                   labelanchor="nw", font=("Arial", "14"))
btn_srv_label.grid(row=1, column=0, rowspan=1, columnspan=3, sticky="n", padx=20, pady=30)


s_btn_srv_min_pulse = tk.Scale(btn_srv_label, label="MIN PULSE WIDTH", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0.2, to_=1.2, resolution=0.02)
s_btn_srv_min_pulse.grid(row=0, column=0, sticky="w", padx=12, pady=5)
s_btn_srv_min_pulse.set(b_min_pulse_width)
s_btn_srv_min_pulse.bind("<ButtonRelease-1>", btn_srv_min_pulse)



s_btn_srv_CCW = tk.Scale(btn_srv_label, label="CCW", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=-1, to_=-0.5, resolution=0.02)
s_btn_srv_CCW.grid(row=0, column=1, sticky="w", padx=12, pady=5)
s_btn_srv_CCW.set(b_servo_CCW)
s_btn_srv_CCW.bind("<ButtonRelease-1>", servo_CCW)


s_btn_srv_home = tk.Scale(btn_srv_label, label="HOME", font=('arial','14'), orient='horizontal',
                          width=30, relief='raised', length=320, from_=-0.5, to_=0.5, resolution=0.02)                           
s_btn_srv_home.grid(row=0, rowspan=2, column=2, sticky="w", padx=12, pady=5)
s_btn_srv_home.set(b_home)
s_btn_srv_home.bind("<ButtonRelease-1>", servo_home)


s_btn_srv_CW = tk.Scale(btn_srv_label, label="CW", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0.5, to_=1, resolution=0.02)
s_btn_srv_CW.grid(row=0, column=3, sticky="w", padx=12, pady=5)
s_btn_srv_CW.set(b_servo_CW)
s_btn_srv_CW.bind("<ButtonRelease-1>", servo_CW)


s_btn_srv_max_pulse = tk.Scale(btn_srv_label, label="MAX PULSE WIDTH", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=1.8, to_=2.8, resolution=0.02)
s_btn_srv_max_pulse.grid(row=0, column=4, sticky="w", padx=12, pady=5)
s_btn_srv_max_pulse.set(b_max_pulse_width)
s_btn_srv_max_pulse.bind("<ButtonRelease-1>", btn_srv_max_pulse)


s_btn_srv_rel_CCW = tk.Scale(btn_srv_label, label="RELEASE at CCW  -->", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0, to_=0.2, resolution=0.02)
s_btn_srv_rel_CCW.grid(row=1, column=0, sticky="w", padx=12, pady=5)
s_btn_srv_rel_CCW.set(b_rel_CCW)
s_btn_srv_rel_CCW.bind("<ButtonRelease-1>", servo_rel_CCW)


s_extra_home_CW = tk.Scale(btn_srv_label, label="EXTRA HOME from CW  <--", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0.2, to_=0, resolution=0.02)
s_extra_home_CW.grid(row=1, column=1, sticky="w", padx=12, pady=5)
s_extra_home_CW.set(b_extra_home_CW)
s_extra_home_CW.bind("<ButtonRelease-1>", servo_extra_home_CW)


s_extra_home_CCW = tk.Scale(btn_srv_label, label="EXTRA HOME from CCW  -->", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0, to_=0.2, resolution=0.02)                           
s_extra_home_CCW.grid(row=1, column=3, sticky="w", padx=12, pady=5)
s_extra_home_CCW.set(b_extra_home_CCW)
s_extra_home_CCW.bind("<ButtonRelease-1>", servo_extra_home_CCW)


s_btn_srv_rel_CW = tk.Scale(btn_srv_label, label="RELEASE at CW  <--", font=('arial','14'), orient='horizontal',
                          relief='raised', length=320, from_=0.2, to_=0, resolution=0.02)
s_btn_srv_rel_CW.grid(row=1, column=4, sticky="w", padx=12, pady=5)
s_btn_srv_rel_CW.set(b_rel_CW)
s_btn_srv_rel_CW.bind("<ButtonRelease-1>", servo_rel_CW)



s_btn_srv_spin_time = tk.Scale(btn_srv_label, label="TIME: spin (s)", font=('arial','14'),
                                        orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                        resolution=0.02, command=servo_spin_time)
s_btn_srv_spin_time.grid(row=2, column=1, sticky="w", padx=12, pady=15)
s_btn_srv_spin_time.set(b_spin_time)


s_btn_srv_rotate_time = tk.Scale(btn_srv_label, label="TIME: rotate (s)", font=('arial','14'),
                                    orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                    resolution=0.02, command=servo_rotate_time)
s_btn_srv_rotate_time.grid(row=2, column=2, sticky="w", padx=12, pady=15)
s_btn_srv_rotate_time.set(b_rotate_time)


s_btn_srv_rel_time = tk.Scale(btn_srv_label, label="TIME: release (s)", font=('arial','14'),
                                     orient='horizontal', relief='raised', length=320, from_=0, to_=1,
                                     resolution=0.02, command=servo_rel_time)
s_btn_srv_rel_time.grid(row=2, column=3, sticky="w", padx=12, pady=15)
s_btn_srv_rel_time.set(b_rel_time)








#### test settings related widgets ####
test_label = tk.LabelFrame(root, text="Test (sliders settings)", labelanchor="nw", font=("Arial", "14"))
test_label.grid(row=2, column=0, rowspan=1, columnspan=1, sticky="w", padx=20, pady=30)

close_btn = tk.Button(test_label, text="CLOSE", height=1, width=15, state="normal", command= close_top_cover)
close_btn.configure(font=("Arial", "12"))
close_btn.grid(row=0, column=0, sticky="n", padx=20, pady=10)

open_btn = tk.Button(test_label, text="OPEN", height=1, width=15, state="normal", command= open_top_cover)
open_btn.configure(font=("Arial", "12"))
open_btn.grid(row=0, column=1, sticky="n", padx=20, pady=10)

read_btn = tk.Button(test_label, text="READ", height=1, width=15, state="normal", command= read_position)
read_btn.configure(font=("Arial", "12"))
read_btn.grid(row=0, column=2, sticky="n", padx=20, pady=10)

flip_btn = tk.Button(test_label, text="FLIP  (toggle)", height=1, width=18, state="normal", command= flip_cube)
flip_btn.configure(font=("Arial", "12"))
flip_btn.grid(row=0, column=3, sticky="n", padx=20, pady=10)

ccw_btn = tk.Button(test_label, text="CCW", height=1, width=15, state="normal", command= ccw)
ccw_btn.configure(font=("Arial", "12"))
ccw_btn.grid(row=1, column=0, sticky="n", padx=20, pady=10)

home_btn = tk.Button(test_label, text="HOME", height=1, width=15, state="normal", command= home)
home_btn.configure(font=("Arial", "12"))
home_btn.grid(row=1, column=1, sticky="n", padx=20, pady=10)

cw_btn = tk.Button(test_label, text="CW", height=1, width=15, state="normal", command= cw)
cw_btn.configure(font=("Arial", "12"))
cw_btn.grid(row=1, column=2, sticky="n", padx=20, pady=10)

#######################################################################################




#### saving settings ####
files_label = tk.LabelFrame(root, text="Settings files", labelanchor="nw", font=("Arial", "14"))
files_label.grid(row=2, column=1, rowspan=1, columnspan=1, sticky="w", padx=20, pady=30)


reset_btn = tk.Button(files_label, text="LOAD PREVIOUS SETTING", height=1, width=30, state="normal", command= load_previous_settings)
reset_btn.configure(font=("Arial", "12"))
reset_btn.grid(row=0, column=0, sticky="n", padx=20, pady=10)


save_btn = tk.Button(files_label, text="SAVE SETTINGS", height=1, width=30, state="normal", command= save_new_settings)
save_btn.configure(font=("Arial", "12"))
save_btn.grid(row=1, column=0, sticky="n", padx=20, pady=10)




#### Large test ####
large_test_label = tk.LabelFrame(root, text="Full test", labelanchor="nw", font=("Arial", "14"))
large_test_label.grid(row=2, column=2, rowspan=1, columnspan=1, sticky="w", padx=20, pady=30)

test_btn = tk.Button(large_test_label, text="LONG TEST\n(on saved settings)", height=4, width=22, state="normal", command= test)
test_btn.configure(font=("Arial", "12"))
test_btn.grid(row=0, column=0, sticky="w", padx=20, pady=10)





# ####################################################################################################################
# ###############################     main part   ####################################################################
# ####################################################################################################################

btm_srv_widgets_status()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()   # tkinter main loop