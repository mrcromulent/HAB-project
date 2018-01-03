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
    """file_empty checks the status of the file at filepath. If it's empty 
    (less than the approximate length of a telemetry line) or 
    non-existant, it returns True."""
    
    try:
        #120 is approximately the length of one $$YERRA line
        return (os.stat(filepath).st_size < 120)
    
    except FileNotFoundError:
        return True

def read_properly(f):
    """This function reads an open file object, f, recursively until it 
    a line of telemetry beginning with '$$YERRA' or it reaches the end
    of the file. It will either return the properly formatted telemetry
    as a list or (in the case of reaching the end) will return ['end']"""
    
    tmp = f.readline().split(',')
    
    if tmp[0] == '$$YERRA': #Telemetry found
        
        #split the humidity and checksum into separate elements
        
        tmp2 = tmp[12].split('*')
        tmp.pop()
        tmp.extend(tmp2)
        
        return tmp
    
    elif tmp[0] == '': #End of file found
        return ['end']
    else: #Something else found. Will read next line.
        return read_properly(f) 

def record_launch_values(filepath):
    """record_launch_values() is called once as soon as the telemetry file 
    stops displaying false telemetry on boot. It records the start time,
    latitude, longitude and altitude of the launch from the file object
    f and returns them. If an error occurs, the function returns the"""
    
    try:
        
        #Open file as f
        
        with open(filepath) as f:
            f.seek(read_pos)  
            line = read_properly(f)
            update_read_position(f.tell())
            
        #record and return launch values
        
        start_time = line[2]
        start_lat = float(line[3])
        start_long = float(line[4])
        start_elev = float(line[5])
        
        return (start_time,start_lat,start_long,start_elev)

    except (IndexError,FileNotFoundError,ValueError):
        safe_launch_values = last_safe_line()
        return (safe_launch_values[2],safe_launch_values[3],safe_launch_values[4],safe_launch_values[5])
    
def add_telemetry(filepath):
    """ add_telemetry() takes the filepath of the telemtry file, opens it 
    as f and calls read_properly() on f. add_telemetry then updates the 
    global read_position in the file and formats the telemetry as strings,
    floats and ints. add_telemetry() calls false_telemetry() to check that
    the data is valid. If it is, the new, formatted line is returned and
    it becomes the new 'last safe line' of telemetry. If it is not valid, 
    the previous last safe line of telemetry is returned."""
    
    try:
        
        #Open the file as f and call read_properly
        
        with open(filepath) as f:
            f.seek(read_pos)
            line = read_properly(f)  
            update_read_position(f.tell())
            
        #Format the data
            
        new_line = [line[0],line[1],line[2], float(line[3]),float(line[4]),\
                    float(line[5]),float(line[6]),float(line[7]), int(line[8]),\
                    float(line[9]),float(line[10]),float(line[11]),float(line[12]),line[13]]
        
        #Check for false telemetry
        
        if false_telemetry(filepath,new_line[2:8]):
            raise ValueError
            
        else:
            safe_line = new_line
            
        #If not false telemetry, set as the new safe_line and return
        
        make_new_safe_line(safe_line)
        
        return safe_line
        
    except (IndexError,ValueError):
        
        #If false telemetry, return the last safe line, stored globally
        
        return last_safe_line()
    

def false_telemetry(filepath,state = None):
    """false_telemetry() runs several tests on either the filepath or the
    current state to determine if the data are incorrect. It will return
    True if any of these tests are failed."""
    
    if state == None: #For the case where state has not been defined yet
        (start_time,start_lat,start_long,start_elev) = record_launch_values(filepath)
        return (start_time == '00:00:00' or start_lat == 0.0 or start_long == 0.0 or start_elev == 0.0)
    
    else:
        [time,lat,long,alt,speed,heading] = state[:] #extract the data
        
        return (not(-40 < lat < 0) or not(110 < long < 155) or alt < 1)
    
    
def last_safe_line():
    """Returns the globally-defined last safe line"""
    return safe_line

def make_new_safe_line(new_safe_line):
    """Makes a new safe line from the input"""
    
    global safe_line
    
    safe_line = new_safe_line
    
    
def update_read_position(new_read_pos):
    """Updates the read position to the supplied value"""
    
    global read_pos
    
    read_pos = new_read_pos
    