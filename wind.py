# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:33:53 2017

@author: Pierre
"""

from datetime import datetime
import math

def calc_windspeed(wind_lower_data,wind_upper_data):
    
    FMT = '%H:%M:%S' #datetime format      
    ear_rad = 6000000 #m
    
    #find the time differences between the top and bottom of the band
    
    del_t = datetime.strptime(wind_upper_data[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    dt = del_t.total_seconds()
    
    #Convert latitutde and longitude data to radians
    
    del_lat = (wind_upper_data[1] - wind_lower_data[1]) * math.pi / 180
    del_long = (wind_upper_data[2] - wind_lower_data[2]) * math.pi / 180
    
    lat_lower = wind_lower_data[1] * math.pi / 180
    lat_upper = wind_upper_data[1] * math.pi / 180
    
    #find the radius from the centre of the earth
    
    R = wind_upper_data[3] + ear_rad
    
    term_1 = (math.sin(del_lat)) ** 2
    term_2 = math.cos(lat_lower) * math.cos(lat_upper)
    term_3 = (math.sin(del_long)) ** 2
    
    dist = 2*R*math.sqrt(term_1 + term_2 * term_3)
    
    return [wind_lower_data[3],wind_upper_data[3],dist/dt]