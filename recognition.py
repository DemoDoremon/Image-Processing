import cv2
import io
import picamera
import numpy as np
import os 
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('/home/pi/Desktop/Image-Processing-master/trainer/trainer.yml')
cascadePath = "/home/pi/Desktop/Image-Processing-master/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
#iniciate id counter
id = 0
# names related to ids: example ==> Marcelo: id=1,  etc
names = ['none', 'Demodoremon', 'Obama'] 
while True:
    #Create a memory stream so photos doesn't need to be saved in a file
    stream = io.BytesIO()

    #Get the picture (low resolution, so it should be quite fast)
    #Here you can also specify other parameters (e.g.:rotate the image)
    with picamera.PiCamera() as camera:
        camera.resolution = (320, 240)
        camera.capture(stream, format ='jpeg')

    #Convert the picture into a numpy array
    buff = np.fromstring(stream.getvalue(), dtype = np.uint8)

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
        id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
        # Check if confidence is less them 100 ==> "0" is perfect match 
        if (confidence < 100):
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
        
        cv2.putText(image, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
        cv2.putText(image, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        print(x,y,w,h)
        
    cv2.imshow("Frame", image)
    if cv2.waitKey(1) & 0xff == ord("q"):
	    exit()
    stream.truncate(0)
    stream.seek(0)
