from collections import OrderedDict
from enum import Enum
import time
import os


class Telemetry:

    read_pos = 0
    sleep_time = 0.001
    init_values = dict()
    launch_values = dict()
    curr_values = dict()

    def __init__(self, telemetry_file, column_descriptors, callsign):
        self.telemetry_file = os.path.abspath(telemetry_file)

        self.header, self.formatter_funcs = zip(*column_descriptors)
        self.cols = Enum('cols', self.header, start=0)
        self.callsign = callsign

    def wait_for_telemetry(self):
        print("Waiting for telemetry...")

        telemetry_found = False

        while not telemetry_found:
            if os.path.exists(self.telemetry_file):
                with open(self.telemetry_file, "r") as f:
                    f.seek(self.read_pos, 0)

                    ln = f.readline()

                    line_is_valid, parsed_line = self.valid_line(ln)
                    if line_is_valid:
                        telemetry_found = True
                        self.init_values = parsed_line

                    self.read_pos = f.tell()

            time.sleep(self.sleep_time)

    def valid_line(self, ln):
        if ln.startswith("$$") and ln.find(self.callsign) != -1:
            parsed_line = self.parse_line(ln)
            if parsed_line[self.cols.LATITUDE] != 0.0:
                return True, parsed_line

        return False, dict()

    def parse_line(self, ln):
        d = OrderedDict()
        ln_list = ln.split(",")

        for k, item in self.cols.__members__.items():
            func = self.formatter_funcs[item.value]
            d[item] = func(ln_list[item.value])

        return d

    def get_next_line(self):
        with open(self.telemetry_file, "r") as f:
            f.seek(self.read_pos, 0)
            ln = f.readline()

            if not ln == "":  # Not reached end of file
                line_is_valid, parsed_line = self.valid_line(ln)
                self.read_pos = f.tell()

                if line_is_valid:
                    self.curr_values = parsed_line
                    return parsed_line
