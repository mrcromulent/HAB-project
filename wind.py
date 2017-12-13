  # -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:33:53 2017

@author: Pierre
"""

from datetime import datetime

def calc_windspeed(wind_lower_data,wind_upper_data):
    
    FMT = '%H:%M:%S' #datetime format
    
    #find the time differences between the top and bottom of the band
    
    del_t = datetime.strptime(wind_upper_data[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    dt = del_t.total_seconds()
    
    #Convert latitutde and longitude data to radians
    
    deg_lat = (wind_upper_data[1] - wind_lower_data[1])
    deg_long = (wind_upper_data[2] - wind_lower_data[2]) 

    
    return [wind_lower_data[3],wind_upper_data[3],deg_lat/dt,deg_long/dt]

def make_new_band(state,wind_lower_data,winds):
    
    # ... record the current data
    wind_upper_data = state[:]

    #calculate the windspeeds (in deg/s) and add it to the list
    new_wind = calc_windspeed(wind_lower_data,wind_upper_data)
    winds.append(new_wind)
    
    #reset the lower band data
    wind_lower_data = wind_upper_data[:]
    
    return [winds,wind_lower_data]