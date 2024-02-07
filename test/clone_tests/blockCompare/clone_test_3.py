import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit
import time

def run():#hashfunc, threshold):

    img = Image.open("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet.png")

    frameSize = 60
    
    img_copy = img.copy()

    draw = ImageDraw.Draw(img_copy)
    img = img.convert('L')


    def getArea(x, y, size):
        return (x, y, x + size, y + size)

    draw.rectangle(getArea(1181, 575, frameSize), outline="red", width=1)
    test_img = img.crop(getArea(1181, 575, frameSize))
    #test_hash = hashfunc(test_img)
    test_hash = imagehash.phash(test_img, 8)
    
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
    
    #list_of_lowest = []
    frames_x -= 1
    frames_y -= 1

    x = 0
    y = 0


    
    while x in range(width):
        column_checker = frames_y + 1
        asdf = 0
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
                        continue
                else:
                    break
                        
                
            if testlist[x_position][y_position] == None:
                y += stepsize
                column_checker -= 1
            else:
                compare_img = img.crop(getArea(x, y, frameSize))
                
                compare_hash = imagehash.phash(compare_img, 8)
                
                #if len(list_of_lowest) < 10:
                #    list_of_lowest.append(test_hash - compare_hash)
                #else:
                #    list_of_lowest.sort()
                #    if list_of_lowest[9] > test_hash - compare_hash:
                #        list_of_lowest[9] = test_hash - compare_hash
                
                if test_hash - compare_hash <= 5:
                    draw.rectangle(getArea(x, y, frameSize), outline="blue")

                y += 1

        if column_checker == 0:
            x += stepsize
        else:
            x += 1
            
    #list_of_lowest.sort()
    
    #print(str(hashfunc))
    #for number in list_of_lowest:
    #    print(number)
        
    
    img_copy.show()
    img_copy.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_result_3" + str(hashfunc).split(" ")[1] +".png")    
    
    
#hashes = [imagehash.average_hash, imagehash.phash, imagehash.dhash, imagehash.whash]

#threshes = [0, 5, 10, 5]

#for i in range(4):
    #exec_time = timeit.timeit(lambda: run(hashes[i], threshes[i]), number=5)
    #print(f"Ausführungszeit von {hashes[i]}: {exec_time} Sekunden")

exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")