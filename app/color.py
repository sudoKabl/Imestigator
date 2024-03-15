from PIL import Image
from PyQt5.QtCore import QThread

class ColorWorker(QThread):
    def __init__(self, imagePath, r, g, b, colorPath, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.r = r
        self.g = g
        self.b = b
        self.colorPath = colorPath
        
    def run(self):
        img = Image.open(self.imagePath)
        img = img.convert("RGB")
        r, g, b = img.split()
        
        r = r.point(lambda i: min(255, i * self.r / 100) if self.r > 0 else 0)
        g = g.point(lambda i: min(255, i * self.g / 100) if self.g > 0 else 0)
        b = b.point(lambda i: min(255, i * self.b / 100) if self.b > 0 else 0)
        
        img = Image.merge("RGB", (r, g, b))
        
        img.save(self.colorPath)
        
        self.finished.emit()