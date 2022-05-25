from pathlib import Path
from os.path import dirname
from os.path import abspath

# This file contains all default parameters for the Arguement Parser in main.py

    # Parameters on the Pi

SHOW_VIDEO = False

# Set to MYRIAD on the Pi, CPU for regular pc testing
DEVICE_NAME = "MYRIAD"
SERVER_URL = "https://visitor-tracker-2.herokuapp.com/tracker/testjson"

# If the detection is at least this sure it's a person, increase the counter
CONFIDENCE = 0.35

DETECTION_0200 = "/models/person-detection-0200.xml"
DATA_PATH = 0


FOLDER_PATH = Path(dirname(abspath(__file__))).parent.absolute()
MODEL_PATH = str(FOLDER_PATH)+DETECTION_0200

#----------------------------------------------------------------
    #Uncomment this part to test on PCs

# SHOW_VIDEO = True

# # Set to MYRIAD on the Pi, CPU for regular pc testing
# DEVICE_NAME = "CPU"
# SERVER_URL = ""
# SERVER_URL = "http://localhost:3000/tracker/testjson"

# # If the detection is at least this sure it's a person, increase the counter
# CONFIDENCE = 0.35

# DETECTION_0200 = "/models/person-detection-0200.xml"


# FOLDER_PATH = Path(dirname(abspath(__file__))).parent.absolute()

# DATA_PATH = str(FOLDER_PATH.parent) + "/training_data/video_1647424766.4553282.h264"
# # DATA_PATH = 0

# MODEL_PATH = str(FOLDER_PATH)+DETECTION_0200