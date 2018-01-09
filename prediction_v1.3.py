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

################################################
import pickle
import matplotlib.pyplot as plt
import numpy as np

how_far_list = []
times_list = []
predictions_made = 0
calc_times = []
#################################################

##QUANTITIES
rising = False
telemetry = []
winds = []
last_prediction_time = 0
telemetry_cutoff = 2000; #lines of $$YERRA telemetry before the program exits


##SETUP

#Check if the file has any data written to it. If not, wait sleep_time seconds and try again.
while oc.file_empty(fp):
    print('Telemetry file empty or non-existant.')
    t.sleep(sleep_time)

#Record the position and time of the launch site, ignoring false telemetry
while oc.false_telemetry(fp):
    print('Waiting for launch site values. Ignoring false telemetry.')
    t.sleep(sleep_time)

#Assign variables to the start values and calculate the number of mols of gas
(start_time,start_lat,start_long,start_elev,start_temp,start_pres) = oc.record_launch_values(fp)
landing.find_gas_n(start_temp,start_pres)
    

##MAIN LOOP

while len(telemetry) < telemetry_cutoff:
    
#    try:
    
        #Record the start time of this loop
        loop_start = t.time()
        
        #Add a new line to the telemetry list    
        new_telemetry = oc.add_telemetry(fp)
        
        #Extract the the current altitude and state (state = [time,lat,long,alt,speed,heading,temp_ext,press,humidity])
        state = new_telemetry[2:8] + new_telemetry[10:13]
        alt = new_telemetry[5]
        
        #Detect when the balloon has started to lift off; set the lower wind band data
        if rising == False and (alt - start_elev) > 100:
            rising = True
            wind_lower_data = state[:]
                
        if rising == True:
            
            #Add the new telemetry to the list of telemetry
            telemetry.append(new_telemetry)
            
            #If a wind band has been crossed ...
            
            if (alt - wind_lower_data[3]) >= wind_band_width:
                #...Make a new wind band if rising
                [winds,wind_lower_data] = wind.make_new_band(state,wind_lower_data,winds)
            
#            elif (wind_lower_data[3] - alt) >= wind_band_width:
#                #...Or refine the drag calculation if falling
#                wind_lower_data = landing.refine_drag_calculation(wind_lower_data,state)
                
                
            #If sufficient time has passed, predict the landing site using splat
            
            if (t.time() - last_prediction_time) >= prediction_gap:
                
                prediction = landing.splat(state,winds)
                last_prediction_time = t.time()
                
                #################################################
                how_far_list.append(landing.how_far(prediction,state[0])[1])
                times_list.append(landing.how_far(prediction,state[0])[0])
                predictions_made += 1
                ##################################################
        
        #Check how long the loop took to execute. Put the code to sleep if necessary.
        
        calc_time = t.time() - loop_start
        
    ###################################################
        calc_times.append(calc_time)        
    ######################################################
        
        if calc_time < sleep_time:
        
            t.sleep(sleep_time - calc_time)
        
#    except: #Failsafe. If any errors occur, the program exits
#        break
        
##############################################################
        
with open("ackerman_pred.obj", "rb") as fp:
    ack_pred = pickle.load(fp)
    
how_far_ack = []
prediction_ack_no = 0

for i in range(0,len(ack_pred),20):
    prediction  = [float(ack_pred[i][3]),float(ack_pred[i][4])]
    time = ack_pred[i][2]
    ackerman_prediction = landing.how_far(prediction,time)
    how_far_ack.append(ackerman_prediction[1])
    prediction_ack_no += 1

y = np.linspace(0,130,prediction_ack_no)
x = np.linspace(0,130,predictions_made)
plt.xticks(x,times_list,rotation = 'vertical')
plt.plot(x,how_far_list)
plt.ylabel('Error in landing site prediction [km]')
plt.xlabel('Time [GMT, equivalent to AEDT - 11]')
plt.plot(y,how_far_ack)
plt.show()
a = sorted(calc_times,reverse = True)
a2 = [i for i in a if i > 0]
max_calc = a2[0]
av_calc = sum(a2)/len(a2)
###############################################################