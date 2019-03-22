import io
import picamera
import cv2
import numpy as np
i=0
name =input("\n Enter user id :")
while True:
    #Create a memory stream so photos doesn't need to be saved in a file
    stream = io.BytesIO()

    #Get the picture (low resolution, so it should be quite fast)
    #Here you can also specify other parameters (e.g.:rotate the image)
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.capture(stream, format='jpeg')

    #Convert the picture into a numpy array
    buff = np.fromstring(stream.getvalue(), dtype=np.uint8)

    #Now creates an OpenCV image
    image = cv2.imdecode(buff, 1)
    #Load a cascade file for detecting faces
    face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/Image-Processing-master/haarcascade_frontalface_default.xml')
    #Convert to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Look for faces in the image using the loaded cascade file
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 5, minSize = (100, 100), flags = cv2.CASCADE_SCALE_IMAGE)

    print ("Found "+str(len(faces))+" face(s)")
    #Draw a rectangle around every found face
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        print(x,y,w,h)
    #Save the result image
    if len(faces):
        i=i+1
        img_item = "dataSet/User."+ name + '.' + str(i) + ".jpg"
        cv2.imwrite(img_item,roi_gray)
        
    cv2.imshow("Frame", image)
    if cv2.waitKey(1) & 0xff == ord("q"):
	    exit()
    if i == 100:
        exit()
    stream.truncate(0)
    stream.seek(0)
