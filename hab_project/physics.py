from math import exp, radians, sin, cos, asin, sqrt
from .const import g, R, M_air, earth_radius


def haversine_distance(latlon1, latlon2):
    """

    :param latlon1:
    :param latlon2:
    :return:
    """
    lat1, lon1 = latlon1
    lat2, lon2 = latlon2

    del_lat = radians(lat1 - lat2)
    del_long = radians(lon1 - lon2)

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    a = sin(del_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(del_long / 2) ** 2
    c = 2 * asin(sqrt(a))
    dist = earth_radius * c

    return dist


def get_reference_rates(altitude):
    """
    :param altitude:
    :return: Reference pressure [Pa], reference density [kg/m^3],
    reference temperature [K], lapse rate [K/m] and height of reference [m]
    """

    def case(x):
        return altitude <= x

    if case(11_000):  # Troposphere
        return 101_325.00, 1.2250, 288.15, -0.0065, 0.0
    elif case(20_000):  # Stratosphere1
        return 22_632.10, 0.36391, 216.65, 0.0, 11_000
    elif case(32_000):  # Stratosphere2
        return 5_474.89, 0.08803, 216.65, 0.001, 20_000
    elif case(47_000):  # Stratosphere3
        return 868.02, 0.01322, 228.65, 0.0028, 32_000
    elif case(51_000):
        return 110.91, 0.00143, 270.65, 0.0, 47_000
    elif case(71_000):
        return 66.94, 0.00086, 270.65, -0.0028, 51_000
    else:
        raise ValueError(f"Attempting to get reference rates for {altitude=}")


def primitive_vars_at_altitude(altitude):
    p_b, rho_b, t_b, l_b, h_b = get_reference_rates(altitude)

    if l_b != 0.0:
        p   = p_b * ((t_b + l_b * (altitude - h_b)) / t_b) ** (- g * M_air / (R * l_b))
        rho = rho_b * (t_b / (t_b + l_b * (altitude - h_b))) ** (1 + g * M_air / (R * l_b))
        t   = t_b + l_b * (altitude - h_b)

    else:
        p   = p_b * exp((-g * M_air * (altitude - h_b)) / (R * t_b))
        rho = rho_b * exp((-g * M_air * (altitude - h_b)) / (R * t_b))
        t   = t_b

    return p, rho, t
