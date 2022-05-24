from params import *
from detect import detect
from argparse import ArgumentParser

def build_argparser():
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", required=False, type=str,
                        default=MODEL_PATH,
                        help="Path to an xml file with a trained model.")
    
    parser.add_argument("-i", "--input", required=False,
                        default=DATA_PATH,
                        help="Default 0 taking camra input"
                             "Path to image or video file")

    parser.add_argument("-d", "--device", required=False,type=str, 
                        default=DEVICE_NAME,
                        help="Processor type"
                             "MYRIAD for Intel Neural Stick "
                             "CPU for x64 cpu (used for testing on local machines)")

    parser.add_argument("-c", "--confidence", required=False,type=float, 
                        default=CONFIDENCE,
                        help="Probability threshold for detections filtering")

    parser.add_argument("-o", "--output", type=bool, default=SHOW_VIDEO,
                        help="Enable video output")
    parser.add_argument("-s","--server",required=False,type=str,
                        default=SERVER_URL,
                        help="Server address to send data to")
    return parser


def main():
<<<<<<< HEAD
    ie = IECore()

    net = ie.read_network(model=MODEL_LOCATION)
    input_name = next(iter(net.input_info))

    # print("Outputs:")
    for name, info in net.outputs.items():
        print("\tname: {}".format(name))
        print("\tshape: {}".format(info.shape))
        print("\tlayout: {}".format(info.layout))
        print("\tprecision: {}\n".format(info.precision))

    exec_net = ie.load_network(network=MODEL_LOCATION, device_name=DEVICE_NAME)

    N, C, H, W = net.input_info[input_name].tensor_desc.dims

    cap = cv2.VideoCapture(DATA_PATH)

    while True:
        success, frame = cap.read()

        if success:
            # reads height, width and colors(rgb default 3)
            h_orig, w_orig, c_orig = frame.shape

            img_resized = cv2.resize(frame, (H, W))
            input_data = np.expand_dims(
                np.transpose(img_resized, (2, 0, 1)), 0)

            # detect people using the model and intel stick
            result = exec_net.infer({input_name: input_data})

            output = result['detection_out']
            datarows = output[0][0]

            np.set_printoptions(threshold=np.inf)
            datarows = datarows[~np.all(datarows == 0, axis=1)]

            count = 0

            for row in datarows:
                if row[2] > CONFIDENCE:
                    count += 1
                    # print(row)
                    if SHOW_VIDEO:
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
                                    color=(0, 255, 0),
                                    thickness=2,
                                    lineType=cv2.LINE_AA)
            if SHOW_VIDEO:
                cv2.imshow("Frame", frame)

            # Send data to server
            frame_data = {"timeFrame": datetime.datetime.now().timestamp(),
                          "totalCount": count}
            requests.post(SERVER_URL, json=frame_data)
            key = cv2.waitKey(100)
            if key == ord('q'):
                break
        else:
            break


=======
    args = build_argparser().parse_args()
    detect(args)
    
>>>>>>> develop
if __name__ == "__main__":
    main()
