import timeit

def all():
    from ultralytics import FastSAM
    from ultralytics.models.fastsam import FastSAMPrompt
    import numpy as np
    import math
    from PIL import Image, ImageDraw
    import imagehash
    

    path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_2.png"
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
    
    for coord in prompt_process.results[0].boxes.xyxy:
        
        
        area = (
            math.floor(coord.cpu().numpy()[0]), 
            math.floor(coord.cpu().numpy()[1]), 
            math.floor(coord.cpu().numpy()[2]), 
            math.floor(coord.cpu().numpy()[3])
            )
        
        draw.rectangle(area, outline=(0,0,0), width=1)
        
        box = pillage.crop(area)
        
        harry.append((area, imagehash.phash(box)))
        
        
    
    
    for index, el in enumerate(harry):
        areaA = el[0]
        pHashA = el[1]
        
        for i in range(index + 1, len(harry)):
            (areaB, pHashB) = harry[i]
            
            if pHashA - pHashB < 20:
                draw.rectangle(areaA, fill=(0, 128, 0))
                draw.rectangle(areaB, fill=(0, 128, 0))

                shape = [(areaA[0], areaA[1]),(areaB[0], areaB[1])]
                                
                #draw.line(shape, fill=(0, 0, 128))
                
    
    pillage.save("C:\\Users\\Kapsr\\Pictures\\test_image_folder\\fastSamPIL.png")
    

exec_time = timeit.timeit(all, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")

