from importlib.resources import files
import hab_project
import os


BASE_DIR    = files(hab_project.__name__)
DATA_DIR    = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))

#
FMT                 = "%H:%M:%S"  # datetime format
LAUNCH_THRESHOLD    = 100  # m
LANDING_THRESHOLD   = 500  # m
MEMORY_LENGTH       = 10
