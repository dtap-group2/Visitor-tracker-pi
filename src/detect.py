import cv2
import numpy as np
import json
from datetime import datetime
import time
import requests
from threading import Thread
from openvino.inference_engine import IECore

# NORMALIZED boundaries (from 0 to 1.0)
BOUNDARIES = {"Bound 1": ((0.1,0.2),(0.2,0.3)),"Bound 2": ((0.5,0.6),(0.2,0.3)),
    "Bound 3": ((0.1,0.2),(0.8,0.9)),"Bound 4": ((0.45,0.7),(0.6,0.8))}

# Structure of m1_data:
#   m1_data = {"total": [0],
#              "regions":{
#                           "Boundary name 1": count1,
#                           "Boundary name 2": count2,
#                           ...
#                        }
#              }

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

def checkRegions(point: tuple, region_count: dict, BOUNDARIES: dict):
    for name, coord in BOUNDARIES.items():
        # print(name)
        AM_AB = np.dot(point, coord[0])
        AB_AB = np.dot(coord[0], coord[0])
        AM_AD = np.dot(point, coord[1])
        AD_AD = np.dot(coord[1], coord[1])
        if (0 < AM_AB and AM_AB < AB_AB) and (0 < AM_AD and AM_AD < AD_AD):
            if name not in region_count.keys():
                region_count[name] = 1
            else:
                region_count[name] += 1

def detect(args):
    ie = IECore()
    net = ie.read_network(model=args.model)
    input_name = next(iter(net.input_info))

    for name, info in net.outputs.items():
        print("\tname: {}".format(name))
        print("\tshape: {}".format(info.shape))
        print("\tlayout: {}".format(info.layout))
        print("\tprecision: {}\n".format(info.precision))

    exec_net = ie.load_network(network=args.model, device_name=args.device)

    N, C, H, W = net.input_info[input_name].tensor_desc.dims
    
    cap = Camera(args.input)
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    # Frame duration in seconds
    FRAME_DURATION = 1

    # OpenCV detection time out in seconds
    TIME_OUT = 10

    BUFFERED = False
    BUFFER_FILE = "data.json"


    # Time interval between data sends to server in seconds
    SEND_INTERVAL = 5

    if args.input != 0:
        TIME_OUT = 0

        # Note the original video frame rate while testing
        FRAME_DURATION = 1/30

    timeout_clock = 0
    prev = 0
    time_elapsed = 0


    # Store data
    m1_data = {"total": [0], "regions":{}}

    # Timer for resend interval
    m1_timer = time.time()

    # contains time before next time this sends data to server
    # and the number of sending attempts
    resend_counter = [SEND_INTERVAL,0]
    while cap.isRunning():
        time_elapsed = time.time() - prev
        
        if time_elapsed > FRAME_DURATION:
            prev = time.time()
            success, frame = cap.read()
            region_count = {}
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

                
                count = 0
                for row in datarows:
                    if row[2] > args.confidence:
                        count += 1
                        # print(row)

                        #These coordinates are NORMALIZED from 0 to 1.0
                        top_left_x_f = row[3]
                        top_left_y_f = row[4]
                        bottom_right_x_f = row[5]
                        bottom_right_y_f = row[6]

                        norm_center = ((top_left_x_f+bottom_right_x_f)/2,
                                (top_left_y_f+bottom_right_y_f)/2)

                        checkRegions(norm_center, region_count, BOUNDARIES)

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
                m1_data["total"].append(count)
                if args.output:
                    cv2.imshow("Frame", frame)
                    # print("{} - {}"
                    #     .format(m1_data["total"],
                    #             str(datetime.now().isoformat())))

                # Send data to server
                if time.time() - m1_timer > resend_counter[0]:
                    for data in m1_data["regions"].items():
                        m1_data["regions"][data] = np.ceil(np.mean(
                            m1_data["regions"][data], dtype=np.int)
                            ,dtype=np.int)
                    
                    # If there is buffered data in data.json, try to send it
                    # if it succeeded, wipe data.json
                    if BUFFERED:
                        with open(BUFFER_FILE, 'w', encoding='utf-8') as f:
                            buffer_status = requests.post(args.server,
                                                json=json.dumps(json.load(f)))
                            if buffer_status.status_code == 200:
                                f.truncate(0)
                                BUFFERED = False

                    
                    post_status = requests.post(args.server,
                                        json=json.dumps(m1_data),
                                        timeout=5)

                    # Checks if Post requests succeeded,
                    # if not, set update interval to 0 and
                    # increase resend counter  
                    # If resend counter is 10, dumps dicitonary to data.json
                    if args.server != "" and post_status.status_code == 200:
                        m1_data = {"total": [0], "regions":{}}
                        resend_counter = [SEND_INTERVAL,0]
                    else:
                        if resend_counter[1] < 10:
                            resend_counter[0] = 0
                            resend_counter[1] += 1
                        else:
                            with open(BUFFER_FILE, 'w', encoding='utf-8') as f:
                                json.dump(m1_data, f,
                                    ensure_ascii=False, indent=4)
                                
                                m1_data = {"total": [0], "regions":{}}
                                resend_counter = [SEND_INTERVAL,0]
                                BUFFERED = True

                key = cv2.waitKey(100)
                if key == ord('q'):
                    cap.stop()
                    cv2.destroyAllWindows()
                    # printCounts(total,region_count)
                    break
            else:
                if timeout_clock != 0 and time.time()-timeout_clock>TIME_OUT:
                    cap.stop()
                    cv2.destroyAllWindows()
                    # printCounts(total,region_count)
                    break
                else:
                    timeout_clock = time.time()