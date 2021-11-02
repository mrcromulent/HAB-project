from math import pi
import yaml


class Balloon:

    parachute_diameter: float
    payload_area: float
    payload_mass: float
    balloon_mass: float
    parachute_area: float
    burst_area: float
    descent_mass: float

    def __init__(self, param_file):

        with open(param_file, "r") as f:
            param = yaml.load(f, Loader=yaml.FullLoader)
            for key, val in param.items():
                setattr(self, key, val)

        self.find_parameters()

    def find_parameters(self):

        self.parachute_area = 2 * pi * (self.parachute_diameter / 2) ** 2
        self.burst_area = self.parachute_area + self.payload_area
        self.descent_mass = self.payload_mass + 0.05 * self.balloon_mass
