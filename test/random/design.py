import PySimpleGUI as sg

def collapseable(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible))

image_column = [
    [
        sg.Text("Bild öffnen"),
        sg.In(size=(25, 1), enable_events=True, key="key_search"),
        sg.FileBrowse()
        
    ],
    [
        sg.Image(key="key_image", s=(200, 200), enable_events=True)
    ]
]

modes_column = [
    [
        sg.Text("Analyse")
    ],
    [
        sg.Button(button_text="Normal", enable_events=True, key="key_filter_none")
    ],
    # ----- ELA STUFF
    [
        sg.Button(button_text="Error-Level-Analysis", enable_events=True, key="key_filter_ela")
    ],
    [
        collapseable(
            [
                [sg.Text("JPEG Qualität", key="key_ela_text")],
                [sg.Slider(orientation='h', key="key_ela_slider", range=(0, 100), default_value=90, enable_events=True)],
            ],
            key="key_ela_column",
            visible=False
        )
    ],
    # ----- NOISE DETECTION STUFF
    [
         sg.Button(button_text="Noise-Analysis", enable_events=True, key="key_filter_noise")
    ],
    # ----- CLONE DETECTION STUFF
    [
        sg.Button(button_text="Clone Detection", enable_events=True, key="key_filter_clone")
    ],
    [
        collapseable(
            [
                [sg.Text("Lower bound")],
                [sg.Slider(orientation='h', key="key_clone_lower", range=(0, 255), default_value=128, enable_events=True)],
                [sg.Text("Upper bound")],
                [sg.Slider(orientation='h', key="key_clone_upper", range=(0, 255), default_value=255, enable_events=True)],
            ],
            key="key_clone_column",
            visible=False
        )
    ],
]


info_column = [
    [
        sg.Text("Exif-Daten:")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, key="key_metadata", size=(45, 5)
        )
    ]
]

layout = [
    [
        sg.Column(image_column, expand_x=True, expand_y=True, justification='center'),
        sg.VSeperator(),
        sg.Column(modes_column, size=(200, 500), justification='right')
    ],
    [
        sg.Column(info_column)
    ]
]



window = sg.Window("Image Viewer", layout, resizable=True, finalize=True)
window.bind('<Configure>', "key_resize")
window["key_image"].expand(expand_x=True, expand_y=True)