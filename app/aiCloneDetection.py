from PyQt5.QtCore import QThread
from ultralytics import FastSAM
import cv2
from ultralytics.models.fastsam import FastSAMPrompt
import math


class aiCloneWorker(QThread):
    def __init__(self, imagePath, clonePath, minMatches=5, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.clonePath = clonePath
        self.minMatches = minMatches
    
    
    def run(self):
        img = cv2.imread(self.imagePath)
        img = cv2.resize(img, (1024, 1024))
        
        model = FastSAM('FastSAM-s.pt')
        result = model(self.imagePath, device=0, retina_masks=True, imgsz=1024, conf=0.2, iou=0.7)
        prompt_process = FastSAMPrompt(self.imagePath, result, device=0)
        
        height, width = img.shape[:2]
        limits = [width, height, width, height]
        
        elements = []
        
        for box in prompt_process.results[0].boxes.xyxy:
            area = (
                math.floor(box.cpu().numpy()[0]), 
                math.floor(box.cpu().numpy()[1]), 
                math.floor(box.cpu().numpy()[2]), 
                math.floor(box.cpu().numpy()[3])
                )
            expanding = [-10, -10, 10, 10]
            
            for i in range(4):
                if 0 > area[i] + expanding[i] or area[i] + expanding[i] > limits[i]:
                    expanding[i] = 0
            
            crop = img[area[1]+expanding[0]:area[3]+expanding[1], 
                     area[0]+expanding[2]:area[2]+expanding[3]]
            w, h = crop.shape[:2]
            
            if w > 1 and h > 1:
            
                scale = 1
                if w >= h:
                    if w > 512:
                        scale = w / 512
                    elif w < 512:
                        scale = 512 / w
                else:
                    if h > 512:
                        scale = h / 512
                    elif h < 512:
                        scale = 512 / h
                
                w *= scale
                h *= scale
                
                
                resize = cv2.resize(crop, (math.floor(h), math.floor(w)), interpolation=cv2.INTER_LANCZOS4)
                
                elements.append((area, resize, scale, expanding))
        
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        sift = cv2.SIFT_create()
        
        kp1, des1 = sift.detectAndCompute(img, None)
        
        draw = img.copy()
        
        for (area, resize, scale, expanding) in elements:
            kp2, des2 = sift.detectAndCompute(resize, None)
            if des2 is not None and len(des2) > 0:
                matches = bf.knnMatch(des1, des2, k=2)
                
                if len(matches) > 0:
                    good = []
                    for match in matches:
                        if len(match) < 2:
                            continue
                        m, n = match
                        if m.distance < 0.4*n.distance:
                            good.append([m])
                    
                    if len(good) >= self.minMatches:
                        for match in good:
                            m = match[0]
                            query_idx = m.queryIdx
                            train_idx = m.trainIdx
                            
                            (x1, y1) = kp1[query_idx].pt
                            (x2, y2) = kp2[train_idx].pt
                            
                            x2 /= scale
                            y2 /= scale
                            x2 += area[0]
                            y2 += area[1]
                            
                            if area[0]+expanding[0] <= x1 <= area[2]+expanding[2] and area[1]+expanding[1] <= y1 <= area[3]+expanding[3]:
                                continue
                            
                            
                            cv2.circle(draw, (int(x1), int(y1)), 10, (0, 255, 0), -1)  # -1 fills the circle
                            cv2.circle(draw, (int(x2), int(y2)), 10, (0, 255, 0), -1)
                            cv2.line(draw, tuple(map(int, (x1, y1))), tuple(map(int, (x2, y2))), (0, 255, 0), 2)
        
        cv2.imwrite(self.clonePath, draw)
        self.finished.emit()
        return