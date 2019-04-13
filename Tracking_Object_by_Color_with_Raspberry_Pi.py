import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera 

def nothing(x):
    pass

# create Trackbars
cv2.namedWindow("Trackbars")
cv2.createTrackbar("H_min", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("S_min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("V_min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("H_max", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("S_max", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("V_max", "Trackbars", 255, 255, nothing)


# initialize the camera and grab a reference to the raw camera capture 
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(320, 240))

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    image = frame.array

    # converting frame(img == BGR) to HSV(hue-saturation-value)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # get value Trackbars
    H_min = cv2.getTrackbarPos("H_min", "Trackbars")
    S_min = cv2.getTrackbarPos("S_min", "Trackbars")
    V_min = cv2.getTrackbarPos("V_min", "Trackbars")
    H_max = cv2.getTrackbarPos("H_max", "Trackbars")
    S_max= cv2.getTrackbarPos("S_max", "Trackbars")
    V_max= cv2.getTrackbarPos("V_max", "Trackbars")

    # Morphological Transformations,Opening and Closing
    thresh = cv2.inRange(hsv, np.array([H_min, S_min, V_min]), np.array([H_max, S_max, V_max]))
    kernel = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    result = cv2.bitwise_and(image,image, mask= mask)
 
    # find contours in the mask and initialize the current (x, y) center of the Objective
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
    # only proceed if at least one contour was found
    if len(cnts) > 0:

        # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
        # only proceed if the radius meets a minimum size
        if radius > 10:

            # draw the circle and centroid on the frame, then update the list of tracked points
            cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2)
            cv2.circle(image, center, 3, (0, 0, 255), -1)
            cv2.putText(image,"centroid", (center[0]+10,center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
            cv2.putText(image,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 0, 255),1)
 
    # show the frame to our screen
    cv2.imshow("Original", image)
    cv2.imshow("Detected", result)
    cv2.imshow("Mask", mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        exit()
    rawCapture.truncate(0)
    cv2.destroyAllWindows()
