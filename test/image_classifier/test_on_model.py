import tensorflow as tf
from tensorflow import keras
from keras.models import Model, load_model

import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
import time



#path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"
#path_org = os.path.join(os.getcwd(), "klon_bearbeitet_2.png")
#path_org = os.path.join(os.getcwd(), "ufo.cache-1.jpg")
#path_org = os.path.join(os.getcwd(), "klon_original.jpg")
image_fldr = os.path.join(os.getcwd(), "test")
path_org = os.path.join(image_fldr, "20210604_202708.jpg")



model = load_model(os.path.join(os.getcwd(), "model_2_windows.keras"))

def load_and_prepare_image(image_path, img_size=(256, 256)):
    # Load the image
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
    # Resize the image
    img = tf.image.resize(img, img_size)
    # Normalize the image to [0, 1] if your model expects this range
    img = img / 255.0
    return img

imgO = cv2.imread(path_org)

#createEla(path_org)
#createNoise(path_org)

imgE = path_org + "_ela.jpg"
imgN = path_org + "_noise.jpg"

original_img = load_and_prepare_image(path_org)
filtered1_img = load_and_prepare_image(imgE)
filtered2_img = load_and_prepare_image(imgN)

original_img_batch = tf.expand_dims(original_img, axis=0)  # Shape becomes [1, height, width, channels]
filtered1_img_batch = tf.expand_dims(filtered1_img, axis=0)
filtered2_img_batch = tf.expand_dims(filtered2_img, axis=0)

inputs = [original_img_batch, filtered1_img_batch, filtered2_img_batch]

prediction = model.predict(inputs)

if prediction > 0.5:
    print(f"Predicted class is fake with {prediction}")
else:
    print(f"Predicted class is real with {prediction}")