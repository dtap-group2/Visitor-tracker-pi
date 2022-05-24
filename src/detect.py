import cv2
import numpy as np
import json
import time
import requests
from threading import Thread
from openvino.inference_engine import IECore
from polygon_check import is_inside

# NORMALIZED boundaries (from 0 to 1.0)
BOUNDARIES = {"Bound 1": [(0.06606606606606606, 0.9579158316633266),
                        (0.042042042042042045, 0.5891783567134269),
                        (0.15615615615615616, 0.5390781563126252),
                        (0.26576576576576577, 0.5470941883767535),
                        (0.32432432432432434, 0.44288577154308617),
                        (0.4624624624624625, 0.46693386773547096), 
                        (0.5495495495495496, 0.5150300601202404),
                        (0.5495495495495496, 0.6452905811623246),
                        (0.7762762762762763, 0.7294589178356713)]}

class Camera():
    def __init__(self, source):
        
        self.capture = cv2.VideoCapture(source)
        self.running = True

        self.status = False
        self.frame  = None

        self.thread = Thread(target = self.update,args=())
        self.thread.daemon = True
        self.thread.start()

    def isRunning(self):
        return self.running

    def update(self):
        while self.running:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def read(self):
        frame = None
        if self.status:
            frame = self.frame.copy()
        return self.status, frame  

    def stop(self):
        self.running = False
        self.thread.join()

def checkRegions(point: tuple, frame_data: dict, BOUNDARIES: dict):
    for name, coord in BOUNDARIES.items():
        if (is_inside(points =coord,p=point)):
            if name not in frame_data.keys():
                frame_data[name] = 1
            else:
                frame_data[name] += 1

def detect(args):
    ie = IECore()
    net = ie.read_network(model=args.model)
    input_name = next(iter(net.input_info))

    exec_net = ie.load_network(network=args.model, device_name=args.device)

    N, C, H, W = net.input_info[input_name].tensor_desc.dims
    
    cap = Camera(args.input)

    # Frame duration in seconds
    FRAME_DURATION = 1

    # OpenCV detection time out in seconds
    TIME_OUT = 10

    BUFFERED = False
    BUFFER_FILE = "data.json"


    # Time interval between data sends to server in seconds
    SEND_INTERVAL = 1

    if args.input != 0:
        TIME_OUT = 0

        # Note the original video frame rate while testing
        FRAME_DURATION = 1/30

    timeout_clock = 0
    prev = 0
    time_elapsed = 0


    # Store data
    current_time = time.time()
    m1_data = [current_time,{}]
    buffer_data = []

    # Timer for resend interval
    m1_timer = current_time

    # contains time before next time this sends data to server
    resend_counter = SEND_INTERVAL

    frame_data = {}
    while cap.isRunning():
        time_elapsed = time.time() - prev
        
        if time_elapsed > FRAME_DURATION:
            prev = time.time()
            success, frame = cap.read()
            if success:
                #reads height, width and colors(rgb default 3)

                height, width, colors = frame.shape

                img_resized = cv2.resize(frame, (H, W))
                input_data = np.expand_dims(np.transpose(img_resized, (2, 0, 1)), 0)

                #detect people using the model and intel stick
                result = exec_net.infer({input_name: input_data})

                output = result['detection_out']
                datarows = output[0][0]

                np.set_printoptions(threshold=np.inf) 
                datarows = datarows[~np.all(datarows == 0, axis=1)]

                for row in datarows:
                    if row[2] > args.confidence:

                        #These coordinates are NORMALIZED from 0 to 1.0
                        top_left_x_f = row[3]
                        top_left_y_f = row[4]
                        bottom_right_x_f = row[5]
                        bottom_right_y_f = row[6]

                        norm_center = ((top_left_x_f+bottom_right_x_f)/2,
                                (top_left_y_f+bottom_right_y_f)/2)

                        checkRegions(norm_center, frame_data, BOUNDARIES)

                        # checks if the user need to dislay video output
                        if args.output:
                            top_left_x = int(row[3] * width)
                            top_left_y = int(row[4] * height)
                            bottom_right_x = int(row[5] * width)
                            bottom_right_y = int(row[6] * height)
                            cv2.rectangle(frame, (top_left_x, top_left_y),
                                        (bottom_right_x, bottom_right_y), (255, 0, 0), 2)
                            text_loc = ((bottom_right_x + top_left_x)//2,
                                        bottom_right_y)
                            cv2.putText(frame,
                                        "{:.2%}".format(row[2]),
                                        text_loc,
                                        fontFace=cv2.FONT_HERSHEY_PLAIN,
                                        fontScale=2,
                                        color=(0,255,0),
                                        thickness=2,
                                        lineType=cv2.LINE_AA)
                if args.output:
                    cv2.imshow("Frame", frame)

                temp = m1_data[1]
                for name, value in frame_data.items():
                    if name in temp.keys():
                        temp[name].append(value)
                    else:
                        temp[name] = [value]
                curr = time.time()
                temp = {}
                if curr - m1_timer > resend_counter:
                    m1_timer = curr
                    for name, count in m1_data[1].items():
                        temp[name] = max(count,)
                    for name, count in temp.items():
                        m1_data[1][name] = count

                    if len(buffer_data) > 0:
                        buffer_status = requests.post(args.server,
                                                json=buffer_data,
                                                timeout=0.5)
                        if buffer_status.status_code == 200:
                            print("buffer dump: {}".format(json.dumps(buffer_data,)))
                            buffer_data = []
                    post_status = requests.post(args.server,
                                        json=m1_data,
                                        timeout=0.5)
                    print("json dump: {}".format(json.dumps(m1_data)))
                    print("post_status {}".format(post_status.status_code))
                    # Checks if Post requests succeeded,
                    # if not, set update interval to 0 and
                    # increase resend counter  
                    # If resend counter is 10, dumps dicitonary to data.json
                    if args.server != "" and post_status.status_code == 200:
                        m1_data = [time.time(),{}]
                    else:
                        buffer_data.append(m1_data)
                        m1_data = [time.time(),{}]
                        
                frame_data = {}
                key = cv2.waitKey(100)
                if key == ord('q'):
                    cap.stop()
                    cv2.destroyAllWindows()
                    break
            else:
                if timeout_clock != 0 and time.time()-timeout_clock>TIME_OUT:
                    cap.stop()
                    cv2.destroyAllWindows()
                    break
                else:
                    timeout_clock = time.time()