# Visitor-tracker-pi
Code for DTAP 2022 visitor tracker Raspberry Pi

# Notes
Cd to the folder
Run python3 src/main.py to start the program (on windows use python instead of python3)

currenty data is buffered to a dictionary not data.json

The detection doesn't send any information about the regions to server yet

There are no functions to check if boundaries have the same name yet

There are 2 sets of parameters in params.py, one for testing, the other for 
runing on the PI.
Change variables there if you do not want to use Arguement Parsers

While testing, check the if args.input != 0 condition before the big while loop,
FRAME_DURATION parameter must not be smaller than the video's frame duration,
if it is, the program will terminate early

Right now the server address is only for sending detection data