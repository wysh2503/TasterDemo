import cv2
import numpy as np
import serial
import time

arduinoSerial = serial.Serial('COM3',baudrate=19200,timeout=1)
time.sleep(2)
pan = 90
tilt = 90

def nothing(): pass

cv2.namedWindow('Trackbars')

cv2.createTrackbar('HueLow','Trackbars',24,179,nothing)
cv2.createTrackbar('HueHigh','Trackbars',86,179,nothing)
cv2.createTrackbar('SatLow','Trackbars',139,255,nothing)
cv2.createTrackbar('SatHigh','Trackbars',255,255,nothing)
cv2.createTrackbar('ValLow','Trackbars',122,255,nothing)
cv2.createTrackbar('ValHigh','Trackbars',255,255,nothing)

# For different colors, below data for reference
# RED = (0,17,159,255,135,255)
# GREEN = (39,86,123,255,100,255)
# YELLOW = (8,34,191,255,130,255)
# BLUE = (92,128,101,255,105,255)

dispW = 640
dispH = 480
# Set up webcam
cam = cv2.VideoCapture(0)
cam.set(3,dispW)
cam.set(4,dispH)

# Start capturing and show frames on window
while True:
    success, img = cam.read()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hueLow = cv2.getTrackbarPos('HueLow','Trackbars')
    hueHigh = cv2.getTrackbarPos('HueHigh', 'Trackbars')
    satLow = cv2.getTrackbarPos('SatLow', 'Trackbars')
    satHigh = cv2.getTrackbarPos('SatHigh', 'Trackbars')
    valLow = cv2.getTrackbarPos('ValLow', 'Trackbars')
    valHigh = cv2.getTrackbarPos('ValHigh', 'Trackbars')

    FGmask = cv2.inRange(hsv, (hueLow,satLow,valLow),(hueHigh,satHigh,valHigh))
    cv2.imshow('FGmask',FGmask)

    contours, hierarchy = cv2.findContours(FGmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours,key=lambda x:cv2.contourArea(x),reverse=True)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        (x,y,w,h) = cv2.boundingRect(cnt)
        if area > 100:
            #cv2.drawContours(img,[cnt],0,(255,0,0),3)
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
            centX = x + w/2
            centY = y + h/2
            errorPan = centX - dispW/2
            errorTilt = centY - dispH/2
            if abs(errorPan) > 20:
                pan = pan - errorPan/30
            if pan > 160:
                pan = 160
                print('Out of range')
            if pan < 0:
                pan = 0
                print('Out of range')
            pan = int(pan)

            if abs(errorTilt) > 20:
                tilt = tilt - errorTilt/30
            if tilt > 160:
                tilt = 160
                print('Out of range')
            if tilt < 40:
                tilt = 40
                print('Out of range')
            tilt = int(tilt)

            data = 'X{0:.0f}Y{1:.0f}Z'.format(pan,tilt)
            arduinoSerial.write(data.encode())
            print(data)
            time.sleep(0.1)

    cv2.imshow('Frame', img)
    # cv2.moveWindow('Frame', 100,20)
    if cv2.waitKey(1) & 0xff == 27:
        break

cam.release()
cv2.destroyAllWindows()