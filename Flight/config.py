# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 12:40:18 2018

@author: Pierre
"""

##HAB-LPR Configuration file

#Algorithm parameters
fp = '/home/pi/pits/tracker/telemetry.txt'
output_filepath = '/home/pi/pierre/Flight/pierre_prediction.csv'
callsign = '$$YERRA' 
wind_band_width = 100 #m
sleep_time = 1 #s (usually 1)
prediction_gap = 90 #s (usually 90)


#Launch parameters
pay_m = 1.8 #kg
bal_m = 1.2 #kg
balloon_volume = 4 #m^3
M_gas = 0.004 #molar mass of helium, kg/mol
parachute_diameter = 1.2192 #4 ft in m
payload_area = 0.3 * 0.3 #m^2


#Parachute Drag Coefficient
C = 0.5


##TELEMETRY FORMAT
#Expected telemetry format is CALLSIGN,PACKET_NO,TIME,LAT,LONG,ALT,SPEED,HEADING,NO_SATELLITES,
#INTERNAL_TEMP,EXTERNAL_TEMP,PRESSURE,HUMIDITY*CHECKSUM

#Data not included should be saved as the string 'NI' (THIS FUNCTIONALITY IS NOT YET IMPLEMENTED)

callsign_index = 0
packet_index = 1
time_index = 2
lat_index = 3
long_index = 4
alt_index = 5
speed_index = 6
heading_index = 7
satellites_index = 8
internal_index = 9
external_index = 10
pressure_index = 11
hum_check_index = 12