from hab_project.physics import primitive_vars_at_altitude
from hab_project.definitions import DATA_DIR, FMT
from hab_project.predictor import Predictor
from hab_project.telemetry import Telemetry
from hab_project.analysis import Analyser
from datetime import datetime, timedelta
from hab_project.balloon import Balloon
import matplotlib.pyplot as plt
import numpy as np
import os


def test_yerraloon2():
    def date_repr(date):
        # 2018 01 17 Wed 2:48 PM GMT + 11
        return datetime.combine(datetime(2018, 1, 17), datetime.strptime(date, FMT).time()) + timedelta(hours=11)

    analyser = Analyser(
        "YERRA",
        os.path.join(DATA_DIR, "YERRALOON2_DATA", "telemetry.txt"),
        os.path.join(DATA_DIR, "YERRALOON2_DATA", "parameter_values.txt"),
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
    )

    analyser.plot()


def test_yerraloon1():
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

    analyser = Analyser(
        "YERRA",
        os.path.join(DATA_DIR, "YERRALOON1_DATA", "telemetry.txt"),
        os.path.join(DATA_DIR, "YERRALOON1_DATA", "parameter_values.txt"),
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
            ('HUMIDITY', lambda s: float(s.split('*')[0])),
        ]
    )

    analyser.plot()


def test_yerraloon1_tracker():
    # Landing location
    # -34.37408, 147.85953

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
    tracker = Predictor(telem, balloon, of)
    tracker.run()
    tracker.plot_prediction_error()


def test_yerraloon2_tracker():
    # Landing Location:
    # -34.31743, 148.73291

    def date_repr(date):
        # 2018 01 17 Wed 2:48 PM GMT + 11
        return datetime.combine(datetime(2018, 1, 17), datetime.strptime(date, FMT).time()) + timedelta(hours=11)

    tf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "telemetry.txt")
    pf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "param.yaml")
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
    tracker = Predictor(telem, balloon, of)
    tracker.run()
    tracker.plot_prediction_error()
    tracker.plot_vert_speed()


def test_primitive_variables():

    alts = np.linspace(0, 71_000, 400)
    res = np.empty((len(alts), 3))

    for i, alt in enumerate(alts):
        res[i, :] = primitive_vars_at_altitude(alt)

    fig, ax = plt.subplots(1, 3)
    ax[0].plot(res[:, 0], alts, label="Pressure")
    ax[1].plot(res[:, 1], alts, label="Density")
    ax[2].plot(res[:, 2], alts, label="Temp")
    plt.legend()
    fig.tight_layout()
    fig.show()
