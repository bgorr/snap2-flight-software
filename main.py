import VNIRCamera
#import SWIRCamera
import IMU
import NeuralNet
import INSMessages
import Thermal
import GimbalControl
import Watchdog
import Controller
import numpy as np
import Jetson.GPIO as GPIO
import os
import logging

def main():
    
    directoryCount = 0
    directoryCreated = False
    while(directoryCreated == False):
        dirPath = "./runs/run"+str(directoryCount)
        logging.basicConfig(filename='errors'+str(directoryCount)+'.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        try:
            os.mkdir(dirPath)
            directoryCreated = True
        except:
            directoryCount += 1
    try:
        controller = Controller.Controller(dirPath)
        gc = GimbalControl.GimbalControl()
        gc.enable_driver()
        while True:
            gc.scan_pattern(controller)
    except Exception as e:
        gc.motor_alt_pwm.stop()
        gc.motor_az_pwm.stop()
        print(e)
        e.printStackTrace()
        GPIO.cleanup()
    finally:
        gc.motor_alt_pwm.stop()
        gc.motor_az_pwm.stop()
        GPIO.cleanup()
        

if __name__ == "__main__":
    main()