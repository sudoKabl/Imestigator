from PyQt5.QtCore import QThread
import cv2 as cv
import numpy as np
import math
import os

class CustomWorker(QThread):
    def __init__(self, imagePath, generalPath, filters, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.generalPath = generalPath
        self.filterArray = filters
        
    def run(self):
        img = cv.imread(self.imagePath)

        if len(self.filterArray) == 0:
            cv.imwrite(self.generalPath, img)
            self.finished.emit()
            return
        
        kernel = np.ones((5,5),np.uint8)
        
        for filter, opt in self.filterArray:
            try:
                if filter == "Grayscale":
                    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                    
                elif filter == "Gaussian Blur":
                    img = cv.GaussianBlur(img, (opt[0], opt[0]), 1)
                    
                elif filter == "Median Filter":
                    img = cv.medianBlur(img, opt[0])
                    
                elif filter == "Adaptive Threshold":
                    img = cv.adaptiveThreshold(img, opt[1], cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, opt[0], 2)
                    
                elif filter == "Canny Edge":
                    img = cv.Canny(img, opt[1], opt[0])
                    
                elif filter == "Erosion":
                    img = cv.erode(img, kernel, iterations=1)
                    
                elif filter == "Dilation":
                    img = cv.dilate(img, kernel, iterations=1)
                    
                elif filter == "Equalize Histogram":
                    img = cv.equalizeHist(img)
                    
                elif filter == "Threshold":
                    img = cv.threshold(img,127,255,cv.THRESH_BINARY)
                    
                elif filter == "Top Hat":
                    img = cv.morphologyEx(img, cv.MORPH_TOPHAT, kernel)
                    
                elif filter == "Black Hat":
                    img = cv.morphologyEx(img, cv.MORPH_BLACKHAT, kernel)
                    
                elif filter == "Sobel X": 
                    img = cv.Sobel(img, cv.CV_64F, 1, 0)
                    
                elif filter == "Sobel Y": 
                    img = cv.Sobel(img, cv.CV_64F, 0, 1)
                    
                elif filter == "Laplacian Edge":
                    img = cv.Laplacian(img, cv.CV_64F)
                    
                elif filter == "ELA":
                    img_tmp_path = self.generalPath + ".tmp_ela.jpg"
                    cv.imwrite(img_tmp_path, img, [cv.IMWRITE_JPEG_QUALITY, opt[0]])
                    elad = cv.imread(img_tmp_path)

                    elad_corrected = elad.astype(img.dtype)
                                       
                    img = cv.subtract(img, elad_corrected)
                    
                elif filter == "Noise Analysis":
                    filtered = cv.GaussianBlur(img, (opt[0], opt[0]), 1)
                    img = cv.subtract(img, filtered)
                    
                elif filter == "Brightness and Contrast":
                    img = cv.convertScaleAbs(img, alpha=opt[0], beta=opt[1])
                    
            except Exception as e: print(e)
        
        cv.imwrite(self.generalPath, img)
        self.finished.emit()
        
        
        
