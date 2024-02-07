import timeit

def all():
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
    import cv2

    path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\klon_bearbeitet_2.png"
    #path_org = "C:\\Users\\Kapsr\\Pictures\\test_image_folder\\haar_quant.png"

    image = cv2.imread(path_org)
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #image = cv2.equalizeHist(image)
    #image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    def show_anns(anns):
        if len(anns) == 0:
            return
        sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
        
        for ann in sorted_anns:
            m = ann['bbox']
            #print(m)

            # Coordinates must be a tuple - (x,y)
            cv2.rectangle(image,(m[0], m[1]),(m[0] + m[2], m[1] + m[3]),(0,0,0),1)                   #Color is by default black




    sam = sam_model_registry["default"](checkpoint="F:\\Dokumente\\Business\\Hochschule\\Bachelorarbeit\\sam_vit_h_4b8939.pth")
    sam.to(device="cuda")


    #mask_generator = SamAutomaticMaskGenerator(sam)




    #masks = mask_generator.generate(image)


    mask_generator_2 = SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=32,
        pred_iou_thresh=0.86,
        stability_score_thresh=0.92,
        crop_n_layers=1,
        crop_n_points_downscale_factor=2,
        min_mask_region_area=100,  # Requires open-cv to run post-processing
    )

    masks2 = mask_generator_2.generate(image)

    show_anns(masks2)

    #cv2.imshow("Window Name", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

exec_time = timeit.timeit(all, number=1)
print(f"Ausführungszeit: {exec_time} Sekunden")