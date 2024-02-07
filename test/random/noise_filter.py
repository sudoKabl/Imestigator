from PIL import Image, ImageChops, ImageFilter, ImageOps
import re
import cv2
import numpy as np

def getDistance(a, b):
    if a == b:
        return 0
    if a > b:
        return a - b
    else:
        return b - a

def pixelCompare(img_a, img_b):
    if img_a.size == img_b.size:
        distance = 0
        (width, height) = img_a.size
        
        for x in range(width):
            for y in range(height):
                a = img_a.getpixel((x, y))
                b = img_b.getpixel((x, y))
                
                distance += getDistance(a[0], b[0])
                distance += getDistance(a[1], b[1])
                distance += getDistance(a[2], b[2])

        return distance
    (w, h) = img_a.size
    return w * h * 765
    

target = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\rauschen_full.png")
target = target.convert('RGB')

img = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\manuelles_rauschen.png")
img = img.convert('RGB')

#img = ImageOps.invert(img)
#img = img.convert('L')
#img = img.filter(ImageFilter.GaussianBlur())
#img = img.filter(ImageFilter.FIND_EDGES())
#img.show()


target = ImageOps.invert(target)
target.show()

sizes = [1, 3, 5]
results = []

for size in sizes:

    filters = [ImageFilter.GaussianBlur(), ImageFilter.UnsharpMask(), ImageFilter.SHARPEN(), ImageFilter.MedianFilter(), ImageFilter.DETAIL()]
    
    for filter in filters:
        filtered = img.filter(filter)
        
        #filtered.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\noise\\" + re.search(r'\.(\w+) object at', str(filter)).group(1) + "_" + str(size) + ".png")
        
        only_noise = ImageChops.subtract(img, filtered)
        only_noise.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\noise\\" + re.search(r'\.(\w+) object at', str(filter)).group(1) + "_" + str(size) + ".png")
        
        distance = pixelCompare(target, only_noise)
        
        print(re.search(r'\.(\w+) object at', str(filter)).group(1) + " with size " + str(size) + " resulted: " + str(distance))
        
        results.append([distance, re.search(r'\.(\w+) object at', str(filter)).group(1) + " with size " + str(size) + " resulted: " + str(distance)])


sorted_results = sorted(results, key = lambda x: x[0])

for index, msg in enumerate(sorted_results):
    print(str(index + 1) + ": " + msg[1])