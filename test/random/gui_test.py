import PySimpleGUI as sg
import os.path
from time import sleep
import math

from design import window
from image_data_holder import ImageData

if __name__ == '__main__':

    current_file = None
    button_switch = 0

    def switch_off():
        window["key_ela_column"].update(visible=False)
        window["key_clone_column"].update(visible=False)
        window.refresh()
        

    while True:
        event, values = window.read()
        
        if event == "OK" or event == sg.WIN_CLOSED:
            print("End event")
            break
        
        elif event == "key_resize":
            (x, y) = window.size
            
            window["key_image"].update(size=(math.floor(x * 0.8), math.floor(x * 0.8)))
            
            if current_file is not None:
                window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
        
        # ----- Search for new Image event
        elif event == "key_search":
            window["key_image"].update(data=sg.DEFAULT_BASE64_LOADING_GIF)
            window.refresh()
            image = values["key_search"]
            
            if os.path.isfile(os.path.join(image)):
                current_file = None
                current_file = ImageData(image)
                
                window["key_search"].update(image)
                window["key_metadata"].update(values=current_file.images[0].metadata())
                window["key_image"].update(data=current_file.images[0].scale_image_event())
                window.refresh()
                print(window["key_image"].get_size())
        
        if current_file != None:
            # ----- Button for default Image
            if event == "key_filter_none":
                try:
                    button_switch = 0
                    switch_off()
                    window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
                except:
                    pass
            
            # ----- ELA
            elif event == "key_filter_ela":
                try:
                    button_switch = 1
                    switch_off()
                    window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
                    window["key_ela_column"].update(visible=True)
                    
                except:
                    pass
                
            elif event == "key_ela_slider":
                current_file.update_ela(values["key_ela_slider"])
                window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
        
        # ----- CLONE DETECTION
            elif event == "key_filter_clone":
                #try:
                    button_switch = 2
                    switch_off()
                    window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
                    window["key_clone_column"].update(visible=True)
                #except:
                #    pass
            elif event == "key_clone_lower" or event == "key_clone_upper":
                current_file.update_clone(values["key_clone_lower"], values["key_clone_upper"])
                window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
                
            elif event == "key_filter_noise":
                button_switch = 3
                switch_off()
                window["key_image"].update(data=current_file.images[button_switch].scale_image_event())
    
        
                
        
        
    window.close()
