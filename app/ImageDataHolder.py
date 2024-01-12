import os
import shutil


class ImageData:
    images = []
    ORIGINAL_IMAGE_PATH = ""
    WORKING_PATH = ""
    WORKING_FOLDER_NAME = ".tmp_analyze"
    
    # Temp Images File Extensions
    extensions = [".tmp.jpg", ".clr.png", ".ela.png", ".noa.png", ".asift.png", ".dsift.png"]
    
    
    def __init__(self, imagePath):

        if os.path.isfile(imagePath):
            self.ORIGINAL_IMAGE_PATH = imagePath
            
            # get folder name and create subfolder
            self.input_image_folder, input_image_name = os.path.split(imagePath)
            file_name, egal = os.path.splitext(input_image_name)
            self.WORKING_PATH = os.path.join(self.input_image_folder, self.WORKING_FOLDER_NAME)
            os.makedirs(self.WORKING_PATH, exist_ok=True)
            
            for ext in self.extensions:
                self.images.append(os.path.join(self.WORKING_PATH, file_name + ext))
            
    def cleanup(self):
        if os.path.exists(self.WORKING_PATH):
            shutil.rmtree(self.WORKING_PATH)
        