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
    args = build_argparser().parse_args()
    detect(args)
    
if __name__ == "__main__":
    main()