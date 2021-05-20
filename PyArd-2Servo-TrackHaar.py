import cv2
import serial
import time

arduinoSerial = serial.Serial('com3',baudrate=19200,timeout=1)
time.sleep(2)

faceCascade = cv2.CascadeClassifier('Resources/haarcascade_frontalface_default.xml')

dispWidth = 640
dispHeight = 480
pan = 90
tilt = 90

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(dispWidth))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,int(dispHeight))

while True:
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 4)

    for (x, y, w, h) in faces:
        faceCenterX = x + w / 2
        faceCenterY = y + h / 2
        errorPan = faceCenterX - dispWidth / 2
        errorTilt = faceCenterY - dispHeight / 2

        print(f'face center X:{faceCenterX} Y:{faceCenterY}')
        print(f'errorPan: {errorPan} errorTilt: {errorTilt}')

        if abs(errorPan) > 20:
            pan = pan - errorPan/35
        if pan > 160:
            pan = 160
            print("Out of range")
        if pan < 0:
            pan = 0
            print("out of range")
        if abs(errorTilt) > 20:
            tilt = tilt - errorTilt/35
        if tilt > 130:
            tilt = 130
            print("Out of range")
        if tilt < 40:
            tilt = 40
            print("out of range")

        pan = int(pan)
        tilt = int(tilt)
        # ArduinoSerial.write(str(chr(int(servoPos))))
        servoPos = (pan,tilt)
        data = 'X{0:.0f}Y{1:.0f}Z'.format(pan,tilt)
        arduinoSerial.write(data.encode())
        time.sleep(0.1)
        # print(data)
        # print(type(data))
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Frame',img)

    if cv2.waitKey(2) & 0xff == 27:
        break

cap.release()
cv2.destroyAllWindows()