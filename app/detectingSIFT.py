from PyQt5.QtCore import QThread
import cv2 as cv
import numpy as np

class detectingSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, blur = 3, blur_size = 5, adaThre = 21, min_similar = 0.5, min_matches = 8, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath

        self.blur = blur
        self.blurSize = blur_size
        self.adaThre = int(adaThre * 2 + 1)
        self.minSimilar = min_similar / 10
        self.minMatch = min_matches

        
    def run(self):
        img_org = cv.imread(self.imagePath)
        sift = cv.SIFT_create()
        bf = cv.BFMatcher(cv.NORM_L2, crossCheck=False)
        kernel = np.ones((3,3),np.uint8)       
        height, width = img_org.shape[:2]
 
        
        gray = cv.cvtColor(img_org, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)
        
        for i in range(self.blur):
            gray = cv.GaussianBlur(gray, (self.blurSize, self.blurSize), 0)
        
        
        thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, self.adaThre, 2)
        dilated_1 = cv.dilate(thresh, kernel, iterations=1)
    
        edges = cv.Canny(dilated_1, 50, 150)
        dilated_2 = cv.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv.findContours(dilated_2, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
 
        
        limits = [width, height, width, height]
        expanding = [-20, -20, 20, 20]
        
        elements = []
        
        kp_org, des_org = sift.detectAndCompute(img_org, None)
        
        for cnt in contours:
            x, y, w, h = cv.boundingRect(cnt)
            if w < 20 or h < 20 or w > width/2 or h > height/2:
                continue
            
            area = [x, y, x+w, y+h]
            
            
            
            for i in range(4):
                if not (0 > area[i] + expanding[i] or area[i] + expanding[i] > limits[i]):
                    area[i] += expanding[i]
                    
            crop = img_org[area[1]:area[3], area[0]:area[2]]
            
            crop_width, crop_height = crop.shape[:2]
            
            if crop_width > 1 and crop_height > 1:
                scale = 1
                if crop_width >= crop_height:
                    if crop_width > 512:
                        scale = crop_width // 512
                    elif crop_width < 512:
                        scale = 512 // crop_width
                else:
                    if crop_height > 512:
                        scale = crop_height // 512
                    elif crop_height < 512:
                        scale = 512 // crop_height
                        
                crop_width *= scale
                crop_height *= scale
                
                resize = cv.resize(crop, (crop_height, crop_width), interpolation=cv.INTER_LANCZOS4)
                
                elements.append((area, resize, scale))
                
        print("Starting to comprea advanced")
        print(len(elements))
        for (area, resize, scale) in elements:
            kp_resize, des_resize = sift.detectAndCompute(resize, None)
            if des_resize is not None and len(des_resize) > 0:
                matches = bf.knnMatch(des_org, des_resize, k=2)
                
                if len(matches) > 0:
                    good = []
                    for match in matches:
                        if len(match) < 2:
                            continue
                        m, n = match
                        if m.distance < self.minSimilar*n.distance:
                            good.append(m)
                            
                    if len(good) >= self.minMatch:
                        for m in good:
                            query_idx = m.queryIdx
                            train_idx = m.trainIdx
                            
                            (x1, y1) = kp_org[query_idx].pt
                            (x2, y2) = kp_resize[train_idx].pt
                            
                            x2 /= scale
                            y2 /= scale
                            x2 += area[0]
                            y2 += area[1]
                            
                            if area[0] <= x1 <= area[2] and area[1] <= y1 <= area[3]:
                                continue
                            
                            cv.circle(img_org, (int(x1), int(y1)), 10, (0, 255, 0), -1) 
                            cv.circle(img_org, (int(x2), int(y2)), 10, (0, 255, 0), -1)
                            cv.line(img_org, tuple(map(int, (x1, y1))), tuple(map(int, (x2, y2))), (0, 255, 0), 2)
        
         
        cv.imwrite(self.dsiftPath, img_org)
        self.finished.emit()
        return