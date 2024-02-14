from PyQt5.QtCore import QThread
import cv2
import math
import numpy as np

class detectingSIFTWorker(QThread):
    def __init__(self, imagePath, dsiftPath, hist = False, blur = True, blur_size = 5, adaThre = True, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.dsiftPath = dsiftPath
        self.hist = hist
        self.blur = blur
        self.blurSize = blur_size
        self.adaThre = adaThre

        
    def run(self):
        img = cv2.imread(self.imagePath)
        sift = cv2.SIFT_create()
        bf = cv2.BFMatcher()
        
        gray = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
        
        if self.hist:
            gray = cv2.equalizeHist(gray)
            
            
        if self.blur:
            gray = cv2.GaussianBlur(gray,(self.blurSize, self.blurSize), 0)
        
        height, width = gray.shape
        w, h = (math.floor(width/4), math.floor(height/4))
        
        lower_resultion = cv2.resize(gray, (w, h), interpolation=cv2.INTER_LINEAR)
        
        
        if self.adaThre:
            gray = cv2.adaptiveThreshold(lower_resultion, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        
        #thresholded = cv2.Canny(gray, 50, 200)
        
        kernel = np.ones((3,3),np.uint8)
        no_noise = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        no_noise = cv2.morphologyEx(no_noise, cv2.MORPH_CLOSE, kernel)
        
        no_noise = cv2.resize(no_noise, (width, height), interpolation=cv2.INTER_NEAREST)
        
        #cv2.imwrite(self.dsiftPath, no_noise)
        
        # Get keypoints of original image
        keypoints, descriptors = sift.detectAndCompute(img, None)
        
        # Get contours of objects in filtered image
        contours, _ = cv2.findContours(no_noise, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Convert contours to convex hulls to get rid of some noise and indents
        hulls = []
        
        for cont in contours:
            hull = cv2.convexHull(cont)
            hulls.append(hull)
            
        # Filter contours so very big or smalls ones dont get considered
        filtered_contours = [cnt for cnt in contours if 10 < cv2.contourArea(cnt) < 20000]
        
        des_of_object = [[] for _ in range(len(filtered_contours))]
        kp_of_object = [[] for _ in range(len(filtered_contours))]
        indexes = [[] for _ in range(len(filtered_contours))]
        
        point_in_struct = []
        i = 0
        
        
        # Collect all the keypoints and descriptors that are actually inside of hulls (with some tolerance)
        for index_kp, point in enumerate(keypoints):
            (x, y) = point.pt
            
            for index_c, contour in enumerate(filtered_contours):
                if i == 0:
                    i = 1
                    continue
                
                dist = cv2.pointPolygonTest(contour, (x, y), True)
                # TODO: Changeable tolerance
                if dist >= -10:
                    point_in_struct.append(point)
                    
                    des_of_object[index_c].append(descriptors[index_kp])
                    kp_of_object[index_c].append(keypoints[index_kp])
                    indexes[index_c].append(index_kp)
                    
                    break
        
        img = cv2.drawKeypoints(img, point_in_struct, img, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        # Draw contours
        for contour in filtered_contours:
            if i == 0:
                i = 1
                continue
            cv2.drawContours(img, [contour], 0, (0, 0, 255), 1) 
    
        tester = 0
        for index, obj_des in enumerate(des_of_object):
            np_des = np.array(obj_des)
            
            if len(obj_des) == 0:
                continue
            #TODO:
            # des hier anpassen, sodass np_des nicht enthalten ist
            # alternativ: np des in den matches ausschließen?
            
            temp_des = descriptors.copy()
            
            for to_delete in reversed(indexes[index]):
                temp_des = np.delete(temp_des, to_delete, 0)
            
            matches = bf.knnMatch(np_des, temp_des, k=2)
            kps = kp_of_object[index]
            
            if matches != []:
                good = []
                
                for m,n in matches:
                    if m.distance < 0.75*n.distance:
                        good.append([m])
                # TODO: MInimale matches anpassbar
                if len(good) > 4:
                    for match_obj in good:
                        tester += 1
                        for dingsi in match_obj:
                            pt1 = tuple(map(int, kps[dingsi.queryIdx].pt))
                            pt2 = tuple(map(int, keypoints[dingsi.trainIdx].pt))
                            cv2.line(img, pt1, pt2, (0, 255, 0), 2)
                
        cv2.imwrite(self.dsiftPath, img)
                
        self.finished.emit()