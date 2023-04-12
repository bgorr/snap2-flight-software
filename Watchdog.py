import time
import Jetson.GPIO as GPIO
import datetime
import os
import io

def run_watchdog():
    # setup all pins
    wdi_pin = 21
    # setup all pins to be used
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(wdi_pin, GPIO.OUT)

    for i in range(1000):
        GPIO.output(wdi_pin,GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(wdi_pin,GPIO.LOW)
        time.sleep(40)