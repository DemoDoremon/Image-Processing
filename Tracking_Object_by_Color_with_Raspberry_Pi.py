import cv2
import argparse
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera 
 
def callback(value):
    pass
 
 
def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)
 
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
 
        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)
 
 
def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--filter', required=True,
                    help='Range filter.HSV')
    ap.add_argument('-c', '--camera', required=False,
                    help='picamera', action='store_true')
    args = vars(ap.parse_args())
 
    if not args['filter'].upper() in ['HSV']:
        ap.error("Please speciy a correct filter.")
 
    return args
 
 
def get_trackbar_values(range_filter):
    values = []
 
    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)
    return values
 
args = get_arguments()
range_filter = args['filter'].upper()
setup_trackbars(range_filter)
# initialize the camera and grab a reference to the raw camera capture 
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(320, 240))
 
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    if args['camera']:
        image = frame.array
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
 
    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
 
    thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
 
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    resultHSV = cv2.bitwise_and(image,image, mask= mask)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(image, center, 3, (0, 0, 255), -1)
            cv2.putText(image,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
            cv2.putText(image,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
 
    # show the frame to your screen
    cv2.imshow("Original", image)
    cv2.imshow("Detected", resultHSV)
    cv2.imshow("Mask", mask)
    #wait for 'q' key was pressed and break from the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
