  # -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:33:53 2017

@author: Pierre
"""

from datetime import datetime
import landing
FMT = '%H:%M:%S' #datetime format


def calc_windspeed(wind_lower_data,wind_upper_data):
    """This function constructs and returns a new windband, taking as 
    arguments the state values from the top and bottom of the windband.
    calc_windspeed() finds the amount of time spent in the band and divides
    the change in latitude and longitude by this time to produce an angular
    speed (deg lat/sec and deg long/sec). These are then scaled by the 
    area_correction factor ac (See: landing.ac_at_tp()). The final windband 
    includes the upper and lower altitudes of the band,the angular speeds
    and the average temperature, pressure and humidity, in Kelvin, Pascal
    and decimal respectively."""
    
    #Find the time differences between the top and bottom of the band
    
    del_t = datetime.strptime(wind_upper_data[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    dt = del_t.total_seconds()
    
    #Find the changesin latitude, longitude and altitude
    
    deg_lat = (wind_upper_data[1] - wind_lower_data[1])
    deg_long = (wind_upper_data[2] - wind_lower_data[2])
    
    lower_elev = wind_lower_data[3]
    upper_elev = wind_upper_data[3]
        
    #Extract average temperature and pressure. Convert to Pascal and Kelvin and decimal
    
    temp = 0.5 * (wind_lower_data[6]  + wind_upper_data[6]) + 273.2
    press = 0.5 * 100 * (wind_lower_data[7] + wind_upper_data[7])
    humidity = 0.5 * 1/100 * (wind_lower_data[8]  + wind_upper_data[8])
    
    #Find the area correction
    
    ac = landing.ac_at_tp(temp,press)

    return [lower_elev,upper_elev,ac*deg_lat/dt,ac*deg_long/dt,temp,press,humidity]
    

def make_new_band(state,wind_lower_data,winds):
    """This function handles the function calls to make a new windband 
    and adds the new wind bands to the master list, winds."""
    
    # Set the upper bound of the band at thecurrent location
    wind_upper_data = state[:]

    #Call calc_windspeed and add the new band to winds.
    new_wind = calc_windspeed(wind_lower_data,wind_upper_data)
    winds.append(new_wind)
    
    #reset the lower band data
    wind_lower_data = wind_upper_data[:]
    
    return [winds,wind_lower_data]

