import VNIRCamera
import SWIRCamera
import IMU
import NeuralNet
import INSMessages
import Thermal
import GimbalControl
import Watchdog
import numpy as np
import os

class Controller():
    def __init__(self,dirpath):
        self.count = 0
        self.imu = IMU.IMU()
        self.vnir_cam = VNIRCamera.VNIRCamera()
        self.neural_net = NeuralNet.NeuralNet()
        self.ins_messages = INSMessages.INSMessages()
        self.thermal = Thermal.Thermal()
        self.plume_state = False
        self.plume_pos = (0,0)
        self.plume_lost_count = 0
        self.image_path = dirpath+"/images/"
        self.telemetry_path = dirpath+"/telemetry/"
        if not os.path.exists(self.image_path):
            os.mkdir(self.image_path)
        if not os.path.exists(self.telemetry_path):
            os.mkdir(self.telemetry_path)
        self.swir_cam = SWIRCamera.SWIRCamera()
        #watchdog = Watchdog.Watchdog()

    def save_telemetry(self,tel,count):
        tel_file = open(self.telemetry_path+"telemetry_"+str(count)+".txt","w")
        for item in tel:
            tel_file.write(item+"\n")
        tel_file.close()

    def save_imagery(self,vnir_images,swir_image,mask_image,count):
        np.savetxt(self.image_path+"red_"+str(count)+".csv", vnir_images[0].astype(int), delimiter=",",fmt="%d")
        np.savetxt(self.image_path+"green_"+str(count)+".csv", vnir_images[1].astype(int), delimiter=",",fmt="%d")
        np.savetxt(self.image_path+"blue_"+str(count)+".csv", vnir_images[2].astype(int), delimiter=",",fmt="%d")
        np.savetxt(self.image_path+"nir_"+str(count)+".csv", vnir_images[3].astype(int), delimiter=",",fmt="%d")
        np.savetxt(self.image_path+"mask_"+str(count)+".csv", mask_image.astype(int), delimiter=",",fmt="%d")
        if swir_image is not None:
            np.savetxt(self.image_path+"swir_"+str(count)+".csv", swir_image.astype(int), delimiter=",",fmt="%d")

    def data_capture(self,gc_angles):
        telemetry = []
        swir_image = self.swir_cam.take_image()
        vnir_image = self.vnir_cam.get_image()
        mask, x, y = self.neural_net.run_nn(vnir_image)
        self.plume_pos = (x,y)
        if x != 0 or y != 0:
            self.plume_state = True
        else:
            if self.plume_state == True:
                self.plume_lost_count += 1
        if self.plume_lost_count > 10:
            self.plume_lost_count = 0
            self.plume_state = False
        self.save_imagery(vnir_image,swir_image,mask,self.count)
        telemetry_list = ["Thermistor temps: "+self.thermal.get_thermistor_temps(),
                            "Jetson temps: "+str(self.thermal.get_jetson_temps()),
                            "IMU temps: "+str(self.imu.get_temperature()),
                            "INS message: "+self.ins_messages.readINSmessage(),
                            "IMU YPR: "+str(self.imu.get_ypr()),
                            "Encoder angles: "+str(gc_angles),
                            "Plume position: "+str(self.plume_pos)]
        self.save_telemetry(telemetry_list,self.count)
        self.count += 1