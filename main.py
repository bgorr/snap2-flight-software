import VNIRCamera
import SWIRCamera
import IMU
import NeuralNet
import INSMessages
import Thermal
import GimbalControl
import Watchdog
import numpy as np


def save_telemetry(tel,count):
    print("Saving telemetry")

def save_imagery(vnir_images,swir_image,mask_image,count):
    np.savetxt("./images/red_"+str(count)+".csv", vnir_images[0].astype(int), delimiter=",",fmt="%d")
    np.savetxt("./images/green_"+str(count)+".csv", vnir_images[1].astype(int), delimiter=",",fmt="%d")
    np.savetxt("./images/blue_"+str(count)+".csv", vnir_images[2].astype(int), delimiter=",",fmt="%d")
    np.savetxt("./images/nir_"+str(count)+".csv", vnir_images[3].astype(int), delimiter=",",fmt="%d")
    np.savetxt("./images/mask_"+str(count)+".csv", mask_image.astype(int), delimiter=",",fmt="%d")

def main():
    #imu = IMU.IMU()
    vnir_cam = VNIRCamera.VNIRCamera()
    neural_net = NeuralNet.NeuralNet()
    ins_messages = INSMessages.INSMessages()
    #thermal = Thermal.Thermal()
    #swir_cam = SWIRCamera.SWIRCamera()
    #gimbal_control = GimbalControl.GimbalControl()
    #watchdog = Watchdog.Watchdog()

    for i in range(0,10):
        telemetry = []
        print("xd")
        #print(imu.get_ypr())
        #print(vnir_cam.get_image())
        vnir_image = vnir_cam.get_image()
        mask, x, y = neural_net.run_nn(vnir_image)
        save_imagery(vnir_image,None,mask,i)
        

if __name__ == "__main__":
    main()