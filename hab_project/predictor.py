from .definitions import LAUNCH_THRESHOLD, LANDING_THRESHOLD, MEMORY_LENGTH
from .physics import primitive_vars_at_altitude
from hab_project.const import g
from enum import Enum, auto
from .wind import Wind
from math import sqrt
import numpy as np
import os


class State(Enum):

    NOT_YET_LAUNCHED = auto()
    RISING = auto()
    FALLING = auto()
    LANDED = auto()


class Predictor:

    curr_line = None
    memory = []
    state = State.NOT_YET_LAUNCHED
    wind: Wind

    last_prediction_idx = 0
    num_received_telem = 0
    last_prediction = ()

    def __init__(self,
                 telem,
                 balloon,
                 prediction_file,
                 wind=None,
                 prediction_gap=10):

        self.telem = telem
        self.balloon = balloon
        self.prediction_file = os.path.abspath(prediction_file)
        self.prediction_gap = prediction_gap

        if wind is None:
            self.wind = Wind()

        # Copy column enumeration to current class for convenience
        self.cols = self.telem.cols

    def run(self):

        self.telem.wait_for_telemetry()
        while self.state != State.LANDED:
            self.main_loop_iter()

    def main_loop_iter(self):
        self.curr_line = self.telem.get_next_line()

        if self.curr_line is not None:

            self.add_to_memory()
            self.determine_state()

            if self.state is State.RISING:
                self.manage_wind_bands()

            if self.state in [State.RISING, State.FALLING]:
                self.predict_landing()

    def determine_state(self):
        self.determine_if_launched()
        self.determine_if_falling()
        self.determine_if_landed()

    def determine_if_landed(self):

        if self.state == State.FALLING:
            curr_alt = self.get_most_recent_value(self.cols.ALTITUDE)
            launch_alt = self.get_launch_value(self.cols.ALTITUDE)

            if abs(curr_alt - launch_alt) < LANDING_THRESHOLD:
                curr_time = self.get_curr_time()
                print(f"{curr_time}: Landed!")
                self.state = State.LANDED

    def predict_landing(self):

        if self.num_received_telem - self.last_prediction_idx > self.prediction_gap:

            curr_lat, curr_lon, curr_alt = self.get_lat_lon_alt()
            pred_lat, pred_lon, pred_alt = self.get_lat_lon_alt()

            lower_bands = self.wind.return_lower_bands(curr_alt)

            #
            speed = 0.0
            height = curr_alt
            for band in reversed(lower_bands):
                delta_lat, delta_lon, speed, height = self.find_bandchange(band, speed, height)
                pred_lat += delta_lat
                pred_lon += delta_lon

            self.last_prediction = (pred_lat, pred_lon)
            self.write_prediction()
            self.last_prediction_idx = self.num_received_telem

    def calculate_c(self, m, alt, dr):
        _, rho, _ = primitive_vars_at_altitude(alt)
        area = self.balloon.burst_area
        return (m * g) / (0.5 * area * rho * dr ** 2)

    def calculate_descent_rate(self, m, c, alt):
        _, rho, _ = primitive_vars_at_altitude(alt)
        area = self.balloon.burst_area
        return sqrt((m * g) / (0.5 * rho * c * area))

    def vertical_speed(self):
        alts = []
        for item in self.memory:
            alts.append(item[self.cols.ALTITUDE])

        t0 = self.memory[0][self.cols.TIME]
        t1 = self.memory[-1][self.cols.TIME]
        dt = (t1 - t0).total_seconds() / len(alts)

        return np.mean(np.diff(alts)) / dt

    def find_bandchange(self, band, v, h):

        d_lat_dt = band["d_lat_dt"]
        d_lon_dt = band["d_lon_dt"]

        if h > self.wind.highest_band_height():
            bw = h - band["top_height"]
        else:
            bw = self.wind.band_width

        m = self.balloon.descent_mass
        if self.state == State.FALLING:

            dr = self.vertical_speed()
            # self.balloon.drag_coefficient = 1/5 * (4 * self.balloon.drag_coefficient +
            #                                        self.calculate_c(m, dr, h))

        descent_rate = self.calculate_descent_rate(m, self.balloon.drag_coefficient, h)
        t_total = bw / descent_rate

        return d_lat_dt * t_total, d_lon_dt * t_total, v, h-bw

    def get_lat_lon_alt(self):
        lat = self.get_most_recent_value(self.cols.LATITUDE)
        lon = self.get_most_recent_value(self.cols.LONGITUDE)
        alt = self.get_most_recent_value(self.cols.ALTITUDE)

        return lat, lon, alt

    def determine_if_falling(self):

        if self.state == State.RISING:
            recent_alts = []

            for item in self.memory:
                recent_alts.append(item[self.cols.ALTITUDE])

            if np.sum(np.diff(np.array(recent_alts))) < 0.0:
                print(f"{self.get_curr_time()}: Falling!")
                self.state = State.FALLING

    def manage_wind_bands(self):

        if self.state is State.RISING:

            lat, lon, alt = self.get_lat_lon_alt()
            curr_time = self.get_curr_time()

            if self.wind.is_empty():
                self.wind.add_band(alt, lat, lon, curr_time, 0.0, 0.0)

            if alt > self.wind.highest_band_height() + self.wind.band_width:

                _, prev_lat, prev_lon, prev_time, _, _ = self.wind.get_top_band_info()

                dt = (curr_time - prev_time).total_seconds()
                d_lat_dt = (lat - prev_lat) / dt
                d_lon_dt = (lon - prev_lon) / dt

                self.wind.add_band(alt, lat, lon, curr_time, d_lat_dt, d_lon_dt)

    def add_to_memory(self):

        if len(self.memory) < MEMORY_LENGTH:
            self.memory.append(self.curr_line)
        else:
            self.memory.append(self.curr_line)
            self.memory.pop(0)

        self.num_received_telem += 1

    def get_launch_value(self, name):
        return self.telem.launch_values[name]

    def get_init_value(self, name):
        return self.telem.init_values[name]

    def get_most_recent_value(self, name):
        return self.memory[-1][name]

    def get_curr_time(self):
        return self.get_most_recent_value(self.cols.TIME)

    def determine_if_launched(self):

        if self.state is State.NOT_YET_LAUNCHED:
            init_alt = self.get_init_value(self.cols.ALTITUDE)
            curr_alt = self.get_most_recent_value(self.cols.ALTITUDE)

            if curr_alt - init_alt > LAUNCH_THRESHOLD:
                print(f"{self.get_curr_time()}: Balloons away!")
                self.state = State.RISING
                self.telem.launch_values = self.telem.curr_values

    def write_prediction(self):

        with open(self.prediction_file, 'a') as f:
            f.write(f"{self.last_prediction[0]}, {self.last_prediction[1]}\n")
