import os
import shutil

path = "D:\\Hochschule\\Bachelorarbeit\\training_img\\2\\IMD2020 Edit"
real = "D:\\Hochschule\\Bachelorarbeit\\training_img\\2\\r"
fake = "D:\\Hochschule\\Bachelorarbeit\\training_img\\2\\f"

orig_endings = ("_orig.jpg", "_orig.png")
edit_endings = ("_0.jpg", "_0.png")

for sub in os.listdir(path):
    cur = os.path.join(path, sub)
    
    for image in os.listdir(cur):
        if image.endswith(orig_endings):
            shutil.copyfile(os.path.join(cur, image), os.path.join(real, image))
        
        elif image.endswith(edit_endings):
            shutil.copyfile(os.path.join(cur, image), os.path.join(fake, image))
        
        else:
            print(cur)    
        