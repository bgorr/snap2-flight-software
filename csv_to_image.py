from numpy import genfromtxt
import matplotlib.image

my_data = genfromtxt('./runs/run74/images/swir_0.csv',delimiter=',')
matplotlib.image.imsave('swir.png',my_data)