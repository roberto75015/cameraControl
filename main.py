import time
import logging
import imutils
import cv2
import sys
import numpy as np
import urllib.request
from servo import Servo
from haarDetector  import haarDetector
#from ddnDetector  import ddnDetector
import subprocess

class Detector(object):
    def __init__(self, url: str, cameraType: str):
        self.url = url
        self.detector = haarDetector()
        #self.detector = ddnDetector()
        #fovs = (62.2, 48.8)
        match cameraType:
                case "ov5647":
                    fovs = (53.5, 41.41)
                case "imx219":
                    fovs = (62.2, 48.8)
                case "imx708":
                    fovs = (66, 41)
                case "imx477":
                    fovs = (70.6, 43.3)
                case "imx500":
                    fovs = (66, 52.3)
                case _:
                    print("bad camera type, must be one of: ov5647, imx219, imx708, imx447, imx500")
                    sys.exit(1)
        self.servo = Servo(fovs[0], fovs[1])
        self.stop_detector = False

    def __del__(self):
        logging.info("Stopping Pan & tilt.")
        self.stop_detector = True

    def get_frame(self) -> bytes:
        with urllib.request.urlopen(self.url) as resp:
            i = np.asarray(bytearray(resp.read()), dtype="uint8")
            return cv2.imdecode(i, cv2.IMREAD_REDUCED_COLOR_4)  # with _8 1920x1080 becomes 240x135, keep using _4
        print("Can't read image from url")
        sys.exit(1)

    def detector_loop(self):
        print("Pan & tilt running...")
        max_sleep_time = 2
        sleep_increment = 0.100
        sleep_time = sleep_increment
        moves_threshold = 2
        while self.stop_detector is False:
            #frame = self.picam2.capture_array()
            frame = self.get_frame()
            y, x, junk = frame.shape
            size = (x, y)
            #frame = self.detector.convert(frame)
            #(frame, size) = self.detector.resize(frame)
            boxes = self.detector.detect(frame)
            angles = []
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                # save target angle to move to center of detected box
                angles.append(self.servo.angles( (x+(w/2), y+(h/2)), size))
            if len(angles) > 0:
                #cv2.imshow("Frame", frame)
                #cv2.waitKey(1)
                nmoves = self.servo.goSlowlyToCloserAngle(angles)
                if nmoves > moves_threshold:
                    sleep_time = sleep_increment
            # if nothing detected or no moves needed then sleep a bit
            if len(angles) == 0 or nmoves <= moves_threshold:
                time.sleep(sleep_time)
                sleep_time = min(sleep_time + sleep_increment, max_sleep_time)


# Set up logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cameraType = sys.argv[1]
    else:
        #cameraType = subprocess.check_output("rpicam-hello  --list-cameras | egrep '^0' | awk '{print $3;}'");
        print("Usage: detector <cameraType> {v1=ov5647, v2=imx219, imx708, imx447, imx500} (see rpicam-hello --list-cameras)")
        sys.exit(1)
    url = "http://localhost:8080?action=snapshot"
    if len(sys.argv) > 2:
        url = sys.argv[2]
    camera = Detector(url, cameraType)
    camera.detector_loop()
