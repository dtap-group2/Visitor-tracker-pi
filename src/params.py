from pathlib import Path
from os.path import dirname
from os.path import abspath

# SHOW_VIDEO = False

# # Set to MYRIAD on the Pi, CPU for regular pc testing
# DEVICE_NAME = "MYRIAD"
# # SERVER_URL = "http://localhost:3000/tracker/update-data"

# # If the detection is at least this sure it's a person, increase the counter
# CONFIDENCE = 0.35

# DETECTION_0200 = "/models/person-detection-0200.xml"
# DATA_PATH = 0


# FOLDER_PATH = Path(dirname(abspath(__file__))).parent.absolute()
# DATA_PATH = str(FOLDER_PATH.parent) + "/training_data/video_1647424766.4553282.h264"
# MODEL_LOCATION = str(FOLDER_PATH)+DETECTION_0200


SHOW_VIDEO = True

# Set to MYRIAD on the Pi, CPU for regular pc testing
DEVICE_NAME = "CPU"
# SERVER_URL = "http://localhost:3000/tracker/update-data"

# If the detection is at least this sure it's a person, increase the counter
CONFIDENCE = 0.35

DETECTION_0200 = "/models/person-detection-0200.xml"


FOLDER_PATH = Path(dirname(abspath(__file__))).parent.absolute()

DATA_PATH = str(FOLDER_PATH.parent) + "/training_data/video_1647424766.4553282.h264"
MODEL_PATH = str(FOLDER_PATH)+DETECTION_0200