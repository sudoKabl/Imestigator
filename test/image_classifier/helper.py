import os
import shutil

path = "\\\\wsl.localhost\\Ubuntu-22.04\\home\kabl\\val2017\\train2017"
#path = "D:\\Hochschule\\Bachelorarbeit\\training_img_raw\\classic\\real"
target = "D:\\Hochschule\\Bachelorarbeit\\training_img_raw\\classic\\real"



images = os.listdir(path)
print(len(images))

for i in range(44270):
    img = os.path.join(path, images[i])

    shutil.move(img, os.path.join(target, images[i]))

if False:
    real = "D:\\Hochschule\\Bachelorarbeit\\training_img\\2\\r"
    fake = s

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
            
            
            
    def explore_folder(path):
        for el in os.listdir(path):
            cur = os.path.join(path, el)
            
            if os.path.isdir(cur):
                if len(os.listdir(cur)) == 0:
                    shutil.rmtree(cur)
                    continue
                else:
                    explore_folder(cur)
            else:
                shutil.move(cur, os.path.join(target, el))


    for sub in os.listdir(path):
        cur = os.path.join(path, sub)
        
        if os.path.isdir(cur):
            explore_folder(cur)