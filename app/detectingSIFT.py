from PyQt5.QtCore import QThread
import cv2
import math
import numpy as np

class detectingSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath

        
    def run(self):
        img = cv2.imread(self.imagePath)
        sift = cv2.SIFT_create()
        bf = cv2.BFMatcher()
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray,(5,5),0)
        
        height, width = gray.shape
        w, h = (math.floor(width/4), math.floor(height/4))
        
        lower_resultion = cv2.resize(gray, (w, h), interpolation=cv2.INTER_LINEAR)
        
        thresholded = cv2.adaptiveThreshold(lower_resultion, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)
        
        kernel = np.ones((3,3),np.uint8)
        no_noise = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
        no_noise = cv2.morphologyEx(no_noise, cv2.MORPH_CLOSE, kernel)
        
        cv2.imwrite(self.dsiftPath, no_noise)
                
        self.finished.emit()