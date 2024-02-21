import timeit

def all():
    from ultralytics import FastSAM
    from ultralytics.models.fastsam import FastSAMPrompt
    import numpy as np
    import math
    from PIL import Image, ImageDraw
    import imagehash
    import cv2
    from scipy.fftpack import dct, idct
    

    path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\259vdk.png_clone.jpg"
    #path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\scale.png"
    #path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\ufo.cache-1.jpg"

    pillage = Image.open(path_org)
    draw = ImageDraw.Draw(pillage)

    model = FastSAM('FastSAM-s.pt')
    
    result = model(path_org, device=0, retina_masks=True, imgsz=1024, conf=0.2, iou=0.7)
    prompt_process = FastSAMPrompt(path_org, result, device=0)
    #ann = prompt_process.everything_prompt()
    
    #prompt_process.plot(annotations=ann, output="C:\\Users\\Kapsr\\Pictures\\test_image_folder\\test")

    harry = []
    
    img = cv2.imread(path_org)
    
    masks = []
    bbox = []
    
    (height, width, _) = img.shape
    
    for mask in prompt_process.results[0].masks:
        contour = mask.cpu().xy.pop()
        contour = contour.astype(np.int32)
        contour = contour.reshape(-1, 1, 2)
        masks.append(contour)
        
    for coord in prompt_process.results[0].boxes.xyxy:
        area = (
                math.floor(coord.cpu().numpy()[0]), 
                math.floor(coord.cpu().numpy()[1]), 
                math.floor(coord.cpu().numpy()[2]), 
                math.floor(coord.cpu().numpy()[3])
                )
        
        #w = area[2] - area[0]
        #h = area[3] - area[1]
        #if w > width / 3 or h > height / 3 or (w < 32 and h < 32):
        #    continue
        
        #draw.rectangle(area)
        
        bbox.append((area[0], area[1], area[2] - area[0], area[3] - area[1]))
    #pillage.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\fastSamPIL.png")
    #return
    # Define the 2D DCT Type II function
    def dct2(a):
        # Perform the DCT on rows
        tmp = dct(a, axis=0, norm='ortho')
        # Then perform the DCT on columns
        return dct(tmp, axis=1, norm='ortho')
    
    
    print(img.shape)
    
    (height, width, _) = img.shape
    
    for i in range(len(masks)):
        x, y, w, h = bbox[i]
        
        if w > width / 3 or h > height / 3 or w < 25 or h < 25:
            continue
        
        background = np.zeros((h, w, 3), dtype=np.uint8)
        
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [masks[i]], -1, color=255, thickness=cv2.FILLED)
        
        contour_pixels = cv2.bitwise_and(img, img, mask=mask)
        
        cropped_contour_pixels = contour_pixels[y:y+h, x:x+w]
        
        background[:h, :w] = cropped_contour_pixels
        
        background = cv2.resize(background, (256, 256))
    
        
        # hashing
        
        resize = cv2.resize(background, (32, 32))
        resize = cv2.cvtColor(resize, cv2.COLOR_RGB2GRAY)
        dct_arr = dct2(resize)
        high_freq = dct_arr[0:8, 0:8]
        
        sum = 0
        
        for x in range(0, 8):
            for y in range(0, 8):
                if x and y == 0:
                    continue
                sum += high_freq[x][y]
        
        mean = sum / 63
        bits = ''
        
        for x in range(0, 8):
            for y in range(0, 8):
                if x and y == 0:
                    continue
                
                if high_freq[x][y] >= mean:
                    bits += '1'
                else:
                    bits += '0'
                    
        hash = int(bits, 2)
        
        harry.append((bbox[i], hash, background))

    for index, el in enumerate(harry):
        areaA = (el[0][0], el[0][1], el[0][0] + el[0][2], el[0][1] + el[0][3])
        pHashA = el[1]
        img1 = el[2]
        
        for i in range(index + 1, len(harry)):
            (areaB, pHashB, img2) = harry[i]
            
            areaB = (areaB[0], areaB[1], areaB[0] + areaB[2], areaB[1] + areaB[3])
            
            if bin(pHashA ^ pHashB).count('1') < 15:

                draw.rectangle(areaA, fill=(0, 128, 0))
                draw.rectangle(areaB, fill=(0, 128, 0))

                shape = [(areaA[0], areaA[1]),(areaB[0], areaB[1])]
                                
                draw.line(shape, fill=(0, 0, 128))

    
    pillage.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\fastSamPIL.png")
    

exec_time = timeit.timeit(all, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")

