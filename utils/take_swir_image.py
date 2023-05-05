import SWIRCamera
import numpy as np
from PIL import Image

swir_cam = SWIRCamera.SWIRCamera()
swir_image = swir_cam.take_image()

swir_image = np.asarray(swir_image,dtype=np.uint8)
swir_pil = Image.fromarray(swir_image)
swir_pil.save('./utils/images/swir.png')