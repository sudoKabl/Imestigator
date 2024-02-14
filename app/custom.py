from PyQt5.QtCore import QThread
import cv2 as cv
import numpy as np

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
        
        for filter in self.filterArray:
            try:
                if filter == "Grayscale":
                    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                    
                elif filter == "Gaussian Blur":
                    img = cv.GaussianBlur(img, (3, 3), 1)
                    
                elif filter == "Median Filter":
                    img = cv.medianBlur(img, 3)
                    
                elif filter == "Adaptive Threshold":
                    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
                    
                elif filter == "Canny Edge":
                    img = cv.Canny(img, 100, 200)
                    
                elif filter == "Erosion":
                    img = cv.erode(img, kernel, iterations=1)
                    
                elif filter == "Dilation":
                    img = cv.dilate(img, kernel, iterations=1)
            except Exception:
                pass
        
        cv.imwrite(self.generalPath, img)
        self.finished.emit()
        
        