# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time

URL = 'YERRALOON1_DATA\\telemetry.txt'
sleep_time = 0


for i in range(0,10000):
    
    #ignore the first line
    if i == 0:
        f = open(URL,'r')
        f.seek(0)

    line = f.readline()
    
    g = open('test.txt','a')
    
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
    
    g.close()
        
    time.sleep(sleep_time)
    

f.close()