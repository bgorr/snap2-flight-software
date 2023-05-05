import VNIRCamera
import numpy as np
from PIL import Image

vnir_cam = VNIRCamera.VNIRCamera()
vnir_cam.get_image()
vnir_image = vnir_cam.get_image()

rgb_array = np.dstack([vnir_image[0],vnir_image[1],vnir_image[2]])
image = np.asarray(rgb_array,dtype=np.uint8)
rgb_pil = Image.fromarray(image , "RGB")
rgb_pil.save('./utils/images/rgb.png')

red_image = np.asarray(vnir_image[0],dtype=np.uint8)
red_pil = Image.fromarray(red_image)
red_pil.save('./utils/images/red.png')

green_image = np.asarray(vnir_image[1],dtype=np.uint8)
green_pil = Image.fromarray(green_image)
green_pil.save('./utils/images/green.png')

blue_image = np.asarray(vnir_image[2],dtype=np.uint8)
blue_pil = Image.fromarray(blue_image)
blue_pil.save('./utils/images/blue.png')

nir_image = np.asarray(vnir_image[3],dtype=np.uint8)
nir_pil = Image.fromarray(nir_image)
nir_pil.save('./utils/images/nir.png')