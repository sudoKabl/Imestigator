import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit
import time

def run():

    img = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_einfach.png")

    frameSize = 60
    
    img_copy = img.copy()

    draw = ImageDraw.Draw(img_copy)
    img = img.convert('L')


    def getArea(x, y, size):
        return (x, y, x + size, y + size)

    #draw.rectangle(getArea(1181, 575), outline="red", width=1)
    test_img = img.crop(getArea(1181, 575, frameSize))

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
            
            for xvar in range(width):
                for yvar in range(height):
                    a = img_a.getpixel((xvar, yvar))
                    b = img_b.getpixel((xvar, yvar))
                    
                    distance += getDistance(a, b)

            return distance
        (w, h) = img_a.size
        return w * h * 765


    def manualStddev(img):
        (width, height) = img.size
        stats = ImageStat.Stat(img)
        
        means = stats.mean
        
        r = []
        g = []
        b = []
        
        rgb = [r, g, b]
        
        for index, mean in enumerate(means):
            for x in range(width):
                for y in range(height):
                    pixel = img.getpixel((x, y))
                    rgb[index].append((pixel[index] - means[index])**2)
        
        
        rgb_sq = [0, 0, 0]
        
        for index, clist in enumerate(rgb):
            for el in clist:
                rgb_sq[index] += el
        
        for index, i in enumerate(rgb_sq):
            rgb_sq[index] = i / len(rgb[index])
            rgb_sq[index] = math.sqrt(rgb_sq[index])
            
        return rgb_sq
        
    
    (width, height) = img.size
    
    stepsize = frameSize * 2
    
    
    frames_x = math.ceil(width / stepsize) - 1
    frames_y = math.ceil(height / stepsize) - 1
    testlist = []
    
    for i in range(frames_x):
        testlist.append([])
    
    for list in testlist:
        for i in range(frames_y):
            list.append(None)
    
    for x in range(0, width, stepsize):
        for y in range(0, height, stepsize):
            if x + stepsize > width or y + stepsize > height:
                continue

            compare_img = img.crop(getArea(x, y, stepsize))
            stat = ImageStat.Stat(compare_img)
            stddev = stat.stddev
            
            if stddev[0] > 5:
                testlist[math.floor(x / stepsize)][math.floor(y / stepsize)] = 1
                draw.rectangle(getArea(x, y, stepsize))
            else:
                testlist[math.floor(x / stepsize)][math.floor(y / stepsize)] = None
    
    list_of_lowest = []
    frames_x -= 1
    frames_y -= 1
    
    x = 0
    y = 0
    
    
    
    while x in range(width):
        column_checker = frames_y + 1
        y = 0
        while y in range(height):
            if x == 0:
                x_position = 0
            else:
                if x % stepsize == 0:
                    x_position = math.ceil(x / stepsize)
                else:
                    x_position = math.ceil(x / stepsize) - 1
                
            if y == 0:
                y_position = 0
            else:
                if y % stepsize == 0:
                    y_position = math.ceil(y / stepsize)
                else:
                    y_position = math.ceil(y / stepsize) - 1
                    
            if x_position > frames_x or y_position > frames_y:
                y = 0
                break
                
            if y + frameSize > (y_position + 1) * stepsize:
                if y_position + 1 < frames_y:
                    if testlist[x_position][y_position + 1] == None:
                        y += stepsize
                        column_checker -= 1
                        #print("Skipped because oob")
                        continue
                else:
                    break
                
            if testlist[x_position][y_position] == None:
                y += stepsize
                column_checker -= 1
            else:
                compare_img = img.crop(getArea(x, y, frameSize))
                
                distance = pixelCompare(test_img, compare_img)
                
                if distance < 10000:
                    draw.rectangle(getArea(x, y, frameSize), outline="blue", width=1)
                    
                
                if len(list_of_lowest) < 10:
                    list_of_lowest.append(distance)
                else:
                    list_of_lowest.sort()
                    if list_of_lowest[9] > distance:
                        list_of_lowest[9] = distance
                y += 1


        if column_checker == 0:
            x += stepsize
        else:
            x += 1
            
    list_of_lowest.sort()
    print(list_of_lowest)
        
    
    img_copy.show()
    img_copy.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_result_2.png")    
    
    
exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")
