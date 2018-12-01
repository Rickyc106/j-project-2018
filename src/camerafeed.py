#!/usr/bin/env python

import time
import cv2
import numpy as np
from serial_node import *

cam = cv2.VideoCapture(0)

def find_green(image):
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	# Color Picker: [0-360, 0-100, 0-100]
	# OpenCV: [0-180, 0-255, 0-255]
	# Green (Color Picker): [121, 100, 100]
	# Green (OpenCV): [60.5, 255, 255]
	lower_green = np.array([55,0,200], dtype=np.uint8)
	upper_green = np.array([65,255,255], dtype=np.uint8)

	mask = cv2.inRange(hsv, lower_green, upper_green)
	res = cv2.bitwise_and(image, image, mask=mask)

	return res

def find_distance(marker):
	known_distance = 18 # in
	known_width = 5.5 # in
	px = 370 # pixels
	focal_length = 1210.909091 # pixels
	
	distance = (known_width * focal_length) / marker
	return distance

def new_find_marker(image):
	# red color boundaries (R,B and G)

	lv = 250
	uv = 255
	
	lower = [10, 240, 10]
	upper = [220, 255, 180]

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

		center_x = x + w/2
		center_y = y + h/2

	else:
		center_x = 0
		w = -1

	# show the images
	cv2.imshow("Result", np.hstack([image, output]))

	return w, center_x

def constrain(value, lo, hi):
		if value < lo:
			value = lo
		elif value > hi:
			value = hi
		else:
			pass

		return value

def mapf(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def main():
	SN = SerialNode('/dev/ttyACM0', 115200, 1)

	ETout = SN.begin("float", 4)
	ETin = SN.begin("float", 4)

	while True:
		ret, image = cam.read()
		height, width, channels = image.shape

		half_width = width / 2

		if ret:
			masked_green_img = find_green(image)
			cv2.imshow('RawImage', image)

			marker, center_x = new_find_marker(image)
			distance = find_distance(marker)

			if center_x < half_width:
				pwm = float(half_width - center_x) / float(half_width)

				left_forward = 0.0
				right_forward = 0.0

				default = 0.6
				pwm = mapf(pwm, 0.0, 1.0, 0.0, 1-default)

				left_pwm = default - pwm
				right_pwm = default + pwm

				left_pwm = constrain(left_pwm, 0.0, 1.0)
				right_pwm = constrain(right_pwm, 0.0, 1.0)

			else:
				pwm = float(center_x - half_width) / float(half_width)

				left_forward = 0.0
				right_forward = 0.0

				default = 0.6
				pwm = mapf(pwm, 0.0, 1.0, 0.0, 1-default)

				left_pwm = default + pwm
				right_pwm = default - pwm

				left_pwm = constrain(left_pwm, 0.0, 1.0)
				right_pwm = constrain(right_pwm, 0.0, 1.0)

			data_out = [left_pwm, right_pwm, left_forward, right_forward]
		
		SN.main(ETout, ETin, data_out)

			#print "Distance: {} inches | Center X: {} | PWM: {}".format(distance, center_x, pwm)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	
	cam.release()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass