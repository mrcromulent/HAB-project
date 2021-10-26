from importlib.resources import files
import hab_project
import os


BASE_DIR    = files(hab_project.__name__)
DATA_DIR    = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
