import numpy as np
import torch

def tile_images(large_img):
    small_images = []
    for i in range(0,4):
        for j in range(0,3):
            small_images.append(large_img[j*161:(j+1)*161,i*105:(i+1)*105])
        small_images.append(large_img[512-161:512,i*105:(i+1)*105])
    small_images.append(large_img[0:161,512-105:512])
    small_images.append(large_img[161:322,512-105:512])
    small_images.append(large_img[322:322+161,512-105:512])
    small_images.append(large_img[512-161:512,512-105:512])
    return small_images

def untile_mask(small_images):
    full_mask = np.zeros(shape=(512,512))
    for i in range(0,3):
        for j in range(0,3):
            full_mask[j*161:(j+1)*161,i*105:(i+1)*105] = small_images[3*i+j]
        full_mask[483:512,i*105:(i+1)*105] = small_images[3*i+3][132:161,0:105]
    full_mask[0:161,420:512] = small_images[16][0:161,13:105]
    full_mask[161:322,420:512] = small_images[17][0:161,13:105]
    full_mask[322:483,420:512] = small_images[18][0:161,13:105]
    full_mask[483:512,420:512] = small_images[19][132:161,13:105]
    return full_mask

def get_centroid(image):
    x_sum = 0
    y_sum = 0
    count = 0
    for i in range(len(image[:,0])):
        for j in range(len(image[0,:])):
            if image[i,j] > 0.5:
                x_sum = x_sum + i
                y_sum = y_sum + j
                count = count + 1
    #print(count)
    if count > 0 and count < 1000:
        print("Plume detected!")
        x_loc = x_sum/count
        y_loc = y_sum/count
        print((x_loc,y_loc))
        return (x_loc,y_loc)
    return(0,0)

def preprocess(bands):
    for band in bands:
        band = (band-np.average(band))/np.std(band)
    return bands

class NeuralNet():
    def __init__(self):
        self.nn = torch.jit.load("./trainednet.pt")
    
    def perform_inference(self,input):
        output = self.nn.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.66)
        return outputThreshold[0][0]
    
    def run_nn(self,image):
        processed_bands = preprocess(image)
        red_tiles = tile_images(processed_bands[0])
        green_tiles = tile_images(processed_bands[1])
        blue_tiles = tile_images(processed_bands[2])
        nir_tiles = tile_images(processed_bands[3])
        mask_tiles = []
        for i in range(20):
            stacked_tensor = torch.stack((torch.from_numpy(red_tiles[i]).float(),torch.from_numpy(green_tiles[i]).float(),torch.from_numpy(blue_tiles[i]).float(),torch.from_numpy(nir_tiles[i]).float())) # np has float64, need float
            #final_tensor = torch.stack((stacked_tensor))
            mask_tiles.append(self.perform_inference(torch.unsqueeze(stacked_tensor,0)))
        full_mask = untile_mask(mask_tiles)
        (x,y) = get_centroid(full_mask)
        return full_mask, x, y