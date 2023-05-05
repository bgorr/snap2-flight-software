import matplotlib.pyplot as plt
import os
import numpy as np

path = "/mnt/c/Users/Ben/tvac_test_042423/telemetry_run3/"

num_files = len(os.listdir(path))
jetson_internal_temps = np.zeros(shape=(num_files))
jetson_external_temps = np.zeros(shape=(num_files))
vnir_camera_temps = np.zeros(shape=(num_files))
swir_camera_temps = np.zeros(shape=(num_files))
imu_internal_temps = np.zeros(shape=(num_files))
for file in os.listdir(path):
    textfile = open(path+file,'r')
    numstr = file.removeprefix("telemetry_")
    numstr = numstr.removesuffix(".txt")
    filenum = int(numstr)
    lines = textfile.readlines()
    for line in lines:
        tokens = line.split(":",1)
        if tokens[0] == "Thermistor temps":
            thermistor_tokens = tokens[1].split(",")
            for tt in thermistor_tokens:
                tok = tt.split(":")
                if tok[0] == "relief":
                    jetson_external_temps[filenum] = float(tok[1])
                elif tok[0] == "vnircam":
                    vnir_camera_temps[filenum] = float(tok[1])
                elif tok[0] == "swircam":
                    swir_camera_temps[filenum] = float(tok[1])
        elif tokens[0] == "Jetson temps":
            jetson_tokens = tokens[1].split(",")
            for jt in jetson_tokens:
                tok = jt.split(":")
                if tok[0] == " thermal":
                    jetson_internal_temps[filenum] = float(tok[1])
        elif tokens[0] == "IMU temps":
            imu_internal_temps[filenum] = float(tokens[1])

plt.plot(jetson_internal_temps)
plt.plot(jetson_external_temps)
plt.plot(imu_internal_temps)
plt.plot(vnir_camera_temps)
plt.plot(swir_camera_temps)
plt.legend(["Jetson internal", "Jetson external", "IMU internal", "VNIR camera", "SWIR camera"])
plt.xlabel("Time")
plt.ylabel("Temperature (deg C)")
plt.show()
