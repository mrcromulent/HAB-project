# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 12:40:18 2018

@author: Pierre
"""

##HAB-LPR Configuration file

#Algorithm parameters
fp = 'YERRALOON1_DATA//telemetry.txt'
output_filepath = 'prediction.txt'
callsign = '$$YERRA' 
wind_band_width = 100
sleep_time = 0.001
prediction_gap = 0.05

#Launch parameters
pay_m = 1.8 #kg
#pay_m = 1
bal_m = 1.2 #kg
balloon_volume = 4 # calculated using V = 4/3 * pi * (1.5/2)^2, for a measurediameter of 1.5 m
M_gas = 0.004 #molar mass of helium, kg/mol
parachute_diameter = 1.2192 #m
payload_area = 0.3 * 0.3
##DRAG COEFFICIENTS
C = 0.44 
#C = 2

##TELEMETRY FORMAT
#Expected telemetry format is CALLSIGN,PACKET_NO,TIME,LAT,LONG,ALT,SPEED,HEADING,NO_SATELLITES,
#INTERNAL_TEMP,EXTERNAL_TEMP,PRESSURE,HUMIDITY*CHECKSUM

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