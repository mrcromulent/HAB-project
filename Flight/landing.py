# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 08:59:41 2017

@author: Pierre
"""

from math import exp, pi, sqrt, sin, cos, asin, radians
from datetime import datetime
from config import bal_m,pay_m,output_filepath,C,parachute_diameter,payload_area,balloon_volume
FMT = '%H:%M:%S' #datetime format

##PHYSICAL CONSTANTS

g = 9.80665 # m/s^2
R = 8.3144598 #gas constant, m^3 Pa/ K / mol
M_air = 0.0289644 #molar mass of air, kg/mol
earth_radius = 6371 #km. Earth radius

##BALLOON PARAMETERS
parachute_area = 2 * pi * (parachute_diameter/2) ** 2  
area_burst = parachute_area + payload_area
descent_m = pay_m + 0.05 * bal_m #Descent mass, kg

#VELOCITY-TRACKING VARIABLE
v0_global = 0


#DENSITY AND DRAG FUNCTIONS
    
def density_at_alt(alt):
    """"Returns air density in kg/m^3 as a function of altitude above mean 
    sea level (given in m). Density computed using Barometric Formula, 
    available at https://en.wikipedia.org/wiki/Barometric_formula"""
    
    if 0 <= alt < 11000: #Troposphere
        p_b = 1.2250
        T_b = 288.15
        L_b = -0.0065
        h_b = 0
        
    elif 11000 <= alt < 20000: #Stratosphere1
        p_b = 0.36391
        T_b = 216.65
        L_b = 0
        h_b = 11000
        
    elif 20000 <= alt < 32000: #Stratosphere2
        p_b = 0.08803
        T_b = 216.65
        L_b = 0.001
        h_b = 20000
        
    elif 32000 <= alt < 47000: #Stratosphere3
        p_b = 0.01322
        T_b = 288.65
        L_b = 0.0028
        h_b = 32000
        
    #Apply the correct formula based on the value of the Lapse Rate, L_b
        
    if L_b != 0:
        
        fraction = T_b / (T_b + L_b*(alt - h_b))
        exponent = 1 + (g * M_air)/(R * L_b)
        
        return p_b * (fraction) ** exponent
    
    if L_b == 0:
        exponent = (-g * M_air * (alt - h_b))/(R * T_b)
        
        return p_b * exp(exponent)    


def drag_at_alt(alt,descent_rate):
    """drag_at_alt applies the drag formula: 
        F_drag = 1/2 * Coefficient_drag * density * velocity^2 * Area"""
    
    rho = density_at_alt(alt)
    
    return 0.5 * C * rho * descent_rate ** 2 * parachute_area 


def refine_drag_calculation(state):
    """This function refines the value of the drag coefficient using the 
    v0_global and an estimation of the current terminal velocity. 
    refine_drag_calculation() calls find_C()."""
    
    global C
    
    #Extract the current altitude and find terminal velocity

    alt = state[3]
    v_terminal = find_terminal_velocity(alt)
    
    #Check if the current velocity is within a sensible range of v_terminal. 
    #If so, C becomes the average of the two
    
    if abs(v0_global - v_terminal) < 10:
        C = 1/2 * (C + find_C(v0_global,alt))
        
        
def find_C(descent_rate,alt):
    """find_C() returns a new coefficient of drag for a non-zero descent_rate,
    assuming that the payload is falling at terminal velocity"""
    
    rho = density_at_alt(alt)
    
    if not(descent_rate == 0):
        return (descent_m * g)/(0.5 * rho * descent_rate ** 2 * parachute_area)
    
    else:
        return C


#TEMPERATURE/PRESSURE FUNCTIONS
    
def temp_press_at_alt(alt):
    """This function returns the temperature (in Kelvin) and pressure (in Pa) 
    at any given altitude, as determined by the formula given at:
    https://www.grc.nasa.gov/www/k-12/rocket/atmosmet.html"""
    
    if 0 <= alt < 11000:
        P_b = 101325 #Pa
        T_b = 288.15 #K
        L_b = -0.0065
        h_b = 0
        
    elif 11000 <= alt < 20000:
        P_b = 22632.10
        T_b = 216.65
        L_b = 0
        h_b = 11000
        
    elif 20000 <= alt < 32000:
        P_b = 5474.89
        T_b = 216.65
        L_b = 0.001
        h_b = 20000
        
    elif 32000 <= alt < 47000:
        P_b = 868.02
        T_b = 288.65
        L_b = 0.0028
        h_b = 32000
        
    #Apply the correct formula based on the lapse rate, L_b
        
    if L_b != 0:
        
        fraction = T_b / (T_b + L_b*(alt - h_b))
        exponent = (g * M_air)/(R * L_b)
        
        P = P_b * (fraction) ** exponent
        
        return [T_b,P]
    
    if L_b == 0:
        exponent = (-g * M_air * (alt - h_b))/(R * T_b)
        
        P = P_b * exp(exponent)
        
        return [T_b,P]


def radius_at_tp(T,P):  
    """Finds the radius of the balloon as a function of the external 
    temperature and pressure, T and P, using the Ideal Gas Law: 
        PV = nRT. T is expected in Kelvin and P in Pascals."""
    
    #from the ideal gas law ...
    
    return ((3 * n * R * T)/(4 * pi * P)) ** (1/3)

def ac_at_tp(temp,press):
    """ac_at_alt() finds the 'area correction' (defined as the ratio of
    the balloon-payload system after and before bursting) as a function
    of the external temperature and pressure. Temperature is expected 
    in Kelvin and Pressure in Pascal."""
    
    balloon_radius = radius_at_tp(temp,press)
    
    #Find the unburst area and return the ratio
    
    area_unburst = payload_area + pi * (balloon_radius) ** 2
    
    return area_burst/area_unburst

def find_gas_n(start_temp,start_pres):
    """find_gas_n() finds the number of mols of gas in the balloon using the
    starting temperature (K), pressure (Pa) and volume (m^3) and the Ideal
    Gas Law."""
    
    global n
    
    n = (start_pres * balloon_volume / (R * start_temp))
    
    
#SPEED FUNCTIONS

def refine_speed(state,speed_state):
    """This function refines the value of the globally-defined v0_global by
    making a distance/time calculation using its current state and the last
    time it checked (i.e. the speed state)"""
    
    global v0_global
    
    #find the distance and time taken between now and the last windband
    
    alt = state[3]
    
    at = datetime.strptime(state[0], FMT) - datetime.strptime(speed_state[0], FMT)
    actual_time = at.total_seconds()
    dist = alt - speed_state[3]
    
    #If time has elapsed, take v0_global as distance/time
    
    if not(actual_time == 0):
        v0_global = dist/actual_time

    #reset speed_state as the current state and return it
                
    speed_state = state[:]
    
    return speed_state

def find_terminal_velocity(alt):
    """This function finds the terminal velocity at a specific altitude 
    assuming terminal velocity. alt is expected in m."""
    
    rho = density_at_alt(alt)
    
    return -1*sqrt(descent_m * g / (0.5 * C * rho * parachute_area))


#LANDING-PREDICTION FUNCTIONS
    
def how_many_bands(winds,alt):
    """Uses a loop to return the index of the first windband entirely 
    above alt. If none exist, the last index is returned."""
    for i in range(0,len(winds)):
        if winds[i][1] > alt:
            return i

    return len(winds)

def find_bandchange(windband,v0):
    """find_bandchange finds the change in latitude, longitude and altitude
    and velocity of the falling payload over a single windband by 
    iterating through kinematic equations on 1000 band_sections."""
    
    #extract data from the windband
    
    [alt_lower,alt_upper,dLat_dt,dLong_dt,_,_,_] = windband[:]
    
    bandwidth =  alt_upper - alt_lower
    
    #split the windband into 1000 band_sections...
    
    band_section = -0.001 * bandwidth
    
    #Initialise variables to track altitude and time spent
    
    sum_t = 0
    alti = alt_upper
    
    for i in range (0,1000):
        
        F_drag = drag_at_alt(alti,v0)
        
        #Apply the kinematic equations

        a = 1/descent_m * (F_drag - descent_m*g)
        dt = (-v0 - sqrt(v0 ** 2 + 2 * a * band_section))/a
        
        #iterate up the time sum, altitude and velocity        
        
        sum_t += dt
        alti += band_section
        v0 = v0 + a * dt
    
    #find the bandchange by multiplying the rate of change of latitude ...
    #and longitude by the total time spent, sum_t
    
    delta_lat = dLat_dt * sum_t
    delta_long = dLong_dt * sum_t
    
    return [sum_t,delta_lat,delta_long,alt_lower,v0]


def splat(state,winds):
    """Predicts the landing site by identifying the current altitude 
    (from state) and applying the find_bandchange() function iteratively
    to all lower windbands. The results of find_bandchange() are added to
    the current latitude and longitude and these new values are fed back
    into find_bandchange(). splat() also writes the prediction to the 
    output .txt file."""
    
    #extract the relevant quantities from the arguments
    
    [time,lat,long,alt,speed,heading] = state[0:6]
    
    #Override the speed from the Raspberri Pi with our best 
    #speed estimate from the descent data
    
    speed = v0_global
    
    #find the number of bands below the payload, at alt
    
    num_bands = how_many_bands(winds,alt)
    
    #call find_bandchange on each band (starting with the highest band) and 
    #finishing at the lowest.
    
    for i in range(num_bands-1,-1,-1):
        
        #Iterate through find_bandchange
        
        [_,delta_lat,delta_long,new_alt,new_speed] = find_bandchange(winds[i],speed)
        
        lat = lat + delta_lat
        long = long + delta_long
        speed = new_speed
        
    #write the results to the prediction file and return the current precition
        
    with open(output_filepath,'a') as h:
        h.write(str(round(lat,6)) + ',' + str(round(long,6)) + '\n')
    
    return (lat,long)
            

#DISTANCE FUNCTIONS

def how_far(time,prediction,lat2 = -34.37435, long2 = 147.859):
    """how_far() returns the distance (in km) between any two points of 
    latitude and longitude using the Haversine Formula (see 
    https://www.movable-type.co.uk/scripts/latlong.html). The function
    expects prediction as a list of the form [lat,long] and time as a
    string. lat2 and long2 have default values as the actual landing
    coordinates of YERRALOON1."""
    
    #Extract the latitude and longitude from prediction 
    
    [lat1,long1] = prediction[:]
    
    #Convert to radians
    
    del_lat = radians(lat1 - lat2)
    del_long = radians(long1 - long2)

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    
    #Apply the Haversine Formula
    
    a = sin(del_lat/2)**2 + cos(lat1)*cos(lat2)*sin(del_long/2)**2
    c = 2*asin(sqrt(a))
    dist = earth_radius*c
    
    return [time,dist] 
