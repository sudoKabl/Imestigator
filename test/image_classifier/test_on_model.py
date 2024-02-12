import tensorflow as tf
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import time

#path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"
path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_2.png"

model = tf.keras.models.load_model("D:\\Hochschule\\Bachelorarbeit\\training_img\\model_1.h5")

img = cv2.imread(path_org)

resize = tf.image.resize(img, (256,256))

print(model.predict(np.expand_dims(resize, 0)))