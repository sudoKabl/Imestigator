from PyQt5.QtCore import QThread
import cv2
import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw
import imagehash

class autoSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, block_size = 8, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath
        self.blockSize = block_size
        
        
    def run(self):
        img = Image.open(self.imagePath)
        
        (width, height) = img.size
        w, h = (math.floor(width/4), math.floor(height/4))
        
        gray = img.convert('L')
        gray = gray.resize((w, h), resample=Image.Resampling.BILINEAR)
        (width, height) = gray.size
        
        print(width, height)
        
        relevant = []
        middle = []
        rect = []
        draw = ImageDraw.Draw(img)
        
        #gray.save(self.dsiftPath)
        #self.finished.emit()
        #return

        for l_x in range(0, width, self.blockSize):
            u_x = l_x + self.blockSize
            
            if (u_x > width):
                continue
            
            for l_y in range(0, height, self.blockSize):
                u_y = l_y + self.blockSize
                
                if (l_y > height):
                    continue
                
                area = (l_x, l_y, u_x, u_y)
                
                testing_image = gray.crop(area)
                testing_image.convert('L')
                
                stat = ImageStat.Stat(testing_image)
                std_dev = stat.stddev
                
                if std_dev[0] > 20:
                    relevant.append(testing_image)
                    x = math.floor(l_x + (self.blockSize / 2))
                    y = math.floor(l_y + (self.blockSize / 2))
                                   
                    middle.append((x * 4, y * 4))
                    rect.append([(l_x * 4, l_y * 4), (u_x * 4, u_y * 4)])
                    
        
        
        for index, image in enumerate(relevant):
            hash = imagehash.phash(image)
            
            for i in range(index + 1, len(relevant)):
                hash_comp = imagehash.phash(relevant[i])
                
                #print(hash - hash_comp)
                
                if hash - hash_comp < 15:
                    draw.line([middle[index], middle[i]], fill=(255, 0, 0), width=2)
                    draw.rectangle(rect[index], outline="red", width=1)
                    draw.rectangle(rect[i], outline="red", width=1)
                    
                    
                    
        img.save(self.dsiftPath)
        self.finished.emit()
                    
            
            
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