# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time


for i in range(0,50):
    
    #ignore the first line
    if i == 0:
        f = open('telemetry_test.txt','r')
#        f.readline()
    
    line = f.readline()
    
    g = open('test.txt','a')
    g.write(line)
    g.close()
        
    time.sleep(12)
    

f.close()