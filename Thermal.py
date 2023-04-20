import serial
import os

class Thermal():
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=57600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout=1
        )
    def get_jetson_temps(self):
        temps = os.popen("cat /sys/devices/virtual/thermal/thermal_zone*/temp").read()
        temps = temps.split('\n')
        zones = ["AO","CPU","GPU","PLL","PMIC","thermal"]
        temp_list = []
        count = 0
        for temp in temps:
            if(count > 5):
                break
            temp_list.append(zones[count]+": "+str(float(temp)/1000))
            count += 1
        return ", ".join(temp_list)
    def get_thermistor_temps(self):
        raw_serial = self.ser.readline()
        raw_str = raw_serial.decode()
        value = raw_str.rstrip('\r\n')
        return value