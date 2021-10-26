from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib import dates
from .config import FMT
from enum import Enum
import pandas as pd
import numpy as np
import os 


class Analyser:
    
    data: pd.DataFrame

    def __init__(self, callsign, telemetry_file, parameter_file, column_descriptors):

        self.callsign = callsign
        self.telemetry_file = os.path.abspath(telemetry_file)
        self.parameter_file = os.path.abspath(parameter_file)
        self.header, self.formatter_funcs = zip(*column_descriptors)
        self.columns = Enum('columns', self.header, start=0)

        self.get_data()
        
    def get_data(self):

        data_list = []

        with open(self.telemetry_file, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith("$$"):
                    if line.find(self.callsign) != -1:
                        read_line = self.read_line(line)
                        if read_line[self.columns.LATITUDE] != 0.0:
                            data_list.append(read_line)

        self.data = pd.DataFrame(data_list)

    def read_line(self, ln):
        d = OrderedDict()
        ln_list = ln.split(',')

        for k, item in self.columns.__members__.items():
            func = self.formatter_funcs[item.value]
            d[item] = func(ln_list[item.value])

        return d

    def find_launch(self):
        altitudes = self.data[self.columns.ALTITUDE]
        return np.argmax(altitudes > altitudes[0] + 50)

    def find_landing_idx(self):
        altitudes = self.data[self.columns.ALTITUDE]
        burst_idx = self.find_burst_idx()
        first_altitude = altitudes[0]
        indices = np.multiply(
            abs(altitudes - first_altitude) < 500,
            np.array(range(len(altitudes))) > burst_idx
        )
        return np.argmax(indices)

    def find_burst_idx(self):
        altitudes = self.data[self.columns.ALTITUDE]
        return np.argmax(altitudes)

    @staticmethod
    def format_axis(axis_obj):
        fmt = dates.DateFormatter(FMT)
        axis_obj.xaxis.set_major_formatter(fmt)
        axis_obj.tick_params(axis='x', labelrotation=90, labelsize=7)

    def plot(self):

        # Find the three major points of the launch
        launch_idx = self.find_launch()
        burst_idx = self.find_burst_idx()
        landing_idx = self.find_landing_idx()

        #
        x = self.data[self.columns.LATITUDE]
        y = self.data[self.columns.LONGITUDE]
        z = self.data[self.columns.ALTITUDE]
        times = self.data[self.columns.TIME]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(x, y, z)

        ax.plot(x[0], y[0], z[0], 'go', label=f"Start ({times[0].time()})")

        # Plot launch
        ax.plot(x[launch_idx],
                y[launch_idx],
                z[launch_idx], 'kx', label=f"Launch ({times[launch_idx].time()})")

        # Plot burst point

        ax.plot(x[burst_idx], y[burst_idx], z[burst_idx], 'r*',
                label=f"Burst ({times[burst_idx].time()})")

        # Plot landing
        ax.plot(x[landing_idx],
                y[landing_idx],
                z[landing_idx], 'kD', label=f"Landing ({times[landing_idx].time()})")

        ax.plot(x.iloc[-1], y.iloc[-1], z.iloc[-1], 'y.', label=f"End ({times.iloc[-1].time()})")

        plt.legend()
        fig.savefig("1.png")

        fig2, ax2 = plt.subplots(2, 3, squeeze=False)

        #
        ax2[0, 0].plot(x, y)
        ax2[0, 0].plot(x[burst_idx], y[burst_idx], 'r*')
        ax2[0, 0].plot(x[landing_idx], y[landing_idx], 'kD')
        ax2[0, 0].plot(x[launch_idx], y[launch_idx], 'kx')

        #
        ax2[0, 1].plot(x, z)
        ax2[0, 1].plot(x[burst_idx], z[burst_idx], 'r*')
        ax2[0, 1].plot(x[landing_idx], z[landing_idx], 'kD')
        ax2[0, 1].plot(x[launch_idx], z[launch_idx], 'kx')

        #
        ax2[0, 2].plot(y, z)
        ax2[0, 2].plot(y[burst_idx], z[burst_idx], 'r*')
        ax2[0, 2].plot(y[landing_idx], z[landing_idx], 'kD')
        ax2[0, 2].plot(y[launch_idx], z[launch_idx], 'kx')

        #
        ax2[1, 0].plot(times, z)
        ax2[1, 0].plot(times[burst_idx], z[burst_idx], 'r*')
        ax2[1, 0].axvline(x=times[landing_idx], color="k", alpha=0.6)
        ax2[1, 0].axvline(x=times[launch_idx], color="k", alpha=0.6)
        self.format_axis(ax2[1, 0])

        #
        ax2[1, 1].plot(times, x)
        ax2[1, 1].plot(times[burst_idx], x[burst_idx], 'r*')
        ax2[1, 1].axvline(x=times[landing_idx], color="k", alpha=0.6)
        ax2[1, 1].axvline(x=times[launch_idx], color="k", alpha=0.6)
        self.format_axis(ax2[1, 1])

        #
        ax2[1, 2].plot(times, y)
        ax2[1, 2].plot(times[burst_idx], y[burst_idx], 'r*')
        ax2[1, 2].axvline(x=times[landing_idx], color="k", alpha=0.6)
        ax2[1, 2].axvline(x=times[launch_idx], color="k", alpha=0.6)
        self.format_axis(ax2[1, 2])

        fig2.tight_layout()
        fig2.savefig("2.png")
