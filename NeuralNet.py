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
    for i in range(0,4):
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
    print("Number of plume pixels: "+count)
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
    def __init__(self,nn_setting,num_bands):
        if num_bands == 3:
            if nn_setting == "skeptical":
                self.nn = torch.jit.load("./trainednet_3s.pt")
            else:
                self.nn = torch.jit.load("./trainednet_3o.pt")
        elif num_bands == 4:
            if nn_setting == "skeptical":
                self.nn = torch.jit.load("./trainednet_4s.pt")
            else:
                self.nn = torch.jit.load("./trainednet_4o.pt")
        else:
            if nn_setting == "skeptical":
                self.nn = torch.jit.load("./trainednet_5s.pt")
            else:
                self.nn = torch.jit.load("./trainednet_5o.pt")
        self.nn_3s = torch.jit.load("./trainednet_3s.pt")
        self.nn_4s = torch.jit.load("./trainednet_4s.pt")
        self.nn_5s = torch.jit.load("./trainednet_5s.pt")
        self.nn_3o = torch.jit.load("./trainednet_3o.pt")
        self.nn_4o = torch.jit.load("./trainednet_4o.pt")
        self.nn_5o = torch.jit.load("./trainednet_5o.pt")
    def perform_inference_3bands_skeptical(self,input):
        output = self.nn_3s.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0] 
    def perform_inference_3bands_optimistic(self,input):
        output = self.nn_3o.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0] 
    def perform_inference_4bands_optimistic(self,input):
        output = self.nn_4o.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0]
    def perform_inference_4bands_skeptical(self,input):
        output = self.nn_4s.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0]
    def perform_inference_5bands_skeptical(self,input):
        output = self.nn_5s.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0]
    def perform_inference_5bands_optimistic(self,input):
        output = self.nn_5o.forward(input)
        outputSigmoid = torch.sigmoid(output)
        outputThreshold = torch.gt(outputSigmoid,0.4)
        return outputThreshold[0][0]
    
    def run_nn(self,vnir_image,swir_image):
        processed_bands = preprocess(vnir_image)
        swir_processed = preprocess(swir_image)
        red_tiles = tile_images(processed_bands[0])
        green_tiles = tile_images(processed_bands[1])
        blue_tiles = tile_images(processed_bands[2])
        nir_tiles = tile_images(processed_bands[3])
        swir_tiles = tile_images(swir_processed)
        mask_tiles_3s = []
        mask_tiles_3o = []
        mask_tiles_4s = []
        mask_tiles_4o = []
        mask_tiles_5s = []
        mask_tiles_5o = []
        for i in range(20):
            stacked_tensor_3bands = torch.stack((torch.from_numpy(red_tiles[i]).float(),torch.from_numpy(green_tiles[i]).float(),torch.from_numpy(blue_tiles[i]).float())) # np has float64, need float
            stacked_tensor_4bands = torch.stack((torch.from_numpy(red_tiles[i]).float(),torch.from_numpy(green_tiles[i]).float(),torch.from_numpy(blue_tiles[i]).float(),torch.from_numpy(nir_tiles[i]).float())) # np has float64, need float
            stacked_tensor_5bands = torch.stack((torch.from_numpy(red_tiles[i]).float(),torch.from_numpy(green_tiles[i]).float(),torch.from_numpy(blue_tiles[i]).float(),torch.from_numpy(nir_tiles[i]).float(),torch.from_numpy(swir_tiles[i]).float())) # np has float64, need float
            #final_tensor = torch.stack((stacked_tensor))
            mask_tiles_3o.append(self.perform_inference_5bands_optimistic(torch.unsqueeze(stacked_tensor_3bands,0)))
            mask_tiles_3s.append(self.perform_inference_5bands_skeptical(torch.unsqueeze(stacked_tensor_3bands,0)))
            mask_tiles_4o.append(self.perform_inference_5bands_optimistic(torch.unsqueeze(stacked_tensor_4bands,0)))
            mask_tiles_4s.append(self.perform_inference_5bands_skeptical(torch.unsqueeze(stacked_tensor_4bands,0)))
            mask_tiles_5o.append(self.perform_inference_5bands_optimistic(torch.unsqueeze(stacked_tensor_5bands,0)))
            mask_tiles_5s.append(self.perform_inference_5bands_skeptical(torch.unsqueeze(stacked_tensor_5bands,0)))
        full_mask_3s = untile_mask(mask_tiles_3s)
        (x_3s,y_3s) = get_centroid(full_mask_3s)
        full_mask_3o = untile_mask(mask_tiles_3o)
        (x_3o,y_3o) = get_centroid(full_mask_3o)
        full_mask_4s = untile_mask(mask_tiles_4s)
        (x_4s,y_4s) = get_centroid(full_mask_4s)
        full_mask_4o = untile_mask(mask_tiles_4o)
        (x_4o,y_4o) = get_centroid(full_mask_4o)
        full_mask_5s = untile_mask(mask_tiles_5s)
        (x_5s,y_5s) = get_centroid(full_mask_5s)
        full_mask_5o = untile_mask(mask_tiles_5o)
        (x_5o,y_5o) = get_centroid(full_mask_5o)
        return full_mask_5s, x_5s, y_5s