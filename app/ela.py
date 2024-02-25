from PIL import Image, ImageChops, ImageEnhance
import math
import os
from PyQt5.QtCore import QThread

class ELAWorker(QThread):
    def __init__(self, imagePath, elaPath, q, offset_x, offset_y, parent=None):
        super().__init__(parent)
        self.imagePath = imagePath
        self.elaPath = elaPath
        
        self.q = q
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        
    def run(self):
        img_org = Image.open(self.imagePath)
        img_org = img_org.convert('RGB')
        img_tmp_path = self.elaPath + ".tmp_ela.jpg"
        
        shifted_image = Image.new(img_org.mode, img_org.size)
        shifted_image.paste(img_org, (self.offset_x, self.offset_y))
        
        shifted_image.save(img_tmp_path, 'JPEG', quality=math.floor(self.q))
        
        tmp_img = Image.open(img_tmp_path)
        
        shifted_image = Image.new(img_org.mode, img_org.size)
        shifted_image.paste(tmp_img, (-self.offset_x, -self.offset_y))
        
        img_ela = ImageChops.difference(img_org, shifted_image)

        extrema = img_ela.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0/max_diff
        img_ela = ImageEnhance.Brightness(img_ela).enhance(scale)
        
        img_ela.save(self.elaPath)
        os.remove(img_tmp_path)
        
        self.finished.emit()