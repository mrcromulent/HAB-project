# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 08:59:41 2017

@author: Pierre
"""

from math import exp, pi, sqrt, sin, cos, asin, radians
from datetime import datetime
FMT = '%H:%M:%S' #datetime format

g_0 = 9.80665 # m/s^2
R_star = 8.3144598 #gas constant, m^3 Pa/ K / mol
M = 0.0289644 #molar mass of air
M_helium = 0.004 #kg/mol
R = 6371 + 0.280 #km. Earth radius + temora altitude
 
parachute_area = pi * 0.3048 ** 2 #r = 1 foot in meters
payload_area = 0.3 * 0.3

C = 1.5 #from https://www.grc.nasa.gov/www/k-12/VirtualAero/BottleRocket/airplane/rktvrecv.html
C_box = 1.15 #from https://www.engineersedge.com/fluid_flow/rectangular_flat_plate_drag_14036.htm

#mass parameters of the balloon
pay_m = 1.2
bal_m = 1.2
gas_m = 0.28 #kg, estimated from https://www.webqc.org/ideal_gas_law.html

n = gas_m / M_helium

descent_m = pay_m + 0.05 * bal_m #DESCENT MASS 

v0 = 0

###########################################################################################

#def density_at_tph(T,P,humidity):
#    
#    #from https://wahiduddin.net/calc/density_altitude.htm
#    #T in K, P in Pa, humidity as a decimal
#    
#    T_c = T - 273.2 #Find the temperature in Celsius
#    Rd = 287.05
#    eso = 6.1078
#    
#    #Define 
#    
#    c0 = 0.99999683
#    c1 = -0.90826951*10 ** (-2)
#    c2 = 0.78736169*10 ** (-4)
#    c3 = -0.61117958*10 ** (-6)
#    c4 = 0.43884187*10 ** (-8)
#    c5 = -0.29883885*10 ** (-10)
#    c6 = 0.21874425*10 ** (-12)
#    c7 = -0.17892321*10 ** (-14)
#    c8 = 0.11112018*10 ** (-16)
#    c9 = -0.30994571*10 ** (-19)
#    
#    p = (c0+T_c*(c1+T_c*(c2+T_c*(c3+T_c*(c4+\
#   T_c*(c5+T_c*(c6+T_c*(c7+T_c*(c8+T_c*c9)))))))))
#    
#    E_s = 100*eso/(p ** 8) #Pa
#    
#    pv = E_s * humidity
#    
#    return (P/(Rd*T))*(1-(0.378*pv)/P)

#def drag_at_tph(temp,press,humidity,descent_rate):
#    
#    rho = density_at_tph(temp,press,humidity)
#    
#    return 0.5 * descent_rate ** 2 * rho * (C * parachute_area + C_box * payload_area)
#    #return 0.5 * C * descent_rate ** 2 * rho * (parachute_area + payload_area)

#############################################################################################
    
def density_at_alt(alt):

    #altitutde is given in m above mean sea level
    #from https://en.wikipedia.org/wiki/Barometric_formula
    
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
    
    return 0.5 * descent_rate ** 2 * rho * (C * parachute_area + C_box * payload_area)
    #return 0.5 * C * descent_rate ** 2 * rho * (parachute_area + payload_area)

def find_bandchange(windband,v0):
    
    #extract data from the windband
    
    [alt_lower,alt_upper,dLat_dt,dLong_dt,temp,press,humidity] = windband[:]
    
    bandwidth =  alt_upper - alt_lower
    
    #split the windband into band_sections...
    
    band_section = -0.001 * bandwidth
    
    sum_t = 0
    alti = alt_upper
    
    #...and find the time spent in each using kinematic equations
    
    for i in range (0,1000):
        
        ######################################################
        
#        a = 1/descent_m * (drag_at_tph(temp,press,humidity,v0) - g_0)
        
        ######################################################

        a = 1/descent_m * (drag_at_alt(alti,v0) - g_0)
        
        dt = (-v0 - sqrt(v0 ** 2 + 2 * a * band_section))/a
        
        sum_t += dt
        
        alti += band_section
        v0 = v0 + a * dt
    
    #find the bandchange by multiplying the rate of change of latitude ...
    #and longitude by the total time spent, sum_t
    
    delta_lat = dLat_dt * sum_t
    delta_long = dLong_dt * sum_t
    
    return [sum_t,delta_lat,delta_long,alt_lower,v0]

def how_many_bands(winds,alt):
    for i in range(0,len(winds)):
        if winds[i][1] > alt:
            return i

    return len(winds)

def splat(state,winds):
    
    #extract the relevant quantities from the arguments
    
    [time,lat,long,alt,speed,heading] = state[0:6]
    
    #find the number of bands below the payload
    
    num_bands = how_many_bands(winds,alt)
    
    #call find_bandchange on each band and sum the results
    
    for i in range(num_bands-1,-1,-1):
        
        [_,delta_lat,delta_long,new_alt,new_speed] = find_bandchange(winds[i],speed)
        
        lat = lat + delta_lat
        long = long + delta_long
        speed = new_speed
        
    #write the results to the prediction file and return the current precition
        
    with open('prediction.txt','a') as h:
        h.write(time + ',' + str(round(lat,6)) + ',' + str(round(long,6)) + '\n')
    
    return (lat,long)
            

def how_far(prediction,time,lat2 = -34.37435, long2 = 147.859):
    
    #this function finds the distance between any two points of latitude and longitude
    #default arguments are for YERRALOON1's landing site.
    
    #Forumula from https://www.movable-type.co.uk/scripts/latlong.html
    
    [lat1,long1] = prediction[:]
    
    del_lat = radians(lat1 - lat2)
    del_long = radians(long1 - long2)

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    
    a = sin(del_lat/2)**2 + cos(lat1)*cos(lat2)*sin(del_long/2)**2
    c = 2*asin(sqrt(a))
    dist = R*c
    
    return [time,dist] 

def radius_at_tp(T,P):
    
    #from the ideal gas law ...
    
    return ((3 * n * R_star * T)/(4 * pi * P)) ** (1/3)

def ac_at_tp(temp,press):
    
    balloon_radius = radius_at_tp(temp,press)
    area_unburst = payload_area + pi * (balloon_radius) ** 2
    area_burst = payload_area + parachute_area
    
    return area_burst/area_unburst

def refine_drag_coeff(wind_lower_data,state,winds):
    
    #Use formula to refine C_d http://www.rocketmime.com/rockets/descent.html
    
    global v0
    global C
    
    at = datetime.strptime(state[0], FMT) - datetime.strptime(wind_lower_data[0], FMT)
    actual_time = at.total_seconds()
    
    ind = how_many_bands(winds,state[3])
    
    [estimated_time,_,_,_,v0] = find_bandchange(winds[ind + 1],v0)
    
    wind_lower_data = state[:]
    
    alt = state[3]
    rho = density_at_alt(alt)
    D = 2 * 0.3048
    
    #C_new = C * (actual_time/estimated_time)
    
    C_new = 8 * descent_m * g_0 / (pi * rho * v0 ** 2 * D ** 2)
    
    
    if not(C_new > 100 or C_new < 0.5):
        C = C_new
        
    print(wind_lower_data[3],C,C_new,rho,v0)
    
    return wind_lower_data
    