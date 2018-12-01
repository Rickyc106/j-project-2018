#!/usr/bin/env python

# Import required modules
import time
import numpy as np
import cv2

from picamera import PiCamera
from picamera.array import PiRGBArray

class VisionNode:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (640,480)
        self.camera.framerate = 90
        self.rawCapture = PiRGBArray(self.camera, size=(640,480))
    
    def find_white(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        lower_white = np.array([0,0,0], dtype=np.uint8)
        upper_white = np.array([255,0,255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower_white, upper_white)
        res = cv2.bitwise_and(image, image, mask=mask)

        return res

    def find_distance(self, marker):
        known_distance = 18 # in
        known_width = 5.5 # in
        px = 370 # pixels
        focal_length = 1210.909091 # pixels
        
        distance = (known_width * focal_length) / marker
        return distance
        
        #actual_focal_length = 3.04 # mm

    def new_find_marker(self, image):
        # red color boundaries (R,B and G)

        lv = 150
        uv = 255
        
        lower = [lv, lv, lv]
        upper = [uv, uv, uv]

        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(image, lower, upper)
        output = cv2.bitwise_and(image, image, mask=mask)

        ret,thresh = cv2.threshold(mask, 40, 255, 0)
        im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            # draw in blue the contours that were founded
            cv2.drawContours(output, contours, -1, 255, 3)

            #find the biggest area
            c = max(contours, key = cv2.contourArea)

            x,y,w,h = cv2.boundingRect(c)
            # draw the book contour (in green)
            cv2.rectangle(output,(x,y),(x+w,y+h),(0,255,0),2)

        else:
            w = -1

        # show the images
        cv2.imshow("Result", np.hstack([image, output]))

        return w
        
    def main(self):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            masked_white_img = self.find_white(image)

            #cv2.namedWindow('Raw Image', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Resized Image', 640,480)
            #cv2.imshow('Raw Image', approx)
            #cv2.imshow('White Image', masked_white_img)

            marker = self.new_find_marker(image)
            # Distance in Inches
            distance = self.find_distance(marker)
            print "Measured distance is approximately: {} inches".format(distance)

            key = cv2.waitKey(1) & 0xFF

            self.rawCapture.truncate(0)

            if key == ord("q"):
                break

            time.sleep(0.01)

if __name__ == '__main__':
    try:
        vn = VisionNode()
        vn.main()
    except KeyboardInterrupt:
        pass
        
