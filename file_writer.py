# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time

sleep_time = 0.01

with open('YERRALOON1_DATA\\telemetry.txt') as f:
    for i in range(0,6000):
        if i == 0:
            f.seek(0)
        
        line = f.readline()
        
        with open('test.txt','a') as g:
            if line[0] == 'F':
                g.write(line) #Free space line
                line = f.readline()
                g.write(line) #Yerra line
                line = f.readline()
                g.write(line) #XX line
                
            elif line[0:3] == '$$Y':
                g.write(line) #Yerra line
                line = f.readline()
                g.write(line) #XX line
            else:
                g.write(line) #XX line
            
 
    time.sleep(sleep_time)
