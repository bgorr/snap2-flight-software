import matplotlib.pyplot as plt
import os
import numpy as np

path = "/mnt/c/Users/Ben/tvac_test_042423/telemetry_run1/"

num_files = len(os.listdir(path))
imu_yaw = np.zeros(shape=(num_files))
imu_pitch = np.zeros(shape=(num_files))
imu_roll = np.zeros(shape=(num_files))
azs = np.zeros(shape=(num_files))
els = np.zeros(shape=(num_files))
for file in os.listdir(path):
    textfile = open(path+file,'r')
    numstr = file.removeprefix("telemetry_")
    numstr = numstr.removesuffix(".txt")
    filenum = int(numstr)
    lines = textfile.readlines()
    for line in lines:
        tokens = line.split(":",1)
        if tokens[0] == "IMU YPR":
            ypr = tokens[1].removeprefix(" [")
            ypr = ypr.removesuffix("]\n")
            ypr_tokens = ypr.split(",")
            yaw = ypr_tokens[0]
            pitch = ypr_tokens[1]
            roll = ypr_tokens[2]
            imu_yaw[filenum] = float(yaw)
            imu_pitch[filenum] = float(pitch)
            imu_roll[filenum] = float(roll)
        elif tokens[0] == "Encoder angles":
            azel = tokens[1].removeprefix(" (")
            azel = azel.removesuffix(")\n")
            azel_tokens = azel.split(",")
            az = azel_tokens[0]
            el = azel_tokens[1]
            azs[filenum] = float(az)
            els[filenum] = float(el)

plt.plot(imu_roll)
plt.plot(azs)
plt.xlabel("Time")
plt.ylabel("Angle (deg)")
plt.legend(["Roll","Altitude"])
plt.show()
