from vnpy import *

class IMU():
    def __init__(self):
        self.s = VnSensor()
        self.s.connect("/dev/ttyUSB0",115200)
    
    def get_ypr(self):
        ypr = self.s.read_yaw_pitch_roll()
        return [ypr.x, ypr.y, ypr.z]
