from PIL import Image, ImageChops, ImageEnhance
import io
import os
from PIL.ExifTags import TAGS
from design import window
import PySimpleGUI as sg
import math
import cv2 as cv
import imagehash
import numpy as np
from multiprocessing import Process, Queue


class ImageData:
    images = [None] * 4
    image_path = ""
    tmp_fname = ""
    ela_fname = ""
    input_image_folder = ""
    
    def __init__(self, imagePath) -> None:
        self.images = [None] * 4
        
        # get folder name and create subfolder
        self.input_image_folder, input_image_name = os.path.split(imagePath)
        file_name, egal = os.path.splitext(input_image_name)
        self.input_image_folder = os.path.join(self.input_image_folder, "tmp_analyse")
        os.makedirs(self.input_image_folder, exist_ok=True)
        
        # check if image size is bigger than max size for performance reasons
        im = Image.open(imagePath)
        (x, y) = im.size
        
        while x > 1920 or y > 1080:
            x /= 2
            y /= 2
            
        im = im.resize((math.floor(x), math.floor(y)), Image.Resampling.BILINEAR)
        
        self.image_path = os.path.join(self.input_image_folder, input_image_name)
        im.save(self.image_path)
        
        self.images[0] = CustomImage(self.image_path)
        
        
        # ----- Create subfolder and names for all temp-files of the filters
        TMP_EXT = ".tmp.jpg"
        ELA_EXT = ".ela.png"
        CLONE_EXT = ".clone.png"
        NOISE_EXT = ".noise.png"
        
        
        # create filenames
        self.tmp_fname = os.path.join(self.input_image_folder, file_name + TMP_EXT)
        self.ela_fname = os.path.join(self.input_image_folder, file_name + ELA_EXT)
        self.clone_fname = os.path.join(self.input_image_folder, file_name + CLONE_EXT)
        self.noise_fname = os.path.join(self.input_image_folder, file_name + NOISE_EXT)
        
        # ----- Create different filtered Images
        
        ela_process = Process(target=self.ela, args=(90,))
        ela_process.start()
        #self.images[1] = CustomImage(self.ela(90))
        
        clone_process = Process(target=self.detect_clones)
        clone_process.start()
        #self.images[2] = CustomImage(self.detect_clones())
        
        noise_process = Process(target=self.noise)
        noise_process.start()
        #self.images[3] = CustomImage(self.noise())
        
        ela_process.join()
        self.images[1] = CustomImage(self.ela_fname)
        
        clone_process.join()
        self.images[2] = CustomImage(self.clone_fname)
        
        noise_process.join()
        self.images[3] = CustomImage(self.noise_fname)
        
        
    
    def ela(self, q):
        if not os.path.isfile(self.ela_fname):
            if not os.path.isfile(self.tmp_fname):
                im = Image.open(self.image_path)
                im.save(self.tmp_fname, 'JPEG', quality=math.floor(q))
            else:
                im = Image.open(self.tmp_fname)

            tmp_fname_im = Image.open(self.tmp_fname)
            ela_im = ImageChops.difference(im, tmp_fname_im)

            extrema = ela_im.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            scale = 255.0/max_diff
            ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)

            ela_im.save(self.ela_fname)
        
        if os.path.isfile(self.tmp_fname):
            os.remove(self.tmp_fname)
        
        return
        
    def update_ela(self, q):
        os.remove(self.ela_fname)
        if len(self.images) > 1:
            self.images[1] = CustomImage(self.ela(q))
            
    def detect_clones(self, lower_bound=128, upper_bound=255, tolerance=20, min_matches=2):
        img = cv.imread(self.image_path)
        sift = cv.SIFT_create()
        bf = cv.BFMatcher()
        point_in_struct = []
        matches = []
        i = 0
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        gray = cv.equalizeHist(gray)
        gray = cv.GaussianBlur(gray,(5,5),0)
        
        ddepth = cv.CV_16S
        kernel_size = 3
        
        lp = cv.Laplacian(gray, ddepth, ksize=kernel_size)
        displ = cv.convertScaleAbs(lp)
        #cv.imshow("lp", displ)
        #cv.imshow("gray", gray)
        
        gray = cv.addWeighted(gray, 0.7, displ, 0.3, 0.0)
        
        height, width = gray.shape
        w, h = (math.floor(width/2), math.floor(height/2))
        
        gray = cv.resize(gray, (w, h), interpolation=cv.INTER_LINEAR)
        
        gray = cv.medianBlur(gray,3)
        gray = cv.adaptiveThreshold(gray,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
        
        
        kernel = np.ones((3,3),np.uint8)
        gray = cv.morphologyEx(gray, cv.MORPH_OPEN, kernel)
        gray = cv.morphologyEx(gray, cv.MORPH_CLOSE, kernel)

        gray = cv.resize(gray, (width, height), interpolation=cv.INTER_NEAREST)
        
        #cv.imshow('result', gray)

        kp, des = sift.detectAndCompute(img, None)
        
        contours, _ = cv.findContours(gray, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        
        hulls = []
        
        for cont in contours:
            hull = cv.convexHull(cont)
            hulls.append(hull)
            
        
        filtered_contours = [cnt for cnt in contours if 10 < cv.contourArea(cnt) < 20000]
        
        des_of_object = [[] for _ in range(len(filtered_contours))]
        kp_of_object = [[] for _ in range(len(filtered_contours))]
        indexes = [[] for _ in range(len(filtered_contours))]
        
        
        for index_kp, point in enumerate(kp):
            (x, y) = point.pt
            
            for index_c, contour in enumerate(filtered_contours):
                if i == 0:
                    i = 1
                    continue
                
                dist = cv.pointPolygonTest(contour, (x, y), True)
                if dist >= -tolerance:
                    point_in_struct.append(point)
                    
                    des_of_object[index_c].append(des[index_kp])
                    kp_of_object[index_c].append(kp[index_kp])
                    indexes[index_c].append(index_kp)
                    
                    break
        
        img = cv.drawKeypoints(img, point_in_struct, img)
        
        # Draw contours
        for contour in filtered_contours:
            if i == 0:
                i = 1
                continue
            cv.drawContours(img, [contour], 0, (0, 0, 255), 1) 
    
        tester = 0
        for index, obj_des in enumerate(des_of_object):
            np_des = np.array(obj_des)
            
            if len(obj_des) == 0:
                continue
            #TODO:
            # des hier anpassen, sodass np_des nicht enthalten ist
            # alternativ: np des in den matches ausschließen?
            
            temp_des = des.copy()
            
            for to_delete in reversed(indexes[index]):
                temp_des = np.delete(temp_des, to_delete, 0)
            
            matches = bf.knnMatch(np_des, temp_des, k=2)
            kps = kp_of_object[index]
            
            if matches != []:
                good = []
                
                for m,n in matches:
                    if m.distance < 0.75*n.distance:
                        good.append([m])
                
                if len(good) > min_matches:
                    for match_obj in good:
                        tester += 1
                        for dingsi in match_obj:
                            pt1 = tuple(map(int, kps[dingsi.queryIdx].pt))
                            pt2 = tuple(map(int, kp[dingsi.trainIdx].pt))
                            cv.line(img, pt1, pt2, (0, 255, 0), 2)

        cv.imwrite(self.clone_fname, img)
            
    def update_clone(self, lower, upper):
        os.remove(self.clone_fname)
        self.images[2] = CustomImage(self.detect_clones(lower, upper))
        
    def noise(self, block_size=9):
        img = cv.imread(self.image_path)
        
        # Convert the image to grayscale
        gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Calculate the standard deviation of pixel intensities in each local block
        std_dev_map = cv.GaussianBlur(gray_image.astype(np.float64), (block_size, block_size), 0)
        std_dev_map = np.sqrt((gray_image - std_dev_map) ** 2)

        # Normalize the standard deviation map to the range [0, 255]
        std_dev_map = cv.normalize(std_dev_map, None, 0, 255, cv.NORM_MINMAX)
        
        std_dev_map = std_dev_map.astype(np.uint8)
        
        std_dev_map = cv.equalizeHist(std_dev_map)
        
        cv.imwrite(self.noise_fname, std_dev_map.astype(np.uint8))
        
class CustomImage:
    display_image = None
    pil_image = None
    
    def __init__(self, image) -> None:
        
        if isinstance(image, str):
            self.pil_image = Image.open(image)
        
        else:
            self.pil_image = image
        
        self.display_image = convert_PIL_img_to_bytes(self.pil_image)
    
        
    def metadata(self):
        exifdata = self.pil_image.getexif()
        
        result = []
        
        if exifdata == {}:
            result.append("Keine Daten gefunden")
            return result
        
        # iterating over all EXIF data fields
        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            # decode bytes 
            if isinstance(data, bytes):
                data = data.decode(encoding="latin-1")
            result.append(f"{tag:25}: {data}")
        
        return result
    
    def scale_image_event(self):
        return convert_PIL_img_to_bytes(scale_image_to_window(self.pil_image))
        

def convert_PIL_img_to_bytes(img):
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    
    
def scale_image_to_window(img):
    (x, y) = img.size
    
    (win_x, win_y) = window["key_image"].get_size()
    
    if x >= y:
        scale = x / win_x
        y = y / scale
        x = win_x
    else:
        scale = y / win_y
        x = x / scale
        y = win_y
    
    scaled_image = img.resize((math.floor(x), math.floor(y)), Image.Resampling.BILINEAR)
    
    return scaled_image