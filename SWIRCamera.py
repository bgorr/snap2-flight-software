import cv2
import logging

class SWIRCamera():
    def __init__(self):
        self.camera = 0                
        
    def take_image(self):
        try:
            cam = cv2.VideoCapture(self.camera,cv2.CAP_V4L2)
            ret, frame = cam.read()
            return self.crop_center(frame,512,512)
        except Exception:
            logging.exception("Error taking SWIR image.")
            return 0

    def crop_center(self,img,cropx,cropy):
        x = img.shape[1]
        y = img.shape[0]
        startx = x//2 - (cropx//2)
        starty = y//2 - (cropy//2)
        return img[starty:starty+cropy,startx:startx+cropx,0]

