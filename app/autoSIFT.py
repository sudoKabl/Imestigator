from PyQt5.QtCore import QThread
import cv2
import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import time

import tkinter as tk

class autoSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, block_size, min_detail, min_similar, hash_mode = 1, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath
        self.blockSize = block_size
        self.minDetail = min_detail
        self.minSimilar = min_similar
        self.hashMode = hash_mode
        
        
    def run(self):
        img = Image.open(self.imagePath)
        
        (width, height) = img.size
        w, h = (math.floor(width/4), math.floor(height/4))
        
        gray = img.convert('L')
        gray = gray.filter(ImageFilter.UnsharpMask)
        gray = gray.filter(ImageFilter.GaussianBlur)
        gray = gray.resize((w, h), resample=Image.Resampling.NEAREST)
        print(gray.getextrema())
        (width, height) = gray.size
        
        relevant = []
        middle = []
        rect_helper = []
        
        sub_rect = []
        sub_middle = []
        
        draw = ImageDraw.Draw(img)
        gray_copy = gray.copy()
        draw_gray = ImageDraw.Draw(gray_copy)
        
        #gray.save(self.dsiftPath)
        #self.finished.emit()
        #return
        

        stepsize = self.blockSize * 2

        for l_x in range(0, width, stepsize):
            u_x = l_x + stepsize

            if (u_x > width):
                continue
            
            for l_y in range(0, height, stepsize):
                u_y = l_y + stepsize
                
                if (u_y > height):
                    continue
                
                area = (l_x, l_y, u_x, u_y)
                
                testing_image = gray.crop(area)
                
                stat = ImageStat.Stat(testing_image)
                std_dev = stat.stddev
            

                if std_dev[0] >= self.minDetail:
                    relevant.append(testing_image)
                    x = math.floor(l_x + (stepsize / 2))
                    y = math.floor(l_y + (stepsize / 2))
                    
                    draw_gray.rectangle(area)
                    draw_gray.text((l_x + 1, l_y), str(math.floor(std_dev[0])))
                                   
                    sub_middle.append((x, y))
                    
                    rect_helper.append([(l_x * 4, l_y * 4), (u_x * 4, u_y * 4)])
                    sub_rect.append(area)

        gray_copy.save(self.dsiftPath)
        self.finished.emit()
        return
    
    # Idee: Nur felder vergleichen die in der nähe der anderen Standardabweichung sind?

        rect = []
        working_images = []
        
        for index, image in enumerate(relevant):

            l_x = 0
            l_y = 0
            u_x, u_y = image.size
            m_x = math.floor(u_x/2)
            m_y = math.floor(u_y/2)
            
            sub_areas = [
                (l_x, l_y, m_x, m_y), 
                (m_x, l_y, u_x, m_y), 
                (l_x, m_y, m_x, u_y), 
                (m_x, m_y, u_x, u_y)
                ]
            
            real_l, real_u = rect_helper[index]
            real = (real_l[0], real_l[1], real_l[0], real_l[1])

            for a in sub_areas:
                gray_koords = tuple(map(lambda i, j: i + (j/4), a, real))
                working_images.append(gray.crop(gray_koords))
                
                
                rect.append(tuple(map(lambda i, j: (i * 4) + j, a, real)))
                middle_x = gray_koords[0] + (u_x / 4)
                middle_y = gray_koords[1] + (u_y / 4) 
                middle.append((middle_x * 4, middle_y * 4))
            
        
        hashmap = []
        
        if self.hashMode == 0:
            for image in working_images:
                hashmap.append(imagehash.colorhash(image))
        
        if self.hashMode == 1:
            for image in working_images:
                hashmap.append(imagehash.average_hash(image))
        elif self.hashMode == 2:
            for image in working_images:
                hashmap.append(imagehash.phash(image))
        elif self.hashMode == 3:
            for image in working_images:
                hashmap.append(imagehash.dhash(image))
        elif self.hashMode == 4:
            for image in working_images:
                hashmap.append(imagehash.whash(image))
        elif self.hashMode == 5:
            for image in working_images:
                hashmap.append(imagehash.crop_resistant_hash(image))
                
        imagehash.colorhash
                
        
        for index, image in enumerate(working_images):
            hash = hashmap[index]
            
            for i in range(index + 1, len(working_images)):
                hash_comp = hashmap[i]
                
                #temp_img = img.copy()
                #draw_temp = ImageDraw.Draw(temp_img)
                
                #draw_temp.rectangle(rect[index], outline="green", width=1)
                #draw_temp.rectangle(rect[i], outline="blue", width=1)
                #draw_temp.line([middle[index], middle[i]], fill=(0, 255, 255), width=2)

                if hash - hash_comp < self.minSimilar:
                    #draw.line([middle[index], middle[i]], fill=(255, 0, 0), width=2)
                    draw.rectangle(rect[index], outline="red", width=1)
                    draw.rectangle(rect[i], outline="red", width=1)
                    
                    
        print("done with " + str(self.minSimilar))
                    
        img.save(self.dsiftPath)
        self.finished.emit()
        return
                    
            
            
    def getHash(self, img):
        height, width = img.shape
        pt_array = np.empty([height * width])
        i = 0
        
        for x in range(height):
            for y in range(width):
                pt = img[x, y]
                pt_array[i] = pt
                i += 1
                #print(pt)
                #print(type(pt))
        
        bytes = pt_array.tobytes()

        return bytes.hex()
    
    def hammingDistance(self, a, b):
        if len(a) == len(b):
            count = 0
            i = 0
            
            while i < len(a):
                if a[i] != b[i]:
                    count += 1
                i += 1
            
            return count
        else:
            return 500
        