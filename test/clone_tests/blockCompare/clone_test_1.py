import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit

def run():

    img = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet.png")

    frameSize = 60
    
    img_copy = img.copy()

    draw = ImageDraw.Draw(img_copy)


    def getArea(x, y):
        return (x, y, x + frameSize, y + frameSize)

    draw.rectangle(getArea(1181, 575), outline="red", width=1)
    test_img = img.crop(getArea(1181, 575))

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

    (width, height) = img.size
    
    list_of_lowest = []
    
    draw.rectangle((1000, 550, 1400, 800), outline="white", width=1)

    for x in range(1000, 1400, 1):
        for y in range(550, 800, 1):
            #print("(" + str(x) + ", " + str(y) + ")")
            if x == 1181 and y == 575:
                continue
            
            compare_img = img.crop(getArea(x, y))
            
            distance = pixelCompare(test_img, compare_img)
            
            if len(list_of_lowest) < 10:
                list_of_lowest.append(distance)
            else:
                list_of_lowest.sort()
                if list_of_lowest[9] > distance:
                     list_of_lowest[9] = distance
            
            if distance < 27850:
                draw.rectangle(getArea(x, y), outline="blue", width=1)
    
    list_of_lowest.sort()
    
    for number in list_of_lowest:
        print(number)
        
    
    img_copy.show()
    img_copy.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_result_1.png")
    
exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")
