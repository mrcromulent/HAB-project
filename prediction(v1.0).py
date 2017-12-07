# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:05:27 2017

@author: Pierre
"""

import time as t
import landing
import other_commands as oc
import wind

fp = 'test.txt'
rising = False
telemetry = []
winds = []
wind_band_width = 100
sleep_time = 2 #normally 12

#check if the file has any data written to it. If not, wait 12 seconds and try again
while oc.file_empty(fp):
    print('Telemetry file empty or non-existant')
    t.sleep(sleep_time)

#record launch site values, taken as the second row of the .txt file

(start_time,start_lat,start_long,start_elev) = oc.record_launch_values(fp)

#MAIN LOOP

while True:
    
    #add a new line to the telemetry list
    
    new_telemetry = oc.add_telemetry(fp)
    telemetry.append(new_telemetry)
    
    #print(telemetry)
    
    #extract current values of the important quantities
        
    time = new_telemetry[2]
    lat = new_telemetry[3]
    long = new_telemetry[4]
    alt = new_telemetry[5]
    speed = new_telemetry[6]
    heading = new_telemetry[7]
        
    #Detect when the balloon has started to lift off, set the lower wind band data
    if rising == False and (alt - start_elev) > 10:
        rising = True
        wind_lower_data = [time,lat,long,alt,speed,heading]
            
    if rising == True:
        
        #If a band has been crossed ...
        if (alt - wind_lower_data[3]) >= wind_band_width:    
            
            # ... record the current data
            wind_upper_data = [time,lat,long,alt,speed,heading]
            
            #calculate the windspeed and add it to the list
            new_wind = wind.calc_windspeed(wind_lower_data,wind_upper_data)

            winds.append(new_wind)
            
            #reset the lower band data
            wind_lower_data = wind_upper_data[:]
            
        #predict the landing site
        prediction = landing.splat(lat,long,alt,speed,heading,winds)
        
        #Find some way to transmit prediction?
        
    #put the code to sleep until new data is expected
    t.sleep(sleep_time)
        

        