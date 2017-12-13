# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 10:25:48 2017

@author: Pierre
"""

import pickle
import landing
import matplotlib.pyplot as plt
import math

f = open('store.pckl', 'rb')
winds = pickle.load(f)
f.close()

speed = 0
speeds = [0]
lat = -34.40288
long = 147.70079

for i in range(270,-1,-1):
    
    [delta_lat,delta_long,new_alt,new_speed] = landing.find_bandchange(winds[i],speed)
    
    lat = lat + delta_lat
    long = long + delta_long
    speed = new_speed
    
    speeds.append(speed)

real_velocities = []

f = open('test3.txt')
f.seek(0)

for i in range(0,250):
    line = f.readline().split(',')
    f.readline()
    
    v = float(line[6])
    angle = math.radians(float(line[7]))
    real_velocities.append(v*math.cos(angle))

f.close()

plt.plot(speeds)
plt.plot(real_velocities)
plt.show()