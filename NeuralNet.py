import numpy as np
import torch

class NeuralNet():
    def __init__:
        torch.load()
    
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
        full_mask = np.zeros(512,512)
        for i in range(0,3):
            for j in range(0,3):
                full_mask[j*161:(j+1)*161,i*105:(i+1)*105] = small_images[3*i+j]
            full_mask[483:512,i*105] = small_images[3*i+3][132:161,0:105]
        full_mask[0:161,420:512] = small_images[16][0:161,13:105]
        full_mask[161:322,420:512] = small_images[17][0:161,13:105]
        full_mask[322:483,420:512] = small_images[18][0:161,13:105]
        full_mask[483:512,420:512] = small_images[19][132:161,13:105]

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
        if count > 0 and count < 1000:
            print("Plume detected!")
        x_loc = x_sum/count
        y_loc = y_sum/count
        return (x_loc,y_loc)