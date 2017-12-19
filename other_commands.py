# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:09:55 2017

@author: Pierre
"""

import os
from math import nan

read_pos = 0
safe_line = [nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan]

def file_empty(filepath):
    #checks if the file at filepath is empty or non-existant
    
    try:
        #120 is approximately the length of one $$YERRA line
        return (os.stat(filepath).st_size < 120)
    
    except FileNotFoundError:
        return True

def read_properly(f):   
    #this function reads until it finds a line starting with $$YERRA
    #or the end of the file object f
    
    tmp = f.readline().split(',')
    
    if tmp[0] == '$$YERRA':
        return tmp
    elif tmp[0] == '':
        return ['end']
    else:
        return read_properly(f)

def record_launch_values(filepath):
    
    try:
        with open(filepath) as f:
            f.seek(read_pos)  
            line = read_properly(f)
            update_read_position(f.tell())
            
        start_time = line[2]
        start_lat = float(line[3])
        start_long = float(line[4])
        start_elev = float(line[5])
        
        return (start_time,start_lat,start_long,start_elev)

    except (IndexError,FileNotFoundError,ValueError):
        return last_safe_line()

def add_telemetry(filepath):
    try:
        
        with open(filepath,'r') as f:
            f.seek(read_pos)
            line = read_properly(f)  
            update_read_position(f.tell())
            
        new_line = [line[0],line[1],line[2], float(line[3]),float(line[4]),\
                    float(line[5]),float(line[6]),float(line[7]), int(line[8]),\
                    float(line[9]),float(line[10]),float(line[11]),line[12]]
        
        if false_telemetry(filepath,new_line[2:8]):
            raise ValueError
            
        else:
            safe_line = new_line
        
        make_new_safe_line(safe_line)
        
        return safe_line
        
    except (IndexError,ValueError):
        return last_safe_line()
    

def false_telemetry(filepath,state = None):
    
    if state == None:
        (start_time,start_lat,start_long,start_elev) = record_launch_values(filepath)
        return (start_time == '00:00:00' or start_lat == 0.0 or start_long == 0.0 or start_elev == 0.0)
    
    else:
        [time,lat,long,alt,speed,heading] = state[:] #state variable
        
        return (not(-40 < lat < 0) or not(110 < long < 155) or alt < 1)
    
    
def last_safe_line():
    return safe_line

def make_new_safe_line(new_safe_line):
    global safe_line
    
    safe_line = new_safe_line
    
    
def update_read_position(new_read_pos):
    global read_pos
    
    read_pos = new_read_pos
    