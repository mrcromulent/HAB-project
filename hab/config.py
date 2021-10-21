from enum import Enum, auto
from datetime import datetime

# Algorithm parameters
output_filepath = "prediction.txt"
callsign = "$$YERRA"
wind_band_width = 100  # m
sleep_time = 0.001  # s (usually 1)
prediction_gap = 0.06  # s (usually 90)

# Launch parameters
pay_m = 1.8  # kg
bal_m = 1.2  # kg
balloon_volume = 4  # m^3
M_gas = 0.004  # molar mass of helium, kg/mol
parachute_diameter = 1.2192  # 4 ft in m
payload_area = 0.3 * 0.3  # m^2

# Parachute Drag Coefficient
C = 0.5

OLD_DATA = False


def date_repr(date):
    return datetime.strptime(date, '%H:%M:%S')


if OLD_DATA:

    def humidity_fmt(s):
        return float(s.split('*')[0])

    fp = "../data/YERRALOON1_DATA/telemetry.txt"
    column_headers = \
        [
            'CALLSIGN',
            'PACKET',
            'TIME',
            'LATITUDE',
            'LONGITUDE',
            'ALTITUDE',
            'SPEED',
            'HEADING',
            'SATELLITES',
            'INTERNAL_TEMP',
            'EXTERNAL_TEMP',
            'PRESSURE',
            'HUMIDITY_CHECK',
        ]
    Columns = Enum('Columns', column_headers, start=0)
    formatter_funcs = {
        Columns.CALLSIGN:           str,
        Columns.PACKET:             int,
        Columns.TIME:               date_repr,
        Columns.LATITUDE:           float,
        Columns.LONGITUDE:          float,
        Columns.ALTITUDE:           float,
        Columns.SPEED:              float,
        Columns.HEADING:            float,
        Columns.SATELLITES:         int,
        Columns.INTERNAL_TEMP:      float,
        Columns.EXTERNAL_TEMP:      float,
        Columns.PRESSURE:           float,
        Columns.HUMIDITY_CHECK:     humidity_fmt,
    }
else:

    def pred_lon_fmt(s):
        return float(s.split('*')[0])

    fp = "../data/YERRALOON2_DATA/telemetry.txt"
    column_headers = \
        [
            'CALLSIGN',
            'PACKET',
            'TIME',
            'LATITUDE',
            'LONGITUDE',
            'ALTITUDE',
            'SPEED',
            'HEADING',
            'SATELLITES',
            'INTERNAL_TEMP',
            'EXTERNAL_TEMP',
            'PRESSURE',
            'HUMIDITY',
            'PRED_LAT',
            'PRED_LON',
        ]
    Columns = Enum('Columns', column_headers, start=0)
    formatter_funcs = {
        Columns.CALLSIGN:           str,
        Columns.PACKET:             int,
        Columns.TIME:               date_repr,
        Columns.LATITUDE:           float,
        Columns.LONGITUDE:          float,
        Columns.ALTITUDE:           float,
        Columns.SPEED:              float,
        Columns.HEADING:            float,
        Columns.SATELLITES:         int,
        Columns.INTERNAL_TEMP:      float,
        Columns.EXTERNAL_TEMP:      float,
        Columns.PRESSURE:           float,
        Columns.HUMIDITY:           float,
        Columns.PRED_LAT:           float,
        Columns.PRED_LON:           pred_lon_fmt,
    }
