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

def main():
    directoryCount = 0
    directoryCreated = False
    while(directoryCreated == False):
        dirPath = "./runs/run"+str(directoryCount)
        try:
            os.mkdir(dirPath)
            directoryCreated = True
        except:
            directoryCount += 1
    try:
        controller = Controller.Controller(dirPath)
        for i in range(10):
            controller.data_capture((0,0))
    except Exception as e:
        print(e)
        e.printStackTrace()
        

if __name__ == "__main__":
    main()