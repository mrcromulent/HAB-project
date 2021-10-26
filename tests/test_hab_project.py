from hab_project.definitions import DATA_DIR
from hab_project.analysis import Analyser
from datetime import datetime, timedelta
from hab_project.config import FMT
import matplotlib.pyplot as plt
import numpy as np
import os


def test_yerraloon2():
    def date_repr(date):
        # 2018 01 17 Wed 2:48 PM GMT + 11
        return datetime.combine(datetime(2018, 1, 17), datetime.strptime(date, FMT).time()) + \
               timedelta(hours=11)

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


def test_hab_project():

    from hab_project.physics import primitive_vars_at_altitude

    alts = np.linspace(0, 71_000, 400)
    res = np.empty((len(alts), 3))

    for i, alt in enumerate(alts):
        res[i, :] = primitive_vars_at_altitude(alt)

    fig, ax = plt.subplots(1, 3)
    ax[0].plot(res[:, 0], alts, label="Pressure")
    # ax[0].set_xscale('log')
    ax[1].plot(res[:, 1], alts, label="Density")
    # ax[1].set_xscale('log')
    ax[2].plot(res[:, 2], alts, label="Temp")
    plt.legend()
    fig.tight_layout()
    fig.show()
