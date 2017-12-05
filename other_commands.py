# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:09:55 2017

@author: Pierre
"""

import os

def file_empty(filepath):
    try:
        return (os.stat(filepath).st_size < 50)
    
    except FileNotFoundError:
        return True


#MODIFY THIS FILE TO CHECK IF THE VALUES MAKE SENSE

def record_launch_values(filepath):
    f = open(filepath)    
    f.readline() #ignore first row

    start_data = f.readline().split(',')

    #assign data to variables

    start_time = start_data[2]
    start_lat = float(start_data[3])
    start_long = float(start_data[4])
    start_elev = float(start_data[5])

    f.close()
    
    return (start_time,start_lat,start_long,start_elev)


def add_telemetry(filepath):
    try:
        f = open(filepath,'rb')    
        f.seek(-78,2)
        
        #convert last line into string
        
        ll = str(f.readline())
        last_line = ll[2:-6].split(',')    
        
        #add to the telemetry list
        
        f.close()
        
        return [last_line[0],last_line[1],last_line[2], float(last_line[3]),\
                float(last_line[4]),float(last_line[5]),float(last_line[6]),\
                float(last_line[7]), int(last_line[8]),float(last_line[9]),\
                float(last_line[10]),last_line[11],last_line[12]]
        
    except FileNotFoundError:
        return [float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'), \
            float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan')]
    
    finally:
        f.close()