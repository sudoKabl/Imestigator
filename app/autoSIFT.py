from PyQt5.QtCore import QThread
import cv2

class autoSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath

        
    def run(self):
        img = cv2.imread(self.imagePath)
        #sift = cv2.SIFT_create()
        #bf = cv2.BFMatcher()
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray,(5,5),0)
        
        result = gray
        
        cv2.imwrite(self.dsiftPath, gray)
                
        self.finished.emit()