import csv
import os
import numpy

with open('telemetry_test.csv', 'rb') as csvfile:
    telem = list(csv.reader(csvfile))

telemetry = [];

for i in range(0,len(telem)):
    telemetry.append(telem[i][0].split(','))
