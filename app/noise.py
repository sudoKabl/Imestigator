from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps
from PyQt5.QtCore import QThread
import cv2
import numpy as np

class NoiseWorker(QThread):
    def __init__(self, imagePath, noisePath, size, brightness, useSharp, subtractEdges, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.noisePath = noisePath
        
        self.size = size
        self.brightness = brightness / 100
        self.useSharp = useSharp
        self.subtractEdges = subtractEdges

        
    def run(self):
        img_org = Image.open(self.imagePath)
        img_org = img_org.convert('RGB')
        
        if self.useSharp:
            filtered = img_org.filter(ImageFilter.UnsharpMask(self.size))
        else:
            filtered = img_org.filter(ImageFilter.MedianFilter(self.size))
            
        
        only_noise = ImageChops.subtract(img_org, filtered)
        
        if self.subtractEdges:
            image = cv2.imread(self.imagePath)
            blurred = cv2.GaussianBlur(image, (5, 5), 0)
            edges = cv2.Canny(blurred, 128, 255)
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            tmp_path = self.noisePath + ".tmp.png"
            cv2.imwrite(tmp_path, edges)
            
            edges = Image.open(tmp_path)
            edges = edges.convert('RGB')
        
            only_noise = ImageChops.subtract(only_noise, edges)
        
        extrema = only_noise.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff != 0:
            scale = 255.0/max_diff
        else:
            scale = 255.0
            
        scale *= self.brightness
        
        result = ImageEnhance.Brightness(only_noise).enhance(scale)

        result.save(self.noisePath)
        self.finished.emit()