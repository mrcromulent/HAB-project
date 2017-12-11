# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:21:36 2017

@author: Pierre
"""
import math
earth_radius = 6371000 #m
alt = 280

def how_far(lat1,long1,lat2 = -34.37435, long2 = 147.86021):
    del_lat = abs(lat1 - lat2) * math.pi / 180
    del_long = abs(long1 - long2) * math.pi / 180

    lat_lower = lat1 * math.pi / 180
    lat_upper = lat2 * math.pi / 180
    
    #find the radius from the centre of the earth
    
    R = earth_radius + alt
    
    term_1 = (math.sin(del_lat/2)) ** 2
    term_2 = math.cos(lat_lower) * math.cos(lat_upper)
    term_3 = (math.sin(del_long/2)) ** 2
    
    dist = 2*R*math.asin(math.sqrt(term_1 + term_2 * term_3))
    
    print('The distance is', dist/1000, 'km')