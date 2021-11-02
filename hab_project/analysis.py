from hab_project.definitions import FMT, LAUNCH_THRESHOLD, LANDING_THRESHOLD
from hab_project.physics import haversine_distance
from hab_project.predictor import State
import matplotlib.pyplot as plt
from matplotlib import dates
import pandas as pd
import pickle as pk
import numpy as np
import os

import matplotlib.cm as cm


def format_axis(axis_obj):
    fmt = dates.DateFormatter(FMT)
    axis_obj.xaxis.set_major_formatter(fmt)
    axis_obj.tick_params(axis='x', labelrotation=90, labelsize=7)


class Analyser:
    data: pd.DataFrame
    prediction_error = []
    prediction_times = []
    predictions = []
    vert_speed = []
    speed_time = []

    ack_fp = None

    def __init__(self, p, ls, ack_fp=None):
        self.predictor = p
        self.landing_site = ls
        self.ack_fp = ack_fp

        self.analyse()

    def analyse(self):

        data_list = []
        self.predictor.telem.wait_for_telemetry()

        while self.predictor.state != State.LANDED:
            self.predictor.main_loop_iter()

            if self.predictor.curr_line is not None:
                data_list.append(self.predictor.curr_line)

            # Estimate errors
            self.estimate_vertical_speed()
            self.estimate_prediction_error()

        #
        self.data = pd.DataFrame(data_list)

    def estimate_vertical_speed(self):
        if self.predictor.curr_line is not None:
            # Estimate the current vertical speed
            alts = []
            for item in self.predictor.memory:
                alts.append(item[self.predictor.cols.ALTITUDE])
            if len(alts) > 1:
                self.vert_speed.append(np.mean(np.diff(alts)))
                curr_time = self.predictor.get_curr_time()
                self.speed_time.append(curr_time)

    def estimate_prediction_error(self):
        if len(self.predictor.last_prediction) > 0:
            ls = self.landing_site
            ps = self.predictor.last_prediction
            self.predictions.append(ps)
            self.prediction_error.append(haversine_distance(ps, ls))
            curr_time = self.predictor.get_curr_time()
            self.prediction_times.append(curr_time)

    def find_launch(self):
        altitudes = self.data[self.predictor.cols.ALTITUDE]
        return np.argmax(altitudes > altitudes[0] + LAUNCH_THRESHOLD)

    def find_landing_idx(self):
        altitudes = self.data[self.predictor.cols.ALTITUDE]
        burst_idx = self.find_burst_idx()
        first_altitude = altitudes[0]
        indices = np.multiply(
            abs(altitudes - first_altitude) < 600,
            np.array(range(len(altitudes))) > burst_idx
        )
        return np.argmax(indices)

    def find_burst_idx(self):
        altitudes = self.data[self.predictor.cols.ALTITUDE]
        return np.argmax(altitudes)

    def plot_ackerman_prediction(self, ax):

        date_repr = self.predictor.telem.formatter_funcs[self.predictor.cols.TIME.value]

        with open(self.ack_fp, "rb") as fp:
            ack_pred = pk.load(fp)

        times = []
        error = []
        for i in range(0, len(ack_pred), 20):
            line_i = ack_pred[i]
            prediction = float(line_i[3]), float(line_i[4])
            error.append(haversine_distance(prediction, self.landing_site))
            times.append(date_repr(line_i[2]))

        ax.plot(times, error)

    def plot_prediction_error(self):

        fig, ax = plt.subplots()
        ax.plot(self.prediction_times, self.prediction_error)
        if self.ack_fp is not None:
            self.plot_ackerman_prediction(ax)

        format_axis(ax)
        fig.show()

    def plot_prediction_error2(self):

        date_repr = self.predictor.telem.formatter_funcs[self.predictor.cols.TIME.value]

        with open(self.ack_fp, "rb") as fp:
            ack_pred = pk.load(fp)

        times = []
        error = []
        ack = []
        for i in range(0, len(ack_pred), 20):
            line_i = ack_pred[i]
            prediction = float(line_i[3]), float(line_i[4])
            ack.append(prediction)
            error.append(haversine_distance(prediction, self.landing_site))
            times.append(date_repr(line_i[2]))

        x = self.data[self.predictor.cols.LATITUDE]
        y = self.data[self.predictor.cols.LONGITUDE]
        v = self.data[self.predictor.cols.SPEED]
        heads = self.data[self.predictor.cols.HEADING] * np.pi / 180
        predictions = np.array(self.predictions)
        ack_pred = np.array(ack)
        burst_idx = self.find_burst_idx()

        n = 20

        fig, ax = plt.subplots()
        # ax.plot(x, y, 'k.')
        # ax.quiver(x[::n], y[::n], (v * np.cos(heads))[::n], (v * np.sin(heads))[::n], scale=3000, color='green')
        ax.plot(self.landing_site[0], self.landing_site[1], 'kx')
        ax.plot(x[burst_idx], y[burst_idx], 'r*')

        xs = predictions[:, 0]
        ys = predictions[:, 1]
        colors = cm.rainbow(np.linspace(0, 1, len(ys)))
        colors2 = cm.jet(np.linspace(0, 1, len(ack_pred[:, 0])))

        plt.scatter(xs, ys, color=colors, s=0.9)
        plt.scatter(ack_pred[:, 0], ack_pred[:, 1], color=colors2, s=0.5)


        fig.show()

    def plot_vert_speed(self):

        fig, ax = plt.subplots()
        ax.plot(self.speed_time, self.vert_speed)
        format_axis(ax)
        fig.show()

    def plot(self):

        # Find the three major points of the launch
        launch_idx = self.find_launch()
        burst_idx = self.find_burst_idx()
        landing_idx = self.find_landing_idx()

        #
        x = self.data[self.predictor.cols.LATITUDE]
        y = self.data[self.predictor.cols.LONGITUDE]
        z = self.data[self.predictor.cols.ALTITUDE]
        times = self.data[self.predictor.cols.TIME]


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
        fig.show()

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
        format_axis(ax2[1, 0])

        #
        ax2[1, 1].plot(times, x)
        ax2[1, 1].plot(times[burst_idx], x[burst_idx], 'r*')
        ax2[1, 1].axvline(x=times[landing_idx], color="k", alpha=0.6)
        ax2[1, 1].axvline(x=times[launch_idx], color="k", alpha=0.6)
        format_axis(ax2[1, 1])

        #
        ax2[1, 2].plot(times, y)
        ax2[1, 2].plot(times[burst_idx], y[burst_idx], 'r*')
        ax2[1, 2].axvline(x=times[landing_idx], color="k", alpha=0.6)
        ax2[1, 2].axvline(x=times[launch_idx], color="k", alpha=0.6)
        format_axis(ax2[1, 2])

        fig2.tight_layout()
        fig2.show()


def main2():

    from datetime import datetime, timedelta
    from hab_project.definitions import DATA_DIR
    from hab_project.telemetry import Telemetry
    from hab_project.balloon import Balloon
    from hab_project.predictor import Predictor

    def date_repr(date):
        # 2018 01 17 Wed 2:48 PM GMT + 11
        return datetime.combine(datetime(2018, 1, 17), datetime.strptime(date, FMT).time()) + timedelta(hours=11)

    tf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "telemetry.txt")
    pf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "param.yaml")
    ack_fp = "../data/YERRALOON2_DATA/ackerman_pred.obj"
    landing_site = (-34.31743, 148.73291)
    of = "prediction.txt"
    callsign = "YERRA"

    headers = \
        [
            ('CALLSIGN', str),
            ('PACKET', int),
            ('TIME', date_repr),
            ('LATITUDE', float),
            ('LONGITUDE', float),
            ('ALTITUDE', float),
            ('SPEED', float),
            ('HEADING', float),
            ('SATELLITES', int),
            ('INTERNAL_TEMP', float),
            ('EXTERNAL_TEMP', float),
            ('PRESSURE', float),
            ('HUMIDITY', float),
            ('PRED_LAT', float),
            ('PRED_LON', lambda s: float(s.split('*')[0]))
        ]

    telem = Telemetry(tf, headers, callsign)
    balloon = Balloon(pf)
    predictor = Predictor(telem, balloon, of)
    anal = Analyser(predictor, landing_site, ack_fp=ack_fp)
    anal.plot_prediction_error()
    # anal.plot_prediction_error2()
    # anal.plot_vert_speed()
    # anal.plot()


def main1():

    from datetime import datetime, timedelta
    from hab_project.definitions import DATA_DIR
    from hab_project.telemetry import Telemetry
    from hab_project.balloon import Balloon
    from hab_project.predictor import Predictor

    launch_time = datetime.combine(
        datetime(2017, 12, 5),
        datetime.strptime("22:59:40", FMT).time()
    )

    def date_repr(date):

        dt = datetime.combine(
            datetime(2017, 12, 5),
            datetime.strptime(date, FMT).time()
        )

        if dt < launch_time:
            return dt + timedelta(days=1, hours=11)
        else:
            return dt + timedelta(hours=11)

    tf = os.path.join(DATA_DIR, "YERRALOON1_DATA", "telemetry.txt")
    pf = os.path.join(DATA_DIR, "YERRALOON1_DATA", "param.yaml")
    ack_fp = "../data/YERRALOON1_DATA/ackerman_pred.obj"
    landing_site = (-34.37408, 147.85953)
    of = "prediction.txt"
    callsign = "YERRA"

    headers = [
        ('CALLSIGN', str),
        ('PACKET', int),
        ('TIME', date_repr),
        ('LATITUDE', float),
        ('LONGITUDE', float),
        ('ALTITUDE', float),
        ('SPEED', float),
        ('HEADING', float),
        ('SATELLITES', int),
        ('INTERNAL_TEMP', float),
        ('EXTERNAL_TEMP', float),
        ('PRESSURE', float),
        ('HUMIDITY', lambda s: float(s.split('*')[0])),
    ]

    telem = Telemetry(tf, headers, callsign)
    balloon = Balloon(pf)
    predictor = Predictor(telem, balloon, of)
    anal = Analyser(predictor, landing_site, ack_fp=ack_fp)

    anal.plot_prediction_error()
    # anal.plot_prediction_error2()
    # anal.plot_vert_speed()
    # anal.plot()


if __name__ == "__main__":
    # main2()
    main1()
