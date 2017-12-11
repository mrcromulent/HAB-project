# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 10:03:42 2017

@author: Pierre
"""

filepath = 'YERRALOON1_DATA\\telemetry.txt'
telemetry = []

f = open(filepath)

#Figure out where the end of the file is so we know when to stop reading
f.seek(0,2)
global end
end = f.tell()
f.seek(0)

#Define a function to read only the lines we care about

def read_properly(f):
    
    tmp = f.readline().split(',')
    
    if tmp[0] == '$$YERRA':
        return tmp
    elif f.tell() == end:
        return 'end'
    else:
        return read_properly(f)

line = read_properly(f)
telemetry.append(line)

while line != 'end':
    telemetry.append(line)
    line = read_properly(f)
    