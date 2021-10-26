from hab_project.definitions import DATA_DIR
from hab_project.helper_functions import haversine_distance
from hab_project.physics import radius_at_tp, primitive_vars_at_altitude
import matplotlib.pyplot as plt
from matplotlib import dates
from datetime import datetime, timedelta
from collections import OrderedDict
from hab_project.const import g
from hab_project.config import FMT
from hab_project.const import R
from enum import Enum, auto
from math import pi
import numpy as np
import yaml
import time
import os


class State(Enum):

    NOT_YET_LAUNCHED = auto()
    RISING = auto()
    FALLING = auto()
    LANDED = auto()


class Telemetry:

    f_pos = 0
    sleep_time = 0.001
    callsign = "YERRA"
    init_values = dict()
    launch_values = dict()
    curr_values = dict()

    def __init__(self, telemetry_file, column_descriptors):
        self.telemetry_file = os.path.abspath(telemetry_file)
        self.header, self.formatter_funcs = zip(*column_descriptors)
        self.columns = Enum('columns', self.header, start=0)

    def wait_for_telemetry(self):
        print("Waiting for telemetry...")

        telemetry_found = False

        while not telemetry_found:
            if os.path.exists(self.telemetry_file):
                with open(self.telemetry_file, "r") as f:
                    f.seek(self.f_pos, 0)

                    ln = f.readline()

                    line_is_valid, parsed_line = self.valid_line(ln)
                    if line_is_valid:
                        telemetry_found = True
                        self.init_values = parsed_line

                    self.f_pos = f.tell()

            time.sleep(self.sleep_time)

    def valid_line(self, ln):
        if ln.startswith("$$"):
            if ln.find(self.callsign) != -1:
                parsed_line = self.parse_line(ln)
                if parsed_line[self.columns.LATITUDE] != 0.0:
                    return True, parsed_line

        return False, dict()

    def parse_line(self, ln):
        d = OrderedDict()
        ln_list = ln.split(",")

        for k, item in self.columns.__members__.items():
            func = self.formatter_funcs[item.value]
            d[item] = func(ln_list[item.value])

        return d

    def get_next_line(self):
        with open(self.telemetry_file, "r") as f:
            f.seek(self.f_pos, 0)
            ln = f.readline()

            if not ln == "":  # Not reached end of file
                line_is_valid, parsed_line = self.valid_line(ln)
                self.f_pos = f.tell()

                if line_is_valid:
                    self.curr_values = parsed_line
                    return parsed_line


class Param:

    n: float

    def __init__(self, param_file):

        with open(param_file, "r") as f:
            self.param = yaml.load(f, Loader=yaml.FullLoader)

        self.determine_launch_conditions()

    def determine_launch_conditions(self):

        parachute_diameter = self.param["parachute_diameter"]
        payload_area = self.param["payload_area"]
        payload_mass = self.param["payload_mass"]
        balloon_mass = self.param["balloon_mass"]

        self.param["parachute_area"] = 2 * pi * (parachute_diameter / 2) ** 2
        self.param["burst_area"] = self.param["parachute_area"] + payload_area
        self.param["descent_mass"] = payload_mass + 0.05 * balloon_mass

    def find_gas_n(self, start_temp, start_pres):
        """find_gas_n() finds the number of mols of gas in the balloon using the
        starting temperature (K), pressure (Pa) and volume (m^3) and the Ideal
        Gas Law."""

        self.n = start_pres * self.param["balloon_volume"] / (R * start_temp)

    def area_correction_at_tp(self, temp, press):
        """ac_at_alt() finds the 'area correction' (defined as the ratio of
        the balloon-payload system after and before bursting) as a function
        of the external temperature and pressure. Temperature is expected
        in Kelvin and Pressure in Pascal."""

        balloon_radius = radius_at_tp(temp, press, self.n)

        # Find the unburst area and return the ratio
        area_unburst = self.param["payload_area"] + pi * balloon_radius ** 2
        return self.param["area_burst"] / area_unburst


class Wind:
    band_width = 600

    def __init__(self):
        # {"top_height": 700, d_lat_dt: 0.01, d_lon_dt: 0.02}
        self.bands = []
        # for h in np.arange(600, 40_000, self.band_width):
        #     self.bands.append({"top_height": h, "d_lat_dt": 0.0, "d_lon_dt": 0.0})

    def is_empty(self):
        return len(self.bands) == 0

    def highest_band_height(self):
        if self.is_empty():
            raise ValueError
        else:
            return self.bands[-1]["top_height"]

    def return_lower_bands(self, alt):
        for i, b in enumerate(self.bands):
            if b["top_height"] > alt:
                return self.bands[:i]
        return []


class Tracker:

    simulate: bool

    memory = []
    state = State.NOT_YET_LAUNCHED
    wind = Wind()

    # prediction_gap = timedelta(seconds=0.32)
    # last_prediction_time = datetime.now()
    prediction_gap = 10
    last_prediction_idx = 0
    num_received_telem = 0
    prediction_error = []
    prediction_times = []

    def __init__(self, telem, param, prediction_file, simulate=False):

        self.telem = telem
        self.param = param
        self.prediction_file = os.path.abspath(prediction_file)
        self.simulate = simulate

    def run(self):

        self.telem.wait_for_telemetry()

        while self.state != State.LANDED:

            next_line = self.telem.get_next_line()

            if next_line is not None:

                self.add_to_memory(next_line)

                self.determine_if_launched()
                self.determine_if_falling()
                self.determine_if_landed()

                if self.state is State.RISING:
                    self.manage_wind_bands()

                if self.state in [State.RISING, State.FALLING]:
                    self.predict_landing()

    def determine_if_landed(self):

        if self.state == State.FALLING:
            curr_alt = self.get_most_recent_value(self.telem.columns.ALTITUDE)
            launch_alt = self.get_launch_value(self.telem.columns.ALTITUDE)

            if abs(curr_alt - launch_alt) < 500:
                curr_time = self.get_most_recent_value(self.telem.columns.TIME)
                print(f"{curr_time}: Landed!")
                self.state = State.LANDED

    def predict_landing(self):

        if self.num_received_telem - self.last_prediction_idx > self.prediction_gap:

            curr_lat, curr_lon, curr_alt = self.get_lat_lon_alt()
            pred_lat, pred_lon, pred_alt = self.get_lat_lon_alt()
            pred_speed = 0.0
            curr_time = self.get_most_recent_value(self.telem.columns.TIME)

            lower_bands = self.wind.return_lower_bands(curr_alt)

            for band in reversed(lower_bands):
                delta_lat, delta_lon, pred_speed = self.find_bandchange(band, pred_speed)

                pred_lat += delta_lat
                pred_lon += delta_lon
                pred_speed = pred_speed

            landing = -34.37408, 147.85953
            prediction_error = haversine_distance(pred_lat, pred_lon, *landing)
            if self.state == State.FALLING.FALLING:
                print("falling")
            self.prediction_error.append(prediction_error)
            self.prediction_times.append(curr_time)
            self.last_prediction_idx = self.num_received_telem

    def find_bandchange(self, band, pred_speed):

        # lower_bound = band["top_height"] - self.wind.band_width
        d_lat_dt = band["d_lat_dt"]
        d_lon_dt = band["d_lon_dt"]
        _, _, curr_alt = self.get_lat_lon_alt()
        # h = curr_alt - band["top_height"]
        x = curr_alt - band["top_height"]
        m = self.param.param["descent_mass"]
        area = self.param.param["burst_area"]
        v = pred_speed

        c = 0.01
        dt = 0.1
        t_total = 0.0

        _, rho, _   = primitive_vars_at_altitude(curr_alt)
        f_grav      = - m * g

        while x > 0:
            f_drag = 0.5 * c * v ** 2 * rho * area
            a = 1 / m * (f_drag + f_grav)
            v += a * dt
            x += v * dt
            t_total += dt

        return d_lat_dt * t_total, d_lon_dt * t_total, v

    def get_lat_lon_alt(self):
        lat = self.get_most_recent_value(self.telem.columns.LATITUDE)
        lon = self.get_most_recent_value(self.telem.columns.LONGITUDE)
        alt = self.get_most_recent_value(self.telem.columns.ALTITUDE)

        return lat, lon, alt

    def determine_if_falling(self):

        if self.state == State.RISING:
            recent_alts = []

            for item in self.memory:
                recent_alts.append(item[self.telem.columns.ALTITUDE])

            if np.sum(np.diff(np.array(recent_alts))) < 0.0:
                curr_time = self.get_most_recent_value(self.telem.columns.TIME)
                print(f"{curr_time}: Falling!")
                self.state = State.FALLING

    def manage_wind_bands(self):

        if self.state is State.RISING:

            lat, lon, alt = self.get_lat_lon_alt()
            curr_time = self.get_most_recent_value(self.telem.columns.TIME)

            if self.wind.is_empty():
                self.wind.bands.append({
                    "top_height": alt,
                    "lat": lat,
                    "lon": lon,
                    "time": curr_time,
                    "d_lat_dt": 0.0,
                    "d_lon_dt": 0.0}
                )
            else:
                if alt > self.wind.bands[-1]["top_height"] + self.wind.band_width:

                    prev_lat = self.wind.bands[-1]["lat"]
                    prev_lon = self.wind.bands[-1]["lon"]
                    prev_time = self.wind.bands[-1]["time"]

                    dt = (curr_time - prev_time).total_seconds()
                    self.wind.bands.append({
                        "top_height": alt,
                        "lat": lat,
                        "lon": lon,
                        "time": curr_time,
                        "d_lat_dt": (lat - prev_lat) / dt,
                        "d_lon_dt": (lon - prev_lon) / dt}
                    )

    def add_to_memory(self, next_line):

        if len(self.memory) < 10:
            self.memory.append(next_line)
        else:
            self.memory.append(next_line)
            self.memory.pop(0)

        self.num_received_telem += 1

    def get_launch_value(self, name):
        return self.telem.launch_values[name]

    def get_init_value(self, name):
        return self.telem.init_values[name]

    def get_most_recent_value(self, name):
        return self.memory[-1][name]

    def determine_if_launched(self):

        if self.state is State.NOT_YET_LAUNCHED:
            init_alt = self.get_init_value(self.telem.columns.ALTITUDE)
            curr_alt = self.get_most_recent_value(self.telem.columns.ALTITUDE)

            if curr_alt - init_alt > 100:
                curr_time = self.get_most_recent_value(self.telem.columns.TIME)
                print(f"{curr_time}: Balloons away!")
                self.state = State.RISING
                self.telem.launch_values = self.telem.curr_values

    def write_prediction(self):
        pass

    def plot_prediction_error(self):

        fig, ax = plt.subplots()
        ax.plot(self.prediction_times, self.prediction_error)
        self.format_axis(ax)
        fig.show()

    @staticmethod
    def format_axis(axis_obj):
        fmt = dates.DateFormatter(FMT)
        axis_obj.xaxis.set_major_formatter(fmt)
        axis_obj.tick_params(axis='x', labelrotation=90, labelsize=7)


def test_yerraloon1():

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

    telem = Telemetry(tf, headers)
    param = Param(pf)
    tracker = Tracker(telem, param, of, simulate=False)
    tracker.run()
    tracker.plot_prediction_error()


def test_yerraloon2():

    # Landing Location:
    # -34.31743, 148.73291

    def date_repr(date):
        # 2018 01 17 Wed 2:48 PM GMT + 11
        return datetime.combine(datetime(2018, 1, 17), datetime.strptime(date, FMT).time()) + \
               timedelta(hours=11)

    tf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "telemetry.txt")
    pf = os.path.join(DATA_DIR, "YERRALOON2_DATA", "param.yaml")
    of = "prediction.txt"

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

    telem = Telemetry(tf, headers)
    param = Param(pf)
    tracker = Tracker(telem, param, of, simulate=False)
    tracker.run()
    tracker.plot_prediction_error()


if __name__ == "__main__":
    test_yerraloon1()
    # test_yerraloon2()
