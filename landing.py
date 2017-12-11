# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 08:59:41 2017

@author: Pierre
"""

from math import exp, pi, sqrt, sin, cos, asin

g_0 = 9.80665
R_star = 8.3144598
M = 0.0289644

parachute_rad = 0.3048 #1 foot in meters
parachute_area = pi * parachute_rad ** 2
payload_area = 0.3 * 0.3

C = 0.3 #from http://randomaerospace.com/Random_Aerospace/Balloons.html

#mass parameters
pay_m = 0.5
bal_m = 1.0
oth_m = 0.3

m = pay_m + oth_m + 0.05 * bal_m #DESCENT MASS 

outfile = 'prediction.txt'

def density_at_alt(alt):
    
    #altitutde is given in m above mean sea level
    
    if 0 <= alt < 11000:
        p_b = 1.2250
        T_b = 288.15
        L_b = -0.0065
        h_b = 0
        
    elif 11000 <= alt < 20000:
        p_b = 0.36391
        T_b = 216.65
        L_b = 0
        h_b = 11000
        
    elif 20000 <= alt < 32000:
        p_b = 0.08803
        T_b = 216.65
        L_b = 0.001
        h_b = 20000
        
    elif 32000 <= alt < 47000:
        p_b = 0.01322
        T_b = 288.65
        L_b = 0.0028
        h_b = 32000
        
    if L_b != 0:
        
        fraction = T_b / (T_b + L_b*(alt - h_b))
        exponent = 1 + (g_0 * M)/(R_star * L_b)
        
        return p_b * (fraction) ** exponent
    
    if L_b == 0:
        exponent = (-g_0 * M * (alt - h_b))/(R_star * T_b)
        
        return p_b * exp(exponent)

def drag_at_alt(alt,descent_rate):
    rho = density_at_alt(alt)
    
    return 0.5 * C * rho * descent_rate ** 2 * (parachute_area + payload_area)

def find_bandchange(windband,v0):
    
    alt_lower = windband[0]
    alt_upper = windband[1]
    d_lat_dt = windband[2]
    d_long_dt = windband[3]
    
    bandwidth =  alt_upper - alt_lower
    band_section = -0.001 * bandwidth
    
    sum_t = 0
    alti = alt_upper
    
    for i in range (0,1000):
        a = 1/m * (drag_at_alt(alti,v0) - g_0)
        
        dt = (-v0 - sqrt(v0 ** 2 + 2 * a * band_section))/a
        
        sum_t += dt
        
        alti -= band_section
        v0 = v0 + a * dt
    
    delta_lat = d_lat_dt * sum_t
    delta_long = d_long_dt * sum_t
    
    return [delta_lat,delta_long,alt_lower,v0]

def how_many_bands(winds,alt):
    for i in range(0,len(winds)):
        if winds[i][1] > alt:
            return i

    return len(winds)

def splat(lat,long,alt,speed,heading,winds):
    
    try:
        num_bands = how_many_bands(winds,alt)
        
        #to_ground = how_many_bands(winds, alt)
        
        for i in range(num_bands-1,-1,-1):
            
            [delta_lat,delta_long,new_alt,new_speed] = find_bandchange(winds[i],speed)
            
            lat = lat + delta_lat
            long = long + delta_long
            
        h = open(outfile,'a')
        h.write(str(round(lat,6)) + ',' + str(round(long,6)) + ',')
        h.close()
        
        return (lat,long)
            

    except FileNotFoundError:
        h.close()
    
earth_radius = 6371000 #m
alt = 280

def how_far(lat1,long1,time,lat2 = -34.37435, long2 = 147.86021):
    del_lat = abs(lat1 - lat2) * pi / 180
    del_long = abs(long1 - long2) * pi / 180

    lat_lower = lat1 * pi / 180
    lat_upper = lat2 * pi / 180
    
    #find the radius from the centre of the earth
    
    R = earth_radius + alt
    
    term_1 = (sin(del_lat/2)) ** 2
    term_2 = cos(lat_lower) * cos(lat_upper)
    term_3 = (sin(del_long/2)) ** 2
    
    dist = 2*R*asin(sqrt(term_1 + term_2 * term_3))
    
    print(time, 'Distance:', dist/1000, 'km')
