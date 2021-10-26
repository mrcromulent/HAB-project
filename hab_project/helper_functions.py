from math import pi, radians, sin, cos, asin, sqrt
from .const import earth_radius


def haversine_distance(lat1, lon1, lat2, lon2):
    del_lat = radians(lat1 - lat2)
    del_long = radians(lon1 - lon2)

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    a = sin(del_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(del_long / 2) ** 2
    c = 2 * asin(sqrt(a))
    dist = earth_radius * c

    return dist
