import VNIRCamera
import IMU

def main():
    imu = IMU.IMU()
    vnir_cam = VNIRCamera.VNIRCamera()
    for i in range(0,10):
        print("xd")
        print(imu.get_ypr())
        print(vnir_cam.get_image())

if __name__ == "__main__":
    main()