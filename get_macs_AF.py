#!/usr/bin/env python
# coding: utf-8

"""
######################################################################################################################
# Andrea Favero 20 March 2023
# 
# Little script returning a tuple with mac adresses from a text file
# This script relates to CUBOTino micro, an extremely small and simple Rubik's cube solver robot 3D printed
# CUBOTino micro is the smallest version of the CUBOTino versions
#
######################################################################################################################
"""

def get_macs_AF():
    import os.path, pathlib                       # os is imported to ensure the file presence, check/make
    folder = pathlib.Path().resolve()             # active folder (should be home/pi/cube)  
    fname = os.path.join(folder,'macs_AF.txt')    # filename for the text file with listed the mac adrresses
    macs_AF = []                                  # emppty list to store the mac addresses
    with open(fname, "r") as f:                   # file is opened in reading mode
        macs = f.readlines()                      # text lines are retrieved
        for mac in macs:                          # iteration over the lines
            macs_AF.append(mac.strip())           # stripped lines contents are appended to the mac list
    
    return tuple(macs_AF)                         # list is converted to tuple and returned
    