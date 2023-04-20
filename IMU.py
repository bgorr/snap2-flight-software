from vnpy import *

class IMU():
    def __init__(self):
        self.s = VnSensor()
        self.s.connect("/dev/ttyUSB0",115200)
    
    def get_ypr(self):
        ypr = self.s.read_yaw_pitch_roll()
        return [ypr.x, ypr.y, ypr.z]

    def get_temperature(self):
        register = self.s.read_imu_measurements()
        return register.temp

    def get_accelerations(self):
        accels = self.s.acceleration
        return accels