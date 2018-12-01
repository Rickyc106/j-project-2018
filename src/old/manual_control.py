#!/usr/bin/env python

# Import required modules
import time
import RPi.GPIO as GPIO

# Define global objects
global l_pwm, r_pwm

def initialize(l_pin, r_pin):
        # Declare the GPIO settings
        GPIO.setmode(GPIO.BOARD)
        if (GPIO.getmode() == None):
                print "Warning: GPIO Mode not set"
        else:
                print "GPIO Mode set to: ", GPIO.getmode()

        # set up GPIO pins
        GPIO.setup(l_pin, GPIO.OUT) # Connected to left motor PWM
        GPIO.setup(r_pin, GPIO.OUT) # Connected to right motor PWM

        # Create PWM objects
        l_pwm = GPIO.PWM(l_pin, 1000) # Pin number, Frequency
        r_pwm = GPIO.PWM(r_pin, 1000)

        # Set the motor speed
        l_pwm.start(0) # Start PWM at 0%
        r_pwm.start(0)

# Stops both motors
def motor_stop():
        l_pwm.stop()
        r_pwm.stop()

# Turns forwards then turns backwards. Repeats until process dies.
def control():
        for i in range(2):
                for x in range(100):
                        l_pwm.ChangeDutyCycle(x)
                        r_pwm.ChangeDutyCycle(x)

                        sleep(0.01)
                        
                for x in range(100, 0, -1):
                        l_pwm.ChangeDutyCycle(x)
                        r_pwm.ChangeDutyCycle(x)

                        sleep(0.01)

if __name__ == "__main__":
        try:
                initialize(12, 13)
                control()

        except KeyboardInterrupt:
                motor_stop()   # Stops motors on Keyboard Interrupt
                GPIO.cleanup() # Makes all outputs LOW
