from .const import g, R, M_air
from math import exp, pi, sqrt


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


def radius_at_tp(t, p, n):
    """Finds the radius of the balloon as a function of the external
    temperature and pressure, T and P, using the Ideal Gas Law:
        PV = nRT. T is expected in Kelvin and P in Pascals."""

    # from the ideal gas law ...
    return ((3 * n * R * t) / (4 * pi * p)) ** (1 / 3)


def find_terminal_velocity(m, c, area, alt):

    _, rho, _ = primitive_vars_at_altitude(alt)
    return -1.0 * sqrt(m * g / (0.5 * c * rho * area))


def find_drag_coefficient(m, v, area, alt):
    return 1.75


def drag_at_alt(v, c, area, alt):

    _, rho, _ = primitive_vars_at_altitude(alt)
    return 0.5 * c * rho * v ** 2 * area
