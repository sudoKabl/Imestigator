from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from PyQt5.QtCore import QThread

class NoiseWorker(QThread):
    def __init__(self, imagePath, noisePath, size, brightness, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.noisePath = noisePath
        self.size = size
        self.brightness = brightness / 100

        
    def run(self):
        img = Image.open(self.imagePath)
    
        median = img.filter(ImageFilter.MedianFilter(self.size))
        
        only_noise = ImageChops.subtract(img, median)
        
        extrema = only_noise.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0/max_diff
        
        scale *= self.brightness
        
        result = ImageEnhance.Brightness(only_noise).enhance(scale)

        result.save(self.noisePath)
                
        self.finished.emit()