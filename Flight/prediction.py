# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time as t
import landing
import other_commands as oc
import wind
from config import fp,wind_band_width,sleep_time,prediction_gap

##QUANTITIES
rising = False
falling = False
speed_state = []
telemetry = []
winds = []
last_prediction_time = 0

##SETUP

try:

    #Check if the file has any data written to it. If not, wait sleep_time seconds and try again.
    while oc.file_empty(fp):
        t.sleep(sleep_time)
    
    #Record the position and time of the launch site, ignoring false telemetry
    while oc.false_telemetry(fp):
        t.sleep(sleep_time)
    
    #Assign variables to the start values and calculate the number of mols of gas
    (start_time,start_lat,start_long,start_elev,start_temp,start_pres) = oc.record_launch_values(fp)
    landing.find_gas_n(start_temp,start_pres)
    
except:
    pass

##MAIN LOOP
    
while True:
     
    try:
    
        #Record the start time of this loop
        loop_start = t.time()
        
        #Add a new line to the telemetry list    
        new_telemetry = oc.add_telemetry(fp)
        
        #Extract the the current altitude and state (state = [time,lat,long,alt,speed,heading,temp_ext,press,humidity])
        state = new_telemetry[2:8] + new_telemetry[10:13]
        alt = new_telemetry[5]
        
        #Detect when the balloon has started to lift off; set the lower wind band data
        
        if rising == False and (alt - start_elev) > -1:
            rising = True
            wind_lower_data = state[:]
                
        if rising == True:
            
            #Add the new telemetry to the list of telemetry
            telemetry.append(new_telemetry)
            
            #Refine the speed calculation
            if falling == True: 
                speed_state = landing.refine_speed(state,speed_state)
            
            #If a wind band has been crossed ...
            
            if (alt - wind_lower_data[3]) >= wind_band_width:
                #...Make a new wind band if rising
                [winds,wind_lower_data] = wind.make_new_band(state,wind_lower_data,winds)
            
            elif (wind_lower_data[3] - alt) >= wind_band_width:
                #...Or refine the drag calculation if falling
                landing.refine_drag_calculation(state)
                
                #Start tracking descent speed
                if falling == False:
                    speed_state = state[:]
                    falling = True
                    
            
            #If sufficient time has passed, predict the landing site using splat
            
            if (t.time() - last_prediction_time) >= prediction_gap:
                
                prediction = landing.splat(state,winds)
                last_prediction_time = t.time()
                
        
        #Check how long the loop took to execute. Put the code to sleep if necessary.
        
        calc_time = t.time() - loop_start
        

        
        if calc_time < sleep_time:
        
            t.sleep(sleep_time - calc_time)
            

        
    except: #Failsafe. If any errors occur, the program exits
        break
