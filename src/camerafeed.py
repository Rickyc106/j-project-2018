#!/usr/bin/env python

# Import required modules
import time
import RPi.GPIO as GPIO

# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)
if (GPIO.getmode() == None):
	print "Warning: GPIO Mode not set properly"