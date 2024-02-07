import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit
import time

#path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"
path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet.png"
path_tmp = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_quant.png"

def quant_img():
    img = cv2.imread(path_org)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    h, w = gray.shape
    scale = 0
    while w > 1024 or h > 1024:
        w, h = (math.floor(w/2), math.floor(h/2))
        scale += 1
        
    blur = cv2.GaussianBlur(gray,(5,5),0)
    
    lower_resultion = cv2.resize(blur, (w, h), interpolation=cv2.INTER_LINEAR)
    
    gauss_thresh = cv2.adaptiveThreshold(lower_resultion, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    kernel = np.ones((5,5),np.uint8)
    open = cv2.morphologyEx(gauss_thresh, cv2.MORPH_OPEN, kernel)
    close = cv2.morphologyEx(open, cv2.MORPH_CLOSE, kernel)
    
    cv2.imwrite(path_tmp, close)
    
    return scale

def run():
    img_org = Image.open(path_org)
    img_copy = img_org.copy()
    draw = ImageDraw.Draw(img_copy)

    img_gray = img_org.convert('L')
    
    frameSize = 4
    
    (width, height) = img_org.size
    (w, h) = (width, height)
    
    factor = 1
    
    while w > 1024 or h > 1024:
        w = math.floor(w / 2)
        h = math.floor(h / 2)
        factor *= 2
        
    print(w, h)
    
    frameSize *= factor
        
    img_resize = img_gray.resize((w, h), resample=Image.Resampling.NEAREST)
    
    
    
    def getArea(x, y, size):
        return (x, y, x + size, y + size)

    frames = []
        
    
    for x in range(0, w, frameSize):
        #frames.append([])
        for y in range(0, h, frameSize):
            if x + frameSize >= w or y + frameSize >= h:
                draw.rectangle(getArea(x * factor, y * factor, frameSize * factor), fill="black")
            else:    
                compare_img = img_resize.crop(getArea(x, y, frameSize))
                
                stat = ImageStat.Stat(compare_img)
                
                if stat.stddev[0] > 5:
                    #frames[math.floor(x / frameSize)].append((0, getArea(x * factor, y * factor, frameSize * factor)))
                #else:
                    frames.append(getArea(x * factor, y * factor, frameSize * factor))
                    #draw.rectangle(getArea(x * factor, y * factor, frameSize * factor), outline="blue")

    table = []
    
    half = math.floor(frameSize * factor / 2)
    
    for frame in frames:
        x1, y1, x2, y2 = frame
        dhashes = []
        
        for x in range(x1, x2):
            for y in range(y1, y2):
                compare_img = img_resize.crop(getArea(x, y, frameSize))
                dhashes.append(imagehash.dhash(compare_img))
         
        if x1 != 0 and x1 - half >= 0:
            x1 -= half
             
        if y1 != 0 and y1 - half >= 0:
            y1 -= half

        if x2 + half < width:
            x2 += half
            
        if y2 + half < height:
            y2 += half
            
        expanded = img_org.crop((x1, y1, x2, y2))
        #draw.rectangle((x1, y1, x2, y2), outline="red")
        
        phash = imagehash.phash(expanded)
        
        table.append([x1, y1, phash, dhashes])
        
        
    for index, el in enumerate(table):
        pHash1 = el[2]
        dHashes1 = el[3]
        
        for i in range(index + 1, len(table)):
            if pHash1 - table[i][2] < 25:
                dHashes2 = table[i][3]
                
                for index, dHash1 in enumerate(dHashes1):
                    for index2 in range(index, len(dHashes2)):
                        if dHash1 - dHashes2[index2] < 10:
                            shape = [(el[0] + frameSize * factor, el[1] + frameSize * factor), (table[i][0] + frameSize * factor, table[i][1] + frameSize * factor)]
                            draw.line(shape)
                            draw.rectangle(getArea(el[0], el[1], frameSize * factor))
                            draw.rectangle(getArea(table[i][0], table[i][1], frameSize * factor))
                        
        
    img_copy.show()
    img_copy.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_result_4.png")    
    


    
    
    
    

exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")
