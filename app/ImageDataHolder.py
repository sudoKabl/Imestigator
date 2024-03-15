import os
import shutil
from PIL.ExifTags import TAGS
import subprocess


class ImageData:
    images = []
    ORIGINAL_IMAGE_PATH = ""
    WORKING_PATH = ""
    WORKING_FOLDER_NAME = ".tmp_analyze"
    FILE_NAME = ""
    
    # Temp Images File Extensions
    extensions = [".tmp.jpg",  ".clr.png", ".cst.png", ".ela.png", ".noa.png", ".scl.png", ".acl.png", ".kcl.png"]
    
    
    def __init__(self, imagePath):

        if os.path.isfile(imagePath):
            self.ORIGINAL_IMAGE_PATH = imagePath
            
            # get folder name and create subfolder
            self.input_image_folder, input_image_name = os.path.split(imagePath)
            self.FILE_NAME, egal = os.path.splitext(input_image_name)
            self.WORKING_PATH = os.path.join(self.input_image_folder, self.WORKING_FOLDER_NAME)
            os.makedirs(self.WORKING_PATH, exist_ok=True)
            
            for ext in self.extensions:
                self.images.append(os.path.join(self.WORKING_PATH, self.FILE_NAME + ext))
                
            
    def cleanup(self):
        if os.path.exists(self.WORKING_PATH):
            shutil.rmtree(self.WORKING_PATH)
        
        self.images.clear()
        
    def metadata(self):
        exiftoolpath = os.path.join(os.getcwd(), "app")
        exiftoolpath = os.path.join(exiftoolpath, "exiftool.exe")
        
        process = subprocess.Popen([exiftoolpath, self.ORIGINAL_IMAGE_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        result = []
        for tag in process.stdout:
            line = tag.strip().split(':')
            result.append(line)
        
        if result == {}:
            result.append("No data found")
            return result
        
        return result