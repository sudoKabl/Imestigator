from PyQt5.QtCore import QThread
import cv2
import numpy as np
import math

class autoSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, block_size = 8, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath
        self.blockSize = block_size

        
    def run_old(self):
        img = cv2.imread(self.imagePath)
        sift = cv2.SIFT_create()
        bf = cv2.BFMatcher()
        
        gray = img.copy()
    
        
        if self.grayScale:
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
            
        
        if self.hist:
            gray = cv2.equalizeHist(gray)
            
            
        if self.blur:
            gray = cv2.GaussianBlur(gray,(self.blurSize, self.blurSize), 0)
            
            
        height, width = gray.shape
        
        main_kp, main_des = sift.detectAndCompute(gray, None)
        
        matches = []
        
        for l_x in range(0, width, self.blockSize):
            u_x = l_x + 19
            
            if (u_x > width):
                break
            
            for l_y in range(0, height, self.blockSize):
                u_y = l_y + 19
                
                if (l_y > height):
                    break
                
                sub_image = gray[l_y:u_y, l_x:u_x]
                kp, des = sift.detectAndCompute(sub_image, None)
                
                if des is not None and main_des is not None:
                
                    matches = bf.knnMatch(main_des, des, k = 2)
                    
                    if matches != []:
                        
                        good = []
                        
                        for match in matches:
                            if len(match) == 2:
                                m, n = match
                                if m.distance < 0.75*n.distance:
                                    pt = main_kp[m.queryIdx].pt
                                    if not (l_x <= pt[0] <= u_x and l_y <= pt[1] <= u_y):
                                        good.append(match)
                        
                        #print(len(good))
                        
                        if len(good) > 4:
                            for match in good:
                                m, n = match
                                pt_main = main_kp[m.queryIdx].pt
                                pt_sub = kp[m.trainIdx].pt
                                
                                pt_sub = (pt_sub[0] + l_x, pt_sub[1] + l_y)
                                    
                                if pt_sub != pt_main:
                                    cv2.line(img, (int(pt_main[0]), int(pt_main[1])), (int(pt_sub[0]), int(pt_sub[1])), (0, 255, 0), 1)
                
        
        cv2.imwrite(self.dsiftPath, img)
                
        self.finished.emit()
        
        
    def run(self):
        img = cv2.imread(self.imagePath)
        
        gray = img.copy()
        
        
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        
        height, width = gray.shape
        
        w, h = (math.floor(width/2), math.floor(height/2))
        
        gray = cv2.resize(gray, (w, h), interpolation=cv2.INTER_LINEAR)
        gray = (gray / 255) * 15
        gray = (gray / 15) * 255
        
        #cv2.imwrite(self.dsiftPath, gray, [cv2.IMWRITE_JPEG_QUALITY, 50])

        #gray = cv2.imread(self.dsiftPath)
        
        #gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        relevant = []
        hashes = []
        
        result = gray.copy()
        for l_x in range(0, width, self.blockSize):
            u_x = l_x + self.blockSize
            
            if (u_x > width):
                continue
            
            for l_y in range(0, height, self.blockSize):
                u_y = l_y + self.blockSize
                
                if (l_y > height):
                    continue
                    
                testing_image = gray[l_y:u_y, l_x:u_x]
                std_dev = np.std(testing_image, axis=(0, 1))
                
                if std_dev > 8:
                    relevant.append((l_x * 4, l_y * 4))
                    hashes.append(self.getHash(testing_image))
                    
        
        
        
        step = self.blockSize * 4
        alt = (0, 0, 255)

        
        for index, hash in enumerate(hashes):
            ouly = relevant[index][1]
            oulx = relevant[index][0]
            
            olry = relevant[index][1] + step
            olrx = relevant[index][0] + step
                    
            for i in range (index + 1, len(hashes)):
                hash_test = hashes[i]
                
                hamming = self.hammingDistance(hash, hash_test)
                
                if hamming < 20:
                    uly = relevant[i][1]
                    ulx = relevant[i][0]
                    
                    lry = relevant[i][1] + step
                    lrx = relevant[i][0] + step
                    
                    halfstep = step / 2
                    
                    middle_x_o = math.floor(oulx + halfstep)
                    middle_y_o = math.floor(ouly + halfstep)
                    
                    middle_x = math.floor(ulx + halfstep)
                    middle_y = math.floor(uly + halfstep)
                    
                    
                    img = cv2.line(img, (middle_x_o, middle_y_o), (middle_x, middle_y), alt, 1)
                    
                    img = cv2.rectangle(img, (ulx, uly), (lrx, lry), alt, 1)
                    img = cv2.rectangle(img, (oulx, ouly), (olrx, olry), alt, 1)

                
        
        cv2.imwrite(self.dsiftPath, img)
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