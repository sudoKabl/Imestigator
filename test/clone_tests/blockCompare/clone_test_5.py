import cv2
import numpy as np
import math
from PIL import Image, ImageStat, ImageDraw, ImageFilter
import imagehash
import timeit
import time
import pywt

#path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"
path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_2.png"
path_tmp = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_quant.png"

# convert a image using haar wavelets in a jpeg-style compression 
def quantize(image, wavelet='haar', level=1, scale=(8, 8)):
    # grayscale and resize image
    image = image.convert('L')
    image = image.resize(scale, Image.Resampling.NEAREST)

    data = np.array(image, dtype=float)

    # Actual wavelet transform
    coeffs = pywt.wavedec2(data, wavelet, level=level)
    coeffs_arr, coeff_slices = pywt.coeffs_to_array(coeffs)
    
    # Quantization matrix, uniform 
    quantization_matrix = np.ones_like(coeffs_arr) * 50
    quantized_coeffs_arr = np.round(coeffs_arr / quantization_matrix) * quantization_matrix

    quantized_coeffs = pywt.array_to_coeffs(quantized_coeffs_arr, coeff_slices, output_format='wavedec2')

    # Reconstruct image
    blocky_data = pywt.waverec2(quantized_coeffs, 'haar')
    
    # Convert data back to image
    blocky_image = Image.fromarray(np.clip(blocky_data, 0, 255).astype('uint8'))
    
    
    return blocky_image

def run():
    # Load Image, convert to RGBA (for Alpha channel)
    img_org = Image.open(path_org)
    img_org = img_org.convert("RGBA")
    
    

    img_gray = img_org.convert('L')
    
    frameSize = 16
    
    (width, height) = img_org.size
    (w, h) = (width, height)
        
    scale = w / 1024
    w = 1024
    h = math.floor(h / scale)
        
        
    img_resize = img_gray.resize((w, h), resample=Image.Resampling.NEAREST)
    
    
    qXMax = math.floor(w / frameSize) * math.floor(frameSize/2)
    qYMax = math.floor(h / frameSize) * math.floor(frameSize/2)
    qFramesize= math.floor(frameSize/2)
    
    quant_image = Image.new("L", (qXMax, qYMax))    
        
    def getAllHashes(koords):
        x, y = koords
        # This stores all average hashes of all frames that share at least 1 pixel with the current frame
        # this may be overkill but gives pretty good results
        allHashesOfFrame = []
        allHashesOfFrame.clear()
        
        # First hash is generated before the main generation loop
        #qSubimage = quant_image.crop((x - qFramesize + 1, 
        #                            y - qFramesize + 1, 
        #                            x + 2, 
        #                            y + 1))
        
        #subDhash = imagehash.average_hash(qSubimage, hash_size=qFramesize)
        
        #allHashesOfFrame.append([subDhash, (x - qFramesize + 1, y - qFramesize + 1)])
        
        # Main hash generation loop
        for yQ in range(y - qFramesize + 1, y + (2*qFramesize) - 1, 2):
            for xQ in range(x - qFramesize + 1, x + (2*qFramesize) - 1, 2):
                qSubimage = quant_image.crop((xQ, yQ, xQ+qFramesize, yQ+qFramesize))
                
                
                
                stat = ImageStat.Stat(qSubimage)
                
                if stat.stddev[0] > 14:
                    subDhash = imagehash.average_hash(qSubimage, hash_size=qFramesize)
                    # if last hash was the same as this hash, dont store it (just for some performance)
                    #if allHashesOfFrame[-1][0] != subDhash:
                    allHashesOfFrame.append([subDhash, (xQ, yQ)])
                    
        return allHashesOfFrame
    
    # Helper function to get Areas easier
    def getArea(x, y, size):
        return (x, y, x + size, y + size)

    
    # ----- First loop
    # This loop goes through the image in a grid
    # It quantizes the image to make it more efficient to handle
    for x in range(0, w, frameSize):
        for y in range(0, h, frameSize):
            if x + frameSize > w or y + frameSize > h:
                continue
            else:    
                compare_img = img_resize.crop(getArea(x, y, frameSize))
                
                # Quantize Colors of each frame depending on standard deviation
                stat = ImageStat.Stat(compare_img)
                compare_img = compare_img.quantize((math.floor(stat.stddev[0]) + 1) * 3)
                
                # Main quantizing step using jpeg style compression but with haar-wavelet
                compressed = quantize(compare_img, scale=(8, 8), level=3)
                
                # resize the image to fit on quantized image
                compressed = compressed.resize((qFramesize, qFramesize))
                
                # Paste on quantized image
                (quantX, quantY) = (math.floor(x/2), math.floor(y/2))
                quant_image.paste(compressed, (quantX, quantY))
    
    #quant_image.show()
    
    # hashLib saves 2 hashes for each frame in the image:
    # [0] = A pHash of the larger Area of the Frame
    # [1] = An array of all average hashes
    
    hashLib = []
    
    half = math.floor((frameSize * scale) / 2)
    
    # Helper function to convert quant koords to real koords
    def toReal(coord):
        return coord * scale * 2
    
    
    # ----- Second Loop
    # Iterates over the previously generated quantized frame grid
    # This loop does all the hash-generating, filtering and comparing work
    # Draws markers at the end
    for y in range (0, qYMax, qFramesize):
        for x in range(0, qXMax, qFramesize):
            if x + qFramesize > qYMax or y + qFramesize > qYMax:
                continue
            
            # Get standard deviation of current frame
            compare_img = quant_image.crop(getArea(x, y, qFramesize))
            stat = ImageStat.Stat(compare_img)
            
            # Only work with frames that are above a certain detail threshold
            if stat.stddev[0] > 14:
                
                # Generate pHash for 3x3 frame-grid around the central frame
                # This is used to very generically compare two frames to see if a more detailed check is worthwhile
                compare_img = quant_image.crop(getArea(x - qFramesize, y - qFramesize, qFramesize * 3))
                phash = imagehash.phash(compare_img)
                

                # This stores all average hashes of all frames that share at least 1 pixel with the current frame
                # this may be overkill but gives pretty good results
                allHashesOfFrame = []
                
                    
                # This loop compares the current frame with all other known frames
                for hashbundle in hashLib:
                    
                    # This is the very general phash comparison
                    # This primarily acts like a filter
                    if hashbundle[0] - phash < 20:
                        
                        allHashesOfFrame = getAllHashes((x, y))
                        
                        if len(hashbundle[1]) == 0:
                            hashbundle[1] = getAllHashes(hashbundle[2])
                        matches = []
                        
                        # If the phash is OK, compare all current ahashes with the ahashes of that frame
                        for index, dHashA in enumerate(allHashesOfFrame):
                            # clone detection already found a clone
                            # this is more performant, but draws incomplete lines so has been commented out for now
                            #if len(matches) > 300:
                            #    break
                            
                            for i in range(index, len(hashbundle[1])):
                                dHashB = hashbundle[1][i]
                                if dHashA[0] - dHashB[0] < 7:
                                    # save both coordinates to draw lines and frames later
                                    matches.append((dHashA[1], dHashB[1]))

                        # If a minimum amount of matches has been made:
                        if len(matches) > 10:
                            #print(len(matches))
                            # Draw all the frames that have matched!
                            for match in matches:
                                
                                # Create copy to draw on
                                img_copy = Image.new("RGBA", img_org.size, (255, 255, 255, 0))
                                draw = ImageDraw.Draw(img_copy)
                                
                                areaA = (toReal(match[0][0]), toReal(match[0][1]), toReal(match[0][0]) + frameSize * scale * 2, toReal(match[0][1]) + frameSize * scale)
                                
                                draw.rectangle(areaA, fill=(0, 128, 0, 32))

                                areaB = (toReal(match[1][0]), toReal(match[1][1]), toReal(match[1][0]) + frameSize * scale, toReal(match[1][1]) + frameSize * scale)
                                
                                draw.rectangle(areaB, fill=(0, 128, 0, 32))
                                
                                shape = [(areaA[0] + half, areaA[1] + half),(areaB[0] + half, areaB[1] + half)]
                                
                                draw.line(shape, fill=(0, 0, 128, 32))
                                
                                img_org = Image.alpha_composite(img_org, img_copy)   
                                   
                # Add the frame we just handled to the list
                hashLib.append([phash, allHashesOfFrame, (x, y)])
                                
    
    #out = Image.alpha_composite(img_org, img_copy)                    

    #out.show()
    
    
    
    

    img_org.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_result_5.png")    
    


    

exec_time = timeit.timeit(run, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")
