# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time as t
import landing
import other_commands as oc
import wind
import how_far as hf

fp = 'test.txt'
#fp = 'YERRALOON1_DATA\\telemetry.txt'

#Quantities
rising = False
telemetry = []
winds = []
wind_band_width = 100
sleep_time = 0.001 #seconds
prediction_gap = 0.01 #seconds
the_time = 0

start_time = '00:00:00'
start_lat = 0.0
start_long = 0.0
start_elev = 0.0

#check if the file has any data written to it. If not, wait sleep_time seconds and try again
while oc.file_empty(fp):
    print('Telemetry file empty or non-existant')
    t.sleep(sleep_time)

#Record the position and time of the launch site. This
while start_time == '00:00:00' or start_lat == 0.0 or start_long == 0.0 or start_elev == 0.0:
    print('Waiting for launch site values')
    t.sleep(sleep_time)
    (start_time,start_lat,start_long,start_elev) = oc.record_launch_values(fp)
    
#MAIN LOOP
    
predictions_made = 0

while True:
    
    #add a new line to the telemetry list
    
    new_telemetry = oc.add_telemetry(fp)
    
    #extract current values of the important quantities
        
    time = new_telemetry[2]
    lat = new_telemetry[3]
    long = new_telemetry[4]
    alt = new_telemetry[5]
    speed = new_telemetry[6]
    heading = new_telemetry[7]
        
    #Detect when the balloon has started to lift off, set the lower wind band data
    if rising == False and (alt - start_elev) > 100:
        rising = True
        wind_lower_data = [time,lat,long,alt,speed,heading]
            
    if rising == True:
        
        telemetry.append(new_telemetry)
        
        #If a band has been crossed ...
        if (alt - wind_lower_data[3]) >= wind_band_width:
            
            #wind.make_new_band
            
            # ... record the current data
            wind_upper_data = [time,lat,long,alt,speed,heading]
            
            #calculate the windspeeds (in deg/s) and add it to the list
            new_wind = wind.calc_windspeed(wind_lower_data,wind_upper_data)
            winds.append(new_wind)
            
            #reset the lower band data
            wind_lower_data = wind_upper_data[:]
            
        #predict the landing site
        
        if (t.time() - the_time) >= prediction_gap:
            #this prediction needs to happen less often
            (lat1,long1) = landing.splat(lat,long,alt,speed,heading,winds)
            predictions_made += 1
            the_time = t.time()
            
            landing.how_far(lat1,long1,time)
        
            #Find some way to transmit prediction?
        
    if len(telemetry) > 6000: #flight must be over by now (10000 might be needed for longer flights)
        break
        
    #put the code to sleep until new data is expected
    t.sleep(sleep_time)
    