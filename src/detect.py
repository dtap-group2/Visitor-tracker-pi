import json
import cv2
import numpy as np
import json
import datetime
import requests
from openvino.inference_engine import IECore

def detect(args):
    ie = IECore()

    net = ie.read_network(model=args.model)
    input_name = next(iter(net.input_info))

    # print("Outputs:")
    for name, info in net.outputs.items():
        print("\tname: {}".format(name))
        print("\tshape: {}".format(info.shape))
        print("\tlayout: {}".format(info.layout))
        print("\tprecision: {}\n".format(info.precision))

    exec_net = ie.load_network(network=args.model, device_name=args.device)

    N, C, H, W = net.input_info[input_name].tensor_desc.dims
    
    cap = cv2.VideoCapture(args.input)
    while True:
        success, frame = cap.read()

        if success:
            #reads height, width and colors(rgb default 3)
            h_orig, w_orig, c_orig = frame.shape

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
                    if args.output:
                        top_left_x_float = row[3]
                        top_left_y_float = row[4]
                        bottom_right_x_float = row[5]
                        bottom_right_y_float = row[6]

                        top_left_x = int(top_left_x_float * w_orig)
                        top_left_y = int(top_left_y_float * h_orig)
                        bottomn_right_x = int(bottom_right_x_float * w_orig)
                        bottomn_right_y = int(bottom_right_y_float * h_orig)

                        cv2.rectangle(frame, (top_left_x, top_left_y),
                                    (bottomn_right_x, bottomn_right_y), (255, 0, 0), 2)
                        text_loc = ((bottomn_right_x + top_left_x)//2,
                                    bottomn_right_y)
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

            # Send data to server
            frame_data = json.dumps({"time":datetime.datetime.now().isoformat(), 
                                "total_count":count})
            # requests.post(SERVER_URL,data=frame_data)
            key = cv2.waitKey(100)
            if key == ord('q'):
                break
        else:
            break