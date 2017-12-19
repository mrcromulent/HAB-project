  # -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:33:53 2017

@author: Pierre
"""

from datetime import datetime
import landing
FMT = '%H:%M:%S' #datetime format
v0 = 0


def calc_windspeed(wind_lower_data,wind_upper_data):
    
    #find the time differences between the top and bottom of the band
    
    del_t = datetime.strptime(wind_upper_data[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    dt = del_t.total_seconds()
    
    #Convert latitutde and longitude data to radians
    
    deg_lat = (wind_upper_data[1] - wind_lower_data[1])
    deg_long = (wind_upper_data[2] - wind_lower_data[2])
    
    lower_elev = wind_lower_data[3]
    upper_elev = wind_upper_data[3]
        
    #extract average temperature and pressure. Convert to Pascal and Kelvin and decimal
    
    temp = 0.5 * (wind_lower_data[6]  + wind_upper_data[6]) + 273.2
    press = 0.5 * 100 * (wind_lower_data[7] + wind_upper_data[7])
    humidity = 0.5 * 1/100 * (wind_lower_data[8]  + wind_upper_data[8])
    
    ######################################
    
#    ac = landing.ac_at_alt(temp,press)

#    return [lower_elev,upper_elev,ac*deg_lat/dt,ac*deg_long/dt,temp,press,humidity]
    
    ######################################

    return [lower_elev,upper_elev,deg_lat/dt,deg_long/dt,temp,press,humidity]
    
def make_new_band(state,wind_lower_data,winds):
    
    # ... record the current data
    wind_upper_data = state[:]

    #calculate the windspeeds (in deg/s) and add it to the list
    new_wind = calc_windspeed(wind_lower_data,wind_upper_data)
    winds.append(new_wind)
    
    #reset the lower band data
    wind_lower_data = wind_upper_data[:]
    
    return [winds,wind_lower_data]

def refine_drag_coeff(wind_lower_data,state,winds):
    
    global v0
    
    at = datetime.strptime(state[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    actual_time = at.total_seconds()
    
    ind = landing.how_many_bands(winds,state[3])
    
    [estimated_time,_,_,_,v0] = landing.find_bandchange(winds[ind + 1],v0)
    
    wind_lower_data = state[:]
    
    landing.C = landing.C * (actual_time/estimated_time)
    
    if landing.C > 2:
        landing.C = 2
        
    elif landing.C < 0.5:
        landing.C = 0.5
    
    return wind_lower_data
    