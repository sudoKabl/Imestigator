from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import math

from app.ImageDataHolder import ImageData

from app.color import ColorWorker
from app.ela import ELAWorker
from app.noise import NoiseWorker
from app.blockCompare import blockCompareWorker
from app.detectingSIFT import detectingSIFTWorker

class Imestigator(QMainWindow):
    FILESTATE = True
    MODESTATE = True
    ACTIVE_MODE = 0
    
    CURRENT_FILE = None
    
    CLONE_OPTION = 0
    
    WORKERS = []
    
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Imestigator")
        desktop = QApplication.desktop().screenGeometry()
        width = desktop.width()
        height = desktop.height()
        
        self.setGeometry(math.floor(width / 4), math.floor(height / 4), math.floor(width / 2), math.floor(height / 2))
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.file_column = QFrame()
        self.file_column.setLayout(self.initFileColumn())
        self.file_column.setMaximumWidth(300)
        
        self.mode_column = self.initModesColumn()
        
        self.imageLabel = QLabel()
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setStyleSheet("background-color: lightgray")
        
        self.files_button = QPushButton()
        self.files_button.setText("<")
        self.files_button.setMaximumSize(25, 25)
        
        self.modes_button = QPushButton()
        self.modes_button.setText(">")
        self.modes_button.setMaximumSize(25, 25)
        
        self.files_button.clicked.connect(self.toggleFiles)
        self.modes_button.clicked.connect(self.toggleModes)
        
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.file_column)
        self.main_layout.addWidget(self.files_button)
        self.main_layout.addWidget(self.imageLabel)
        self.main_layout.addWidget(self.modes_button)
        self.main_layout.addWidget(self.mode_column)
        
        
        self.central_widget.setLayout(self.main_layout)
        
        
    
    def initFileColumn(self):
        file_column = QVBoxLayout()
        
        search_field = QLineEdit()
        search_field.setPlaceholderText("Search or paste path")
        
        self.had_path = ""
        
        def filterTree():
            search_text = search_field.text()
            
            if search_text == '':
                model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.gif"])
                model.setFilter(QDir.Filter.NoFilter)
                self.tree.setRootIndex(model.index(''))
                self.had_path = ""
            else:
                if QDir(search_text).exists():
                    model.setRootPath(search_text)
                    model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.gif"])
                    model.setFilter(QDir.Filter.NoFilter)
                    self.tree.setRootIndex(model.index(search_text))
                    self.had_path = search_text
                else:
                    if self.had_path != "":
                        if self.had_path in search_text:
                            search_text = search_text.replace(self.had_path, "", 1)
                    model.setNameFilters([f"*{search_text}*.jpg", f"*{search_text}*.jpeg", f"*{search_text}*.png", f"*{search_text}*.gif"])
                    model.setFilter(QDir.Filter.Files | QDir.Filter.Drives | QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot)
        
        
        search_field.textChanged.connect(filterTree)
        
        model = QFileSystemModel()
        model.setRootPath('')
        model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.gif"])
        model.setNameFilterDisables(False)
        
        self.tree = QTreeView()
        self.tree.setModel(model)
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tree.setWindowTitle("Search for Files")
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        for column in range(1, model.columnCount()):
            self.tree.hideColumn(column)
            
        def openImage(index):
            path = model.filePath(index)
            if QFileInfo(path).isFile():
                if self.isSomethingRunning() == False:

                    if self.CURRENT_FILE != None and self.CURRENT_FILE.ORIGINAL_IMAGE_PATH != path:
                        self.CURRENT_FILE.cleanup()

                    self.ACTIVE_MODE = 0
                    self.collapse()
                    pixmap = QPixmap(path)
                    
                    if pixmap.isNull():
                        print("Failed to load image")
                    else:
                        scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.imageLabel.setPixmap(scaled_pixmap)
                        self.CURRENT_FILE = ImageData(path)
                        print("Image loaded successfully")
                        self.buildImages()
            
        self.tree.doubleClicked.connect(openImage)
        
        file_column.addWidget(search_field)
        file_column.addWidget(self.tree)
        
        return file_column
        
        
    def initModesColumn(self):
        layout = QVBoxLayout()
        
        # ----- No filter
        self.NONE_BUTTON = QPushButton("None")
        self.NONE_BUTTON.setToolTip("View original image")
        self.NONE_BUTTON.clicked.connect(self.noneClicked)
        
        # ----- Color correction
        self.COLOR_BUTTON = QPushButton("Color correction")
        self.COLOR_BUTTON.setToolTip("Change color composition of image")
        self.COLOR_BUTTON.clicked.connect(self.colorClicked)
        
        self.COLOR_RED = QGroupBox()
        self.COLOR_RED.setTitle("Red")
        r = QVBoxLayout()
        self.RED_SLIDER = self.hSlider(100, 0, 100)
        r.addWidget(self.RED_SLIDER)
        r.addLayout(self.hSliderLabels(self.RED_SLIDER))
        self.COLOR_RED.setLayout(r)
        self.COLOR_RED.hide()
        
        self.RED_SLIDER.valueChanged.connect(self.updateColor)
        
        
        self.COLOR_GREEN = QGroupBox()
        self.COLOR_GREEN.setTitle("Green")
        g = QVBoxLayout()
        self.GREEN_SLIDER = self.hSlider(100, 0, 100)
        g.addWidget(self.GREEN_SLIDER)
        g.addLayout(self.hSliderLabels(self.GREEN_SLIDER))
        self.COLOR_GREEN.setLayout(g)
        self.COLOR_GREEN.hide()
        
        self.GREEN_SLIDER.valueChanged.connect(self.updateColor)
        
        
        self.COLOR_BLUE = QGroupBox()
        self.COLOR_BLUE.setTitle("Blue")
        b = QVBoxLayout()
        self.BLUE_SLIDER = self.hSlider(100, 0, 100)
        b.addWidget(self.BLUE_SLIDER)
        b.addLayout(self.hSliderLabels(self.BLUE_SLIDER))
        self.COLOR_BLUE.setLayout(b)
        self.COLOR_BLUE.hide()
        
        self.BLUE_SLIDER.valueChanged.connect(self.updateColor)
        
        
        # ----- Error level analysis
        self.ELA_BUTTON = QPushButton("Error Level Analysis")
        self.ELA_BUTTON.setToolTip("Perform Error Level Analysis")
        self.ELA_BUTTON.clicked.connect(self.elaClicked)

        self.ELA_QUALITY_GROUPBOX = QGroupBox()
        self.ELA_SLIDER = self.hSlider(90, 1, 100)
        self.ELA_SLIDER.sliderReleased.connect(self.updateEla)
        
        self.SLIDER_IS_PRESSED = False
        
        def elaClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateEla()
        
        self.ELA_SLIDER.valueChanged.connect(elaClick)
        
        def sliderDisabler():
            self.SLIDER_IS_PRESSED = True
        
        self.ELA_SLIDER.sliderPressed.connect(sliderDisabler)
        
        ela_l = QVBoxLayout()
        ela_l.addWidget(self.ELA_SLIDER)
        ela_l.addLayout(self.hSliderLabels(self.ELA_SLIDER))
        self.ELA_QUALITY_GROUPBOX.setLayout(ela_l)
        self.ELA_QUALITY_GROUPBOX.setTitle("JPG Quality")
        self.ELA_QUALITY_GROUPBOX.hide()
        
        # For changing offset of comparing-image
        self.ELA_OFFSET_GROUPBOX = QGroupBox()
        
        label_x = QLabel("X-Axis")
        
        self.ELA_OFFSET_SLIDER_X = self.hSlider(0, 0, 7)
        self.ELA_OFFSET_SLIDER_X.sliderReleased.connect(self.updateEla)
        self.ELA_OFFSET_SLIDER_X.valueChanged.connect(elaClick)
        self.ELA_OFFSET_SLIDER_X.sliderPressed.connect(sliderDisabler)
        
        label_y = QLabel("Y-Axis")
        
        self.ELA_OFFSET_SLIDER_Y = self.hSlider(0, 0, 7)
        self.ELA_OFFSET_SLIDER_Y.sliderReleased.connect(self.updateEla)
        self.ELA_OFFSET_SLIDER_Y.valueChanged.connect(elaClick)
        self.ELA_OFFSET_SLIDER_Y.sliderPressed.connect(sliderDisabler)
        
        ela_o = QVBoxLayout()
        ela_o.addWidget(label_x)
        ela_o.addWidget(self.ELA_OFFSET_SLIDER_X)
        ela_o.addLayout(self.hSliderLabels(self.ELA_OFFSET_SLIDER_X))
        ela_o.addWidget(label_y)
        ela_o.addWidget(self.ELA_OFFSET_SLIDER_Y)
        ela_o.addLayout(self.hSliderLabels(self.ELA_OFFSET_SLIDER_Y))
        
        self.ELA_OFFSET_GROUPBOX.setLayout(ela_o)
        self.ELA_OFFSET_GROUPBOX.setTitle("JPG Offset")
        self.ELA_OFFSET_GROUPBOX.hide()
        
        # ----- Noise analysis
        
        self.NOA_BUTTON = QPushButton("Noise Analysis")
        self.NOA_BUTTON.setToolTip("Perform general noise analysis")
        self.NOA_BUTTON.clicked.connect(self.noaClicked)
        
        self.NOA_CONTENT = QWidget()
        noa_content_layout = QVBoxLayout()
        
        self.NOA_USEMEDIAN = QCheckBox("Use Median Filter")
        self.NOA_USEMEDIAN.clicked.connect(self.updateNoa)
        self.NOA_SUBTRACTEDGES = QCheckBox("Edge reduction")
        self.NOA_SUBTRACTEDGES.clicked.connect(self.updateNoa)
        
        noa_content_layout.addWidget(self.NOA_USEMEDIAN)
        noa_content_layout.addWidget(self.NOA_SUBTRACTEDGES)
        
        def noaClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateNoa()
        
        noa_i_gb = QGroupBox()
        noa_l = QVBoxLayout()
        self.NOA_SLIDER_FILTER_INTENSITY = self.hSlider(3, 3, 15)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_INTENSITY.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderPressed.connect(sliderDisabler)
        
        noa_b_gb = QGroupBox()
        noa_b = QVBoxLayout()
        self.NOA_SLIDER_FILTER_BRIGHTNESS = self.hSlider(300, 1, 500)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderPressed.connect(sliderDisabler)
        
        noa_l.addWidget(self.NOA_SLIDER_FILTER_INTENSITY)
        noa_l.addLayout(self.hSliderLabels(self.NOA_SLIDER_FILTER_INTENSITY))
        
        noa_b.addWidget(self.NOA_SLIDER_FILTER_BRIGHTNESS)
        noa_b.addLayout(self.hSliderLabels(self.NOA_SLIDER_FILTER_BRIGHTNESS))
        
        noa_i_gb.setLayout(noa_l)
        noa_i_gb.setTitle("Filter intensity")
        noa_content_layout.addWidget(noa_i_gb)
        
        noa_b_gb.setLayout(noa_b)
        noa_b_gb.setTitle("Brightness")
        noa_content_layout.addWidget(noa_b_gb)
        
        self.NOA_CONTENT.setLayout(noa_content_layout)
        self.NOA_CONTENT.hide()
        
        # ----- Clone detection
        
        self.CLONE_BUTTON = QPushButton("Clone Detection")
        self.CLONE_BUTTON.clicked.connect(self.cloneClicked)
        
        self.CLONE_RADIO_AUTO = QRadioButton("Frame by frame")
        self.CLONE_RADIO_AUTO.toggled.connect(self.cloneRadioButtonToggled)
        self.CLONE_RADIO_AUTO.toggle()
        
        self.CLONE_RADIO_DETECTING = QRadioButton("SIFT + Object detection")
        self.CLONE_RADIO_DETECTING.toggled.connect(self.cloneRadioButtonToggled)
        self.CLONE_RADIO_DETECTING.setEnabled(False)
        
        clone_radiobuttons = QVBoxLayout()
        clone_radiobuttons.addWidget(self.CLONE_RADIO_AUTO)
        clone_radiobuttons.addWidget(self.CLONE_RADIO_DETECTING)
        
        self.CLONE_RADIO_GROUPBOX = QGroupBox()
        self.CLONE_RADIO_GROUPBOX.setLayout(clone_radiobuttons)
        self.CLONE_RADIO_GROUPBOX.setTitle("Comparison options")
        self.CLONE_RADIO_GROUPBOX.hide()
        
        self.CLONE_AUTO_GROUPBOX = QGroupBox()
        self.CLONE_DETECTING_GROUPBOX = QGroupBox()
        
        self.CLONE_AUTO_GROUPBOX.setTitle("Options")
        self.CLONE_DETECTING_GROUPBOX.setTitle("Options")
        
        def cloneClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateClone()
        
        auto_layout = QVBoxLayout()
        
        blocksize_label = QLabel("Block size")
        
        self.CLONE_AUTO_SLIDER_BLOCKSIZE = self.hSlider(8, 4, 64)
        self.CLONE_AUTO_SLIDER_BLOCKSIZE.sliderReleased.connect(self.updateClone)
        self.CLONE_AUTO_SLIDER_BLOCKSIZE.valueChanged.connect(cloneClick)
        self.CLONE_AUTO_SLIDER_BLOCKSIZE.sliderPressed.connect(sliderDisabler)
        
        min_detail_label = QLabel("Minimum detail level")
        
        self.CLONE_AUTO_SLIDER_DETAIL = self.hSlider(5, 1, 50)
        self.CLONE_AUTO_SLIDER_DETAIL.sliderReleased.connect(self.updateClone)
        self.CLONE_AUTO_SLIDER_DETAIL.valueChanged.connect(cloneClick)
        self.CLONE_AUTO_SLIDER_DETAIL.sliderPressed.connect(sliderDisabler)
        
        min_similar_label = QLabel("Minimum similarity")
        
        self.CLONE_AUTO_SLIDER_SIMILAR = self.hSlider(10, 1, 25)
        self.CLONE_AUTO_SLIDER_SIMILAR.sliderReleased.connect(self.updateClone)
        self.CLONE_AUTO_SLIDER_SIMILAR.valueChanged.connect(cloneClick)
        self.CLONE_AUTO_SLIDER_SIMILAR.sliderPressed.connect(sliderDisabler)
        
        hashing_algo_label = QLabel("Hashing algorithm")
        
        self.CLONE_AUTO_HASH_ALGO_RADIO = []
        
        algo_names = ["Color", "Average", "Perceptual", "Difference", "Wavelet", "Crop-Resistant"]
        
        for item in algo_names:
            radio = QRadioButton(item)
            radio.toggled.connect(self.updateClone)
            self.CLONE_AUTO_HASH_ALGO_RADIO.append(radio)
            
            
        self.CLONE_AUTO_HASH_ALGO_RADIO[0].toggle()
        

        
        
        auto_layout.addWidget(blocksize_label)
        auto_layout.addWidget(self.CLONE_AUTO_SLIDER_BLOCKSIZE)
        auto_layout.addLayout(self.hSliderLabels(self.CLONE_AUTO_SLIDER_BLOCKSIZE))
        
        auto_layout.addWidget(min_detail_label)
        auto_layout.addWidget(self.CLONE_AUTO_SLIDER_DETAIL)
        auto_layout.addLayout(self.hSliderLabels(self.CLONE_AUTO_SLIDER_DETAIL))
        
        auto_layout.addWidget(min_similar_label)
        auto_layout.addWidget(self.CLONE_AUTO_SLIDER_SIMILAR)
        auto_layout.addLayout(self.hSliderLabels(self.CLONE_AUTO_SLIDER_SIMILAR))
        
        auto_layout.addWidget(hashing_algo_label)
        for item in self.CLONE_AUTO_HASH_ALGO_RADIO:
            auto_layout.addWidget(item)
        
        
        self.CLONE_AUTO_GROUPBOX.setLayout(auto_layout)
        self.CLONE_AUTO_GROUPBOX.hide()
        
        
        
        # ----- Add all the elements to column
        layout.addWidget(self.NONE_BUTTON)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.COLOR_BUTTON)
        layout.addWidget(self.COLOR_RED)
        layout.addWidget(self.COLOR_GREEN)
        layout.addWidget(self.COLOR_BLUE)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.ELA_BUTTON)
        layout.addWidget(self.ELA_QUALITY_GROUPBOX)
        layout.addWidget(self.ELA_OFFSET_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.NOA_BUTTON)
        layout.addWidget(self.NOA_CONTENT)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.CLONE_BUTTON)
        layout.addWidget(self.CLONE_RADIO_GROUPBOX)
        layout.addWidget(self.CLONE_AUTO_GROUPBOX)
        
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)
        
        box = QGroupBox()
        box.setLayout(layout)
        box.setTitle("Functions and Filters")
        box.setMaximumWidth(250)
        
        return box

    # ----- OVERRIDDEN FUNCTIONS 
    
    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.imageLabel.pixmap() != None:
            self.scaleImage()   
            return super().resizeEvent(a0)
        
    def closeEvent(self, event):
        if self.CURRENT_FILE != None:
            self.CURRENT_FILE.cleanup()
        event.accept()
    
    
    # ----- HELPER FUNCTIONS FOR GETTING ELEMENTS
    
    def makeLine(self):
        h_line = QFrame()
        h_line.setGeometry(QRect(320, 150, 118, 3))
        h_line.setFrameShape(QFrame.Shape.HLine)
        h_line.setFrameShadow(QFrame.Shadow.Sunken)
        return h_line
    
    
    def hSlider(self, value, min, max):
        slider = QSlider()
        slider.setRange(min, max)
        slider.setValue(value)
        slider.setOrientation(Qt.Orientation.Horizontal)
        return slider
    
    
    def hSliderLabels(self, slider):
        layout = QHBoxLayout()
        
        currentValueLabel = QLineEdit(f"{slider.value()}")
        currentValueLabel.setStyleSheet("background-color: lightgray")
        currentValueLabel.setAlignment(Qt.AlignCenter)
        currentValueLabel.setMaximumWidth(50)
        
        minLabel = QLabel(f"{slider.minimum()}")
        minLabel.setAlignment(Qt.AlignLeft)
        
        maxLabel = QLabel(f"{slider.maximum()}")
        maxLabel.setAlignment(Qt.AlignRight)
        
        layout.addWidget(minLabel)
        layout.addWidget(currentValueLabel)
        layout.addWidget(maxLabel)
        
        def updateTextValue():
            currentValueLabel.setText(f"{slider.value()}")
            
        def updateSliderValue():
            currentValueLabel.clearFocus()
            if currentValueLabel.text() != "":
                number = int(currentValueLabel.text())
                if number >= slider.minimum() and number <= slider.maximum():
                    slider.setValue(number)
                    slider.valueChanged.emit(number)
                else:
                    updateTextValue()
        
        slider.valueChanged.connect(updateTextValue)
        currentValueLabel.returnPressed.connect(updateSliderValue)
        
        return layout
    
    # ----- FUNCTIONS FOR CHANGING VIEW OR LAYOUT
    
    def toggleFiles(self):
        if self.FILESTATE:
            self.file_column.hide()
            self.files_button.setText(">")
        else:
            self.file_column.show()
            self.files_button.setText("<")
        
        self.FILESTATE = not self.FILESTATE
        QTimer.singleShot(1, self.scaleImage)
        
        
    def toggleModes(self):
        if self.MODESTATE:
            self.mode_column.hide()
            self.modes_button.setText("<")
        else:
            self.mode_column.show()
            self.modes_button.setText(">")
        
        self.MODESTATE = not self.MODESTATE
        QTimer.singleShot(1, self.scaleImage)
        
    
    def scaleImage(self):
        if self.imageLabel.pixmap() != None:
            if self.ACTIVE_MODE == 0:
                pixmap = QPixmap(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH)
            else:
                pixmap = QPixmap(self.CURRENT_FILE.images[self.ACTIVE_MODE])
            scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imageLabel.setPixmap(scaled_pixmap)
    
    
    def collapse(self):
        self.COLOR_RED.hide()
        self.COLOR_GREEN.hide()
        self.COLOR_BLUE.hide()
        
        self.ELA_QUALITY_GROUPBOX.hide()
        self.ELA_OFFSET_GROUPBOX.hide()
        
        self.NOA_CONTENT.hide()
        
        self.CLONE_RADIO_GROUPBOX.hide()
        self.CLONE_AUTO_GROUPBOX.hide()
        self.CLONE_DETECTING_GROUPBOX.hide()
    
    
    # ----- BUTTON HANDLING FUNCTIONS
    
    def noneClicked(self):
        self.ACTIVE_MODE = 0
        self.collapse()
        
        self.scaleImage()
    
    
    def colorClicked(self):
        self.ACTIVE_MODE = 1
        self.collapse()
        self.COLOR_RED.show()
        self.COLOR_GREEN.show()
        self.COLOR_BLUE.show()
        
        self.scaleImage()
        
        
    def elaClicked(self):
        self.ACTIVE_MODE = 2
        self.collapse()
        self.ELA_QUALITY_GROUPBOX.show()
        self.ELA_OFFSET_GROUPBOX.show()
        
        self.scaleImage()


    def noaClicked(self):
        self.ACTIVE_MODE = 3
        self.collapse()
        self.NOA_CONTENT.show()
        
        self.scaleImage()


    def cloneClicked(self):
        self.ACTIVE_MODE = 4
        self.CLONE_OPTION = 0
        self.CLONE_RADIO_AUTO.toggle()
        self.collapse()
        
        self.CLONE_RADIO_GROUPBOX.show()
        self.CLONE_AUTO_GROUPBOX.show()
        
        self.scaleImage()
        
        
    def cloneRadioButtonToggled(self):
        if self.CLONE_RADIO_AUTO.isChecked():
            self.CLONE_OPTION = 0
            self.ACTIVE_MODE = 4
        else:
            self.CLONE_OPTION = 1
            self.ACTIVE_MODE = 5
        if self.CURRENT_FILE != None:
            self.scaleImage()
            

    # ----- Image processing
    
    def buildImages(self):
        self.BUTTONS = [self.COLOR_BUTTON, self.ELA_BUTTON, self.NOA_BUTTON, self.CLONE_BUTTON, self.CLONE_RADIO_DETECTING]
        
        for button in self.BUTTONS:
            button.setEnabled(False)
        
        
        self.CLR_WORKER = ColorWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 100, 100, 100, self.CURRENT_FILE.images[1])
        self.ELA_WORKER = ELAWorker(
                        self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                        self.CURRENT_FILE.images[2], 
                        q=self.ELA_SLIDER.value(), 
                        offset_x=self.ELA_OFFSET_SLIDER_X.value(), 
                        offset_y=self.ELA_OFFSET_SLIDER_Y.value()
                        )
        
        self.NOA_WORKER = NoiseWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[3], 
                    self.NOA_SLIDER_FILTER_INTENSITY.value(), 
                    self.NOA_SLIDER_FILTER_BRIGHTNESS.value(),
                    useMedian=self.NOA_USEMEDIAN.isChecked(),
                    subtractEdges=self.NOA_SUBTRACTEDGES.isChecked()
                    )
        
        selected = 0
        for index, option in enumerate(self.CLONE_AUTO_HASH_ALGO_RADIO):
                    if option.isChecked():
                        selected = index
                        break
                    
        self.CLONE_AUTO_WORKER = blockCompareWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[4], 
            self.CLONE_AUTO_SLIDER_BLOCKSIZE.value(), 
            min_detail=self.CLONE_AUTO_SLIDER_DETAIL.value(), 
            min_similar=self.CLONE_AUTO_SLIDER_SIMILAR.value(), 
            hash_mode=selected)
        
        self.CLONE_DETECTING_WORKER = detectingSIFTWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, self.CURRENT_FILE.images[5])
        
        
        self.WORKERS = [self.CLR_WORKER, self.ELA_WORKER, self.NOA_WORKER, self.CLONE_AUTO_WORKER, self.CLONE_DETECTING_WORKER]
        
        for i in range(len(self.WORKERS)):
            self.WORKERS[i].finished.connect(lambda i=i: self.enableButton(self.BUTTONS[i]))
            self.WORKERS[i].start()
            
    
    def isSomethingRunning(self):
        for worker in self.WORKERS:
            if worker.isRunning():
                return True
        return False
        
         
    def enableButton(self, button):
        button.setEnabled(True)
        
    
    # --- Updating functions for option changes

    def updateColor(self):
        if self.CURRENT_FILE != None:
            if self.CLR_WORKER.isRunning():
                pass
            else:
                r = self.RED_SLIDER.value()
                g = self.GREEN_SLIDER.value()
                b = self.BLUE_SLIDER.value()
                
                self.CLR_WORKER = ColorWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, r, g, b, self.CURRENT_FILE.images[1])
                self.CLR_WORKER.finished.connect(self.scaleImage)
                self.CLR_WORKER.start()
                
    
    def updateEla(self):
        self.SLIDER_IS_PRESSED = False
        if self.CURRENT_FILE != None:
            if self.ELA_WORKER.isRunning():
                QTimer.singleShot(500, self.updateEla)
                pass
            else:
                self.ELA_SLIDER_IS_PRESSED = False
                if self.CURRENT_FILE != None:
                    
                    self.ELA_WORKER = ELAWorker(
                        self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                        self.CURRENT_FILE.images[2], 
                        q=self.ELA_SLIDER.value(), 
                        offset_x=self.ELA_OFFSET_SLIDER_X.value(), 
                        offset_y=self.ELA_OFFSET_SLIDER_Y.value()
                        )
                    
                    self.ELA_WORKER.finished.connect(self.scaleImage)
                    self.ELA_WORKER.start()
    
           
    def updateNoa(self):
        if self.CURRENT_FILE != None:
            if self.NOA_WORKER.isRunning():
                QTimer.singleShot(500, self.updateNoa)
            else:
                
                self.NOA_WORKER = NoiseWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[3], 
                    self.NOA_SLIDER_FILTER_INTENSITY.value(), 
                    self.NOA_SLIDER_FILTER_BRIGHTNESS.value(),
                    useMedian=self.NOA_USEMEDIAN.isChecked(),
                    subtractEdges=self.NOA_SUBTRACTEDGES.isChecked()
                    )
                
                self.NOA_WORKER.finished.connect(self.scaleImage)
                self.NOA_WORKER.start()
                
    def updateClone(self):
        if self.CURRENT_FILE != None:
            if self.CLONE_AUTO_WORKER.isRunning() or self.CLONE_DETECTING_WORKER.isRunning():
                QTimer.singleShot(500, self.updateClone)
            else:
                selected = 0
                for index, option in enumerate(self.CLONE_AUTO_HASH_ALGO_RADIO):
                    if option.isChecked():
                        selected = index
                        break
                    
                self.CLONE_AUTO_WORKER = blockCompareWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[4], 
                    self.CLONE_AUTO_SLIDER_BLOCKSIZE.value(), 
                    min_detail=self.CLONE_AUTO_SLIDER_DETAIL.value(), 
                    min_similar=self.CLONE_AUTO_SLIDER_SIMILAR.value(), 
                    hash_mode=selected
                    )
                
                self.CLONE_AUTO_WORKER.finished.connect(self.scaleImage)
                self.CLONE_AUTO_WORKER.start()
    
    
def main():
    app = QApplication(sys.argv)
    window = Imestigator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()