# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time

sleep_time = 2


for i in range(0,500):
    
    #ignore the first line
    if i == 0:
        f = open('YERRALOON1_telemetry.txt','r')
        f.seek(0)
#        f.readline()
    
    line = f.readline()
    
    g = open('test.txt','a')
    g.write(line)
    g.close()
        
    time.sleep(sleep_time)
    

f.close()