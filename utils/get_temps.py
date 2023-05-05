import Thermal
import IMU

thermal = Thermal.Thermal()
imu = IMU.IMU()
temps = ["Thermistor temps: "+thermal.get_thermistor_temps(),
                            "Jetson temps: "+str(thermal.get_jetson_temps()),
                            "IMU temps: "+str(imu.get_temperature())]
for temp in temps:
    print(temp)