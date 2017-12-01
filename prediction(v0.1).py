import numpy as np
import matplotlib.pyplot as mpl


data = np.genfromtxt('telemetry_test.txt',delimiter=',',skip_header=1)


latitudes = data[:,][:,3]
longitudes = data[:,][:,4]
altitudes = data[:,][:,5]
speeds = data[:,][:,6]
headings = data[:,][:,7]



#with open('telemetry_test.csv') as csvfile:   
#    while True:   
#        for line in csvfile:
#            print(line)
#        time.sleep(1)
    
    #telem = list(csv.reader(csvfile))

#telemetry = [];

#for i in range(0,len(telem)):
#    telemetry.append(telem[i][0].split(','))
    
    