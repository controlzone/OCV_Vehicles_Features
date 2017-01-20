import logging
import logging.handlers
import os
import time
import sys

import cv2
import numpy as np

from keypoint_data import KeypointData
from draw_matches import *

# ============================================================================

IMAGE_DIR = "images"
IMAGE_FILENAME_FORMAT = IMAGE_DIR + "/frame_%04d.png"
KEYPOINT_DATA_FILE = "keypoints.p"

##  Keypoints looks like it needs to have the SIFT func
##  put over the cars.png image and stored in the pickle .p
##  Turns out I am blind and there is a file 'create_kd_sift.py'
##  that does exactly that. Just need to port it to 3.0.0

# Support either video file or individual frames
CAPTURE_FROM_VIDEO = False
if CAPTURE_FROM_VIDEO:
    IMAGE_SOURCE = "traffic.avi" # Video file
else:
    IMAGE_SOURCE = IMAGE_FILENAME_FORMAT # Image sequence

# Time to wait between frames, 0=forever
WAIT_TIME = 100 # 250 # ms

LOG_TO_FILE = True

# ============================================================================

def init_logging():
    main_logger = logging.getLogger()

    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(levelname)-8s [%(name)s] %(message)s'
        , datefmt='%Y-%m-%d %H:%M:%S')
    
    handler_stream = logging.StreamHandler(sys.stdout)
    handler_stream.setFormatter(formatter)
    main_logger.addHandler(handler_stream)
    
    if LOG_TO_FILE:
        handler_file = logging.handlers.RotatingFileHandler("debug.log"
            , maxBytes = 2**24
            , backupCount = 10)
        handler_file.setFormatter(formatter)
        main_logger.addHandler(handler_file)
    
    main_logger.setLevel(logging.DEBUG)
    
    return main_logger

# ============================================================================

def save_frame(file_name_format, frame_number, frame, label_format):
    file_name = file_name_format % frame_number
    label = label_format % frame_number
    
    log.debug("Saving %s as '%s'", label, file_name)
    cv2.imwrite(file_name, frame)

# ============================================================================
    

    
# ============================================================================

def process_frame(frame_number, frame, keypoint_data, detector, matcher):
    log = logging.getLogger("process_frame")
    log.debug("Process frame:")
    # Create a copy of source frame to draw into
    processed = frame.copy()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp, des = detector.detectAndCompute(frame, None)
    log.debug("detectAndCompute complete")
    # Match descriptors
    matches = matcher.match(keypoint_data.descriptors, des) # 2.4.9 "home made"
    #matches = cv2.drawMatches(keypoint_data.descriptors, des)  # 3.0.0
    
    # Sort them in order of distance
    matches = sorted(matches, key = lambda x:x.distance)
    
    processed = drawMatches(cv2.imread('car.png',0), keypoint_data.keypoints, gray_frame, kp, matches[:])
    
    return processed
    
# ============================================================================

def main():
    print "start Main()"
    log = logging.getLogger("main")
    
    log.debug("Loading keypoint data from '%s'...", KEYPOINT_DATA_FILE)
    try:
        keypoint_data = KeypointData.load(KEYPOINT_DATA_FILE)
#        KeypointData(keypoints, descriptors)
        print "Loaded keypoints"
    except:
        log.debug("failed to load keypoints")
        log.debug("Attempting to create keypoint data")
        base_image = cv2.imread("car.png")
        base_processed = base_image.copy()
        base_gray = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)
        
        base_sift = cv2.xfeatures2d.SIFT_create(nfeatures=0, nOctaveLayers=5, contrastThreshold=0.05, edgeThreshold=30, sigma=1.5)
        
        (base_kpts, base_desc) = base_sift.detectAndCompute(base_image, None)
        
        
    log.debug("Creating SIFT detector...")
#    sift = cv2.SIFT(nfeatures=0, nOctaveLayers=5, contrastThreshold=0.05, edgeThreshold=30, sigma=1.5)
    sift = cv2.xfeatures2d.SIFT_create(nfeatures=0, nOctaveLayers=5, contrastThreshold=0.05, edgeThreshold=30, sigma=1.5)
    bf = cv2.BFMatcher()

    # Set up image source
    log.debug("Initializing video capture device #%s...", IMAGE_SOURCE)
    cap = cv2.VideoCapture(IMAGE_SOURCE)
    
##    frame_width = cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)     #
##    frame_height = cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)   #
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)       # OpenCV 3.0.0
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)     # OpenCV 3.0.0
    log.debug("Video capture frame size=(w=%d, h=%d)", frame_width, frame_height)

    log.debug("Starting capture loop...")
    frame_number = -1
    while True:
        frame_number += 1
        log.debug("Capturing frame #%d...", frame_number)
        ret, frame = cap.read()
        if not ret:
            log.error("Frame capture failed, stopping...")
            break

        log.debug("Got frame #%d: shape=%s", frame_number, frame.shape)
        
        
        # Archive raw frames from video to disk for later inspection/testing
        if CAPTURE_FROM_VIDEO:
            save_frame(IMAGE_FILENAME_FORMAT
                , frame_number, frame, "source frame #%d")
        
        log.debug("Processing frame #%d...", frame_number)
        
        #processed = process_frame(frame_number, frame, keypoint_data, sift, bf)
        ##          process_frame(frame_number, frame, keypoint_data, detector, matcher)
        processed = process_frame(frame_number, frame, (base_kpts, base_desc), sift, bf)
        
        save_frame(IMAGE_DIR + "/processed_%04d.png"
            , frame_number, processed, "processed frame #%d")
        
        cv2.imshow('Source Image', frame)
        cv2.imshow('Processed Image', processed)
        
        log.debug("Frame #%d processed.", frame_number)
        
        c = cv2.waitKey(WAIT_TIME)
        if c == 27:
            log.debug("ESC detected, stopping...")
            break

    log.debug("Closing video capture device...")
    cap.release()
    cv2.destroyAllWindows()
    log.debug("Done.")

# ============================================================================

if __name__ == "__main__":
    log = init_logging()
    print "log init"
    if not os.path.exists(IMAGE_DIR):
        log.debug("Creating image directory `%s`...", IMAGE_DIR)
        os.makedirs(IMAGE_DIR)
        "Image dir created"
    main()
    
