import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit
import time

def run():

    img = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet.png")
    frameSize = 60
    draw = ImageDraw.Draw(img)

    def getArea(x, y, size):
        return (x, y, x + size, y + size)


    test_img = img.crop(getArea(1181, 575, frameSize))
    test_hash = imagehash.average_hash(test_img)
    
    (width, height) = img.size
    
    larrylist = []
    
    for x in range(0, width, frameSize):
        for y in range(0, height, frameSize):
            compare_img = img.crop(getArea(x, y, frameSize))
            
            shesh = imagehash.average_hash(compare_img)
            #if test_hash - egal < 5:
            
            draw.rectangle(getArea(x, y, frameSize), outline="blue")
            #draw.text((x, y), str(shesh))
            print(str(shesh))
            
            stat = ImageStat.Stat(compare_img)
            stddev = stat.stddev
            
            if stddev[0] > 5:
                larrylist.append((x,y))
            
    img.show()

    
    
exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")
