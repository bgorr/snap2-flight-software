import VNIRCamera
import SWIRCamera
import NeuralNet
import numpy as np
from PIL import Image

vnir_cam = VNIRCamera.VNIRCamera(0)

swir_cam = SWIRCamera.SWIRCamera()

neural_net = NeuralNet.NeuralNet("automatic",5)

swir_image = swir_cam.take_image()
vnir_image = vnir_cam.get_image()
mask, x, y = neural_net.run_all_nns(vnir_image,swir_image)