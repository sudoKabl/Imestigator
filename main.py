from PyQt5.QtGui import QContextMenuEvent, QMouseEvent, QResizeEvent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

from app.ImageDataHolder import ImageData

from app.color import ColorWorker
from app.custom import CustomWorker
from app.ela import ELAWorker
from app.noise import NoiseWorker
from app.blockCompare import blockCompareWorker
from app.detectingSIFT import detectingSIFTWorker
from app.aiCloneDetection import aiCloneWorker

from ui.DragCheckboxes import DragCheckbox
from ui.DragCheckboxes import DragGroubox
        
        
# -------------------- MAIN CLASS ------------------------------------------------------------
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
        
        self.setGeometry(width // 4, height // 4, width // 2, height // 2)
        
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
        search_field.setText(r"C:\Users\Kapsr\Pictures\test_image_folder")
        
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
    
    # --- Function for creating individual method buttons, just so its a little more readable
    
    def createNoFilter(self):
        self.NONE_BUTTON = QPushButton("None")
        self.NONE_BUTTON.setToolTip("View original image")
        self.NONE_BUTTON.clicked.connect(self.noneClicked)
        
    def createColorCorrection(self):
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
        
    def createCustomFilter(self):
        self.CUSTOM_BUTTON = QPushButton("Custom Filters")
        self.CUSTOM_BUTTON.setToolTip("Apply own, custom filters to image")
        self.CUSTOM_BUTTON.clicked.connect(self.customFilterClicked)
        
        
        self.listOfFilters = QGroupBox("Available Filters")
        listOfFiltersLayout = QVBoxLayout()
        
        buttons = ["Grayscale", "Equalize Histogram", 
                   "Gaussian Blur", "Median Filter", 
                   "Threshold", "Adaptive Threshold", 
                   "Sobel X", "Sobel Y", "Laplacian Edge", "Canny Edge", 
                   "Erosion", "Dilation", "Top Hat", "Black Hat",
                   "ELA", "Noise Analysis",
                   "Brightness and Contrast"]

        
        self.listOfFilters.setLayout(listOfFiltersLayout)
        
        self.filterContainer = QScrollArea(self)
        self.filterContainer.setWidgetResizable(True)
        self.filterContainer.setMaximumHeight(450)
        
        self.filters = DragGroubox("Active Filters")

        self.filters.elementMoved.connect(self.updateCustom)
        
        
        def addFilter(name):
            newBox = DragCheckbox(name)
            newBox.setChecked(True)
            
            self.filters.addCheckbox(newBox)
            
            newBox.clicked.connect(lambda: self.updateCustom())
            
            self.updateCustom()

        for button in buttons:
            pushButton = QPushButton(button)
            listOfFiltersLayout.addWidget(pushButton)
            pushButton.clicked.connect(lambda checked, b=button: addFilter(b))
            
        self.CUSTOM_RESET = QPushButton("Reset Filters")
        self.CUSTOM_RESET.clicked.connect(self.filters.reset)
        self.CUSTOM_RESET.clicked.connect(self.updateCustom)
        
        self.filters.setLayout(self.filters.layoutSaver)
        

        self.listOfFilters.hide()
        
        self.filterContainer.setWidget(self.filters)
        self.filterContainer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.filters.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        self.filterContainer.hide()
        
        
        self.CUSTOM_RESET.hide()
        
        

    def createELA(self):
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
        
        
        
        self.ELA_SLIDER.sliderPressed.connect(self.sliderDisabler)
        
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
        self.ELA_OFFSET_SLIDER_X.sliderPressed.connect(self.sliderDisabler)
        
        label_y = QLabel("Y-Axis")
        
        self.ELA_OFFSET_SLIDER_Y = self.hSlider(0, 0, 7)
        self.ELA_OFFSET_SLIDER_Y.sliderReleased.connect(self.updateEla)
        self.ELA_OFFSET_SLIDER_Y.valueChanged.connect(elaClick)
        self.ELA_OFFSET_SLIDER_Y.sliderPressed.connect(self.sliderDisabler)
        
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
        
        
    def createNoise(self):
        self.NOA_BUTTON = QPushButton("Noise Analysis")
        self.NOA_BUTTON.setToolTip("Perform general noise analysis")
        self.NOA_BUTTON.clicked.connect(self.noaClicked)
        
        self.NOA_CONTENT = QWidget()
        noa_content_layout = QVBoxLayout()
        
        self.NOA_USESHARP = QCheckBox("Use sharpening")
        self.NOA_USESHARP.clicked.connect(self.updateNoa)
        self.NOA_SUBTRACTEDGES = QCheckBox("Edge reduction")
        self.NOA_SUBTRACTEDGES.clicked.connect(self.updateNoa)
        
        noa_content_layout.addWidget(self.NOA_USESHARP)
        noa_content_layout.addWidget(self.NOA_SUBTRACTEDGES)
        
        def noaClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateNoa()
        
        noa_i_gb = QGroupBox()
        noa_l = QVBoxLayout()
        self.NOA_SLIDER_FILTER_INTENSITY = self.hSlider(3, 3, 15)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_INTENSITY.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderPressed.connect(self.sliderDisabler)
        
        noa_b_gb = QGroupBox()
        noa_b = QVBoxLayout()
        self.NOA_SLIDER_FILTER_BRIGHTNESS = self.hSlider(300, 1, 500)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderPressed.connect(self.sliderDisabler)
        
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
        
        
    def createSimpleCloneDetection(self):
        self.SIMPLE_CLONE_BUTTON = QPushButton("Clone Detection (simple)")
        self.SIMPLE_CLONE_BUTTON.setToolTip("Apply simple clone detection to image")
        self.SIMPLE_CLONE_BUTTON.clicked.connect(self.simpleCloneClicked)
        
        self.SIMPLE_CLONE_GROUPBOX = QGroupBox()
        
        self.SIMPLE_CLONE_GROUPBOX.setTitle("Options")
        
        def cloneClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateSimpleClone()
        
        simple_layout = QVBoxLayout()
        
        blocksize_label = QLabel("Block size")
        
        self.SIMPLE_CLONE_SLIDER_BLOCKSIZE = self.hSlider(16, 4, 64)
        self.SIMPLE_CLONE_SLIDER_BLOCKSIZE.sliderReleased.connect(self.updateSimpleClone)
        self.SIMPLE_CLONE_SLIDER_BLOCKSIZE.valueChanged.connect(cloneClick)
        self.SIMPLE_CLONE_SLIDER_BLOCKSIZE.sliderPressed.connect(self.sliderDisabler)
        
        min_detail_label = QLabel("Minimum detail level")
        
        self.SIMPLE_CLONE_SLIDER_DETAIL = self.hSlider(14, 1, 50)
        self.SIMPLE_CLONE_SLIDER_DETAIL.sliderReleased.connect(self.updateSimpleClone)
        self.SIMPLE_CLONE_SLIDER_DETAIL.valueChanged.connect(cloneClick)
        self.SIMPLE_CLONE_SLIDER_DETAIL.sliderPressed.connect(self.sliderDisabler)
        
        min_similar_pHash_label = QLabel("pHash Threshold")
        
        self.SIMPLE_CLONE_SLIDER_SIMILAR_P = self.hSlider(20, 10, 40)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_P.sliderReleased.connect(self.updateSimpleClone)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_P.valueChanged.connect(cloneClick)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_P.sliderPressed.connect(self.sliderDisabler)
        
        min_similar_aHash_label = QLabel("aHash Threshold")
        
        self.SIMPLE_CLONE_SLIDER_SIMILAR_A = self.hSlider(7, 1, 25)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_A.sliderReleased.connect(self.updateSimpleClone)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_A.valueChanged.connect(cloneClick)
        self.SIMPLE_CLONE_SLIDER_SIMILAR_A.sliderPressed.connect(self.sliderDisabler)
        
        simple_layout.addWidget(blocksize_label)
        simple_layout.addWidget(self.SIMPLE_CLONE_SLIDER_BLOCKSIZE)
        simple_layout.addLayout(self.hSliderLabels(self.SIMPLE_CLONE_SLIDER_BLOCKSIZE))
        
        simple_layout.addWidget(min_detail_label)
        simple_layout.addWidget(self.SIMPLE_CLONE_SLIDER_DETAIL)
        simple_layout.addLayout(self.hSliderLabels(self.SIMPLE_CLONE_SLIDER_DETAIL))
        
        simple_layout.addWidget(min_similar_pHash_label)
        simple_layout.addWidget(self.SIMPLE_CLONE_SLIDER_SIMILAR_P)
        simple_layout.addLayout(self.hSliderLabels(self.SIMPLE_CLONE_SLIDER_SIMILAR_P))
        
        simple_layout.addWidget(min_similar_aHash_label)
        simple_layout.addWidget(self.SIMPLE_CLONE_SLIDER_SIMILAR_A)
        simple_layout.addLayout(self.hSliderLabels(self.SIMPLE_CLONE_SLIDER_SIMILAR_A))
        
        
        self.SIMPLE_CLONE_GROUPBOX.setLayout(simple_layout)
        self.SIMPLE_CLONE_GROUPBOX.hide()
        
        
    def createAdvancedCloneDetection(self):
        self.ADVANCED_CLONE_BUTTON = QPushButton("Clone Detection (advanced)")
        self.ADVANCED_CLONE_BUTTON.setToolTip("Apply advanced clone detection to image")
        self.ADVANCED_CLONE_BUTTON.clicked.connect(self.advancedCloneClicked)
        
        self.ADVANCED_CLONE_GROUPBOX = QGroupBox()
        
        self.ADVANCED_CLONE_GROUPBOX.setTitle("Options")
        
        def cloneClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateAdvancedClone()
        
        advanced_layout = QVBoxLayout()
        
        bluramount_label = QLabel("Blur amount")
        
        self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT = self.hSlider(3, 1, 10)
        self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT.sliderReleased.connect(self.updateAdvancedClone)
        self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT.valueChanged.connect(cloneClick)
        self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT.sliderPressed.connect(self.sliderDisabler)
        
        blursize_label = QLabel("Blur Size")
        
        self.ADVANCED_CLONE_SLIDER_BLUR_SIZE = self.hSlider(5, 1, 12)
        self.ADVANCED_CLONE_SLIDER_BLUR_SIZE.sliderReleased.connect(self.updateAdvancedClone)
        self.ADVANCED_CLONE_SLIDER_BLUR_SIZE.valueChanged.connect(cloneClick)
        self.ADVANCED_CLONE_SLIDER_BLUR_SIZE.sliderPressed.connect(self.sliderDisabler)
        
        adaptive_size_label = QLabel("Threshold Block size")
        
        self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE = self.hSlider(10, 5, 30)
        self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE.sliderReleased.connect(self.updateAdvancedClone)
        self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE.valueChanged.connect(cloneClick)
        self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE.sliderPressed.connect(self.sliderDisabler)
        
        min_similar_label = QLabel("Minimum similiarity")
        
        self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR = self.hSlider(5, 1, 10)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR.sliderReleased.connect(self.updateAdvancedClone)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR.valueChanged.connect(cloneClick)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR.sliderPressed.connect(self.sliderDisabler)
        
        min_matches_label = QLabel("Minimum matches")
        
        self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH = self.hSlider(8, 1, 16)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH.sliderReleased.connect(self.updateAdvancedClone)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH.valueChanged.connect(cloneClick)
        self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH.sliderPressed.connect(self.sliderDisabler)
        
        advanced_layout.addWidget(bluramount_label)
        advanced_layout.addWidget(self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT)
        advanced_layout.addLayout(self.hSliderLabels(self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT))
        
        advanced_layout.addWidget(blursize_label)
        advanced_layout.addWidget(self.ADVANCED_CLONE_SLIDER_BLUR_SIZE)
        advanced_layout.addLayout(self.hSliderLabels(self.ADVANCED_CLONE_SLIDER_BLUR_SIZE))
        
        advanced_layout.addWidget(adaptive_size_label)
        advanced_layout.addWidget(self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE)
        advanced_layout.addLayout(self.hSliderLabels(self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE))
        
        advanced_layout.addWidget(min_similar_label)
        advanced_layout.addWidget(self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR)
        advanced_layout.addLayout(self.hSliderLabels(self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR))
        
        advanced_layout.addWidget(min_matches_label)
        advanced_layout.addWidget(self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH)
        advanced_layout.addLayout(self.hSliderLabels(self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH))
        
        self.ADVANCED_CLONE_GROUPBOX.setLayout(advanced_layout)
        self.ADVANCED_CLONE_GROUPBOX.hide()
        
        
    def createAICloneDetection(self):
        self.AI_CLONE_BUTTON = QPushButton("Clone Detection (AI)")
        self.AI_CLONE_BUTTON.setToolTip("Apply AI clone detection to image")
        self.AI_CLONE_BUTTON.clicked.connect(self.aiCloneClicked)
        
        self.AI_CLONE_GROUPBOX = QGroupBox()
        
        self.AI_CLONE_GROUPBOX.setTitle("Options")
        
        def cloneClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateAIClone()
        
        ai_layout = QVBoxLayout()
        
        min_matches_label = QLabel("Minimum matches")
        
        self.AI_CLONE_MINMATCH_SLIDER = self.hSlider(8, 1, 25)
        self.AI_CLONE_MINMATCH_SLIDER.sliderReleased.connect(self.updateAIClone)
        self.AI_CLONE_MINMATCH_SLIDER.valueChanged.connect(cloneClick)
        self.AI_CLONE_MINMATCH_SLIDER.sliderPressed.connect(self.sliderDisabler)
        
        min_similar_label = QLabel("Minimum similiarity")
        
        self.AI_CLONE_SLIDER_MINIMAL_SIMILAR = self.hSlider(5, 1, 10)
        self.AI_CLONE_SLIDER_MINIMAL_SIMILAR.sliderReleased.connect(self.updateAIClone)
        self.AI_CLONE_SLIDER_MINIMAL_SIMILAR.valueChanged.connect(cloneClick)
        self.AI_CLONE_SLIDER_MINIMAL_SIMILAR.sliderPressed.connect(self.sliderDisabler)
        
        ai_layout.addWidget(min_matches_label)
        ai_layout.addWidget(self.AI_CLONE_MINMATCH_SLIDER)
        ai_layout.addLayout(self.hSliderLabels(self.AI_CLONE_MINMATCH_SLIDER))
        
        ai_layout.addWidget(min_similar_label)
        ai_layout.addWidget(self.AI_CLONE_SLIDER_MINIMAL_SIMILAR)
        ai_layout.addLayout(self.hSliderLabels(self.AI_CLONE_SLIDER_MINIMAL_SIMILAR))
        
        self.AI_CLONE_GROUPBOX.setLayout(ai_layout)
        self.AI_CLONE_GROUPBOX.hide()
    
    
    def createMetadata(self):
        self.METADATA_BUTTON = QPushButton("View Metadata")
        self.METADATA_BUTTON.setToolTip("View original image")
        self.METADATA_BUTTON.clicked.connect(self.metadataClicked)
    
    def initModesColumn(self):
        layout = QVBoxLayout()
        
        # ----- No filter
        self.createNoFilter()
        
        # ----- Color correction
        self.createColorCorrection()
        
        # ----- Custom Filters
        self.createCustomFilter()
        
        # ----- Error level analysis
        self.createELA()
        
        # ----- Noise analysis
        self.createNoise()
        
        # ----- Clone detection
        self.createSimpleCloneDetection()
 
        self.createAdvancedCloneDetection()
  
        self.createAICloneDetection()
        
        # ----- Metadata
        self.createMetadata()
        
        
        # ----- Add all the elements to column
        
        
        layout.addWidget(self.NONE_BUTTON)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.COLOR_BUTTON)
        layout.addWidget(self.COLOR_RED)
        layout.addWidget(self.COLOR_GREEN)
        layout.addWidget(self.COLOR_BLUE)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.CUSTOM_BUTTON)
        layout.addWidget(self.listOfFilters)
        layout.addWidget(self.filterContainer)
        layout.addWidget(self.CUSTOM_RESET)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.ELA_BUTTON)
        layout.addWidget(self.ELA_QUALITY_GROUPBOX)
        layout.addWidget(self.ELA_OFFSET_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.NOA_BUTTON)
        layout.addWidget(self.NOA_CONTENT)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.SIMPLE_CLONE_BUTTON)
        layout.addWidget(self.SIMPLE_CLONE_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.ADVANCED_CLONE_BUTTON)
        layout.addWidget(self.ADVANCED_CLONE_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.AI_CLONE_BUTTON)
        layout.addWidget(self.AI_CLONE_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.METADATA_BUTTON)
        
        
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
    
    
    def sliderDisabler(self):
        self.SLIDER_IS_PRESSED = True
    
    
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
        
        self.listOfFilters.hide()
        self.filterContainer.hide()
        self.CUSTOM_RESET.hide()
        
        self.ELA_QUALITY_GROUPBOX.hide()
        self.ELA_OFFSET_GROUPBOX.hide()
        
        self.NOA_CONTENT.hide()
        
        self.SIMPLE_CLONE_GROUPBOX.hide()
        self.ADVANCED_CLONE_GROUPBOX.hide()
        self.AI_CLONE_GROUPBOX.hide()
    
    
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
    
    
    def customFilterClicked(self):
        self.ACTIVE_MODE = 2
        self.collapse()
        
        self.listOfFilters.show()
        self.filterContainer.show()
        self.CUSTOM_RESET.show()
        
        self.scaleImage()
        
        
    def elaClicked(self):
        self.ACTIVE_MODE = 3
        self.collapse()
        self.ELA_QUALITY_GROUPBOX.show()
        self.ELA_OFFSET_GROUPBOX.show()
        
        self.scaleImage()


    def noaClicked(self):
        self.ACTIVE_MODE = 4
        self.collapse()
        self.NOA_CONTENT.show()
        
        self.scaleImage()


    def simpleCloneClicked(self):
        self.ACTIVE_MODE = 5
        self.collapse()
        
        self.SIMPLE_CLONE_GROUPBOX.show()
        
        self.scaleImage()
        
        
    def advancedCloneClicked(self):
        self.ACTIVE_MODE = 6
        self.collapse()
        
        self.ADVANCED_CLONE_GROUPBOX.show()
        
        self.scaleImage()
        
        
    def aiCloneClicked(self):
        self.ACTIVE_MODE = 7
        self.collapse()
        
        self.AI_CLONE_GROUPBOX.show()
        
        self.scaleImage()
    
    
    def metadataClicked(self):
        metalist = self.CURRENT_FILE.metadata()
        
        #print(metalist)
        
        self.dialog = TableDialog(metalist)
        self.dialog.show()


    # ----- Image processing
    
    def buildImages(self):
        self.BUTTONS = [self.COLOR_BUTTON, self.CUSTOM_BUTTON, self.ELA_BUTTON, self.NOA_BUTTON, self.SIMPLE_CLONE_BUTTON, self.ADVANCED_CLONE_BUTTON, self.AI_CLONE_BUTTON]
        
        for button in self.BUTTONS:
            button.setEnabled(False)
        
        
        self.CLR_WORKER = ColorWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 100, 100, 100, self.CURRENT_FILE.images[1])
        
        self.CUSTOM_WORKER = CustomWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[2], 
            filters=[]
        )
        
        
        self.ELA_WORKER = ELAWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[3], 
            q=self.ELA_SLIDER.value(), 
            offset_x=self.ELA_OFFSET_SLIDER_X.value(), 
            offset_y=self.ELA_OFFSET_SLIDER_Y.value()
            )
        
        
        self.NOA_WORKER = NoiseWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[4], 
            self.NOA_SLIDER_FILTER_INTENSITY.value(), 
            self.NOA_SLIDER_FILTER_BRIGHTNESS.value(),
            useSharp=self.NOA_USESHARP.isChecked(),
            subtractEdges=self.NOA_SUBTRACTEDGES.isChecked()
            )
                    
        self.SIMPLE_CLONE_WORKER = blockCompareWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[5], 
            block_size=self.SIMPLE_CLONE_SLIDER_BLOCKSIZE.value(), 
            min_detail=self.SIMPLE_CLONE_SLIDER_DETAIL.value(), 
            aHash_thresh=self.SIMPLE_CLONE_SLIDER_SIMILAR_A.value(), 
            pHash_thresh=self.SIMPLE_CLONE_SLIDER_SIMILAR_P.value()
            )
        
        self.ADVANCED_CLONE_WORKER = detectingSIFTWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[6],
            blur = self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT.value(),
            blur_size = self.ADVANCED_CLONE_SLIDER_BLUR_SIZE.value(),
            adaThre = self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE.value(),
            min_similar=self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR.value(),
            min_matches=self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH.value()
        )

        self.AI_CLONE_WORKER = aiCloneWorker(
            self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
            self.CURRENT_FILE.images[7],
            minMatches=self.AI_CLONE_MINMATCH_SLIDER.value(),
            minSimilar=self.AI_CLONE_SLIDER_MINIMAL_SIMILAR.value()
        )
        
        self.WORKERS = [self.CLR_WORKER, self.CUSTOM_WORKER, self.ELA_WORKER, self.NOA_WORKER, self.SIMPLE_CLONE_WORKER, self.ADVANCED_CLONE_WORKER, self.AI_CLONE_WORKER]
        
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
    
    
    def updateCustom(self):
        if self.CURRENT_FILE != None:
            if self.CUSTOM_WORKER.isRunning():
                pass
            else:
                filters = []
                
                for n in range(self.filters.layoutSaver.count()):
                    w = self.filters.layoutSaver.itemAt(n).widget()
                    if w.isChecked():
                        optarr = w.getOptions()
                        opt = []
                        
                        for el in optarr:
                            opt.append(el[2])
                        
                        filters.append((w.text(), opt))
                
                self.CUSTOM_WORKER = CustomWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[2], 
                    filters=filters
                    )
                self.CUSTOM_WORKER.finished.connect(self.scaleImage)
                self.CUSTOM_WORKER.start()
        
    
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
                        self.CURRENT_FILE.images[3], 
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
                    self.CURRENT_FILE.images[4], 
                    self.NOA_SLIDER_FILTER_INTENSITY.value(), 
                    self.NOA_SLIDER_FILTER_BRIGHTNESS.value(),
                    useSharp=self.NOA_USESHARP.isChecked(),
                    subtractEdges=self.NOA_SUBTRACTEDGES.isChecked()
                    )
                
                self.NOA_WORKER.finished.connect(self.scaleImage)
                self.NOA_WORKER.start()
                
    def updateSimpleClone(self):
        if self.CURRENT_FILE != None:
            if self.SIMPLE_CLONE_WORKER.isRunning():
                QTimer.singleShot(500, self.updateSimpleClone)
            else:        
                self.SIMPLE_CLONE_WORKER = blockCompareWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[5], 
                    self.SIMPLE_CLONE_SLIDER_BLOCKSIZE.value(), 
                    min_detail=self.SIMPLE_CLONE_SLIDER_DETAIL.value(), 
                    aHash_thresh=self.SIMPLE_CLONE_SLIDER_SIMILAR_A.value(), 
                    pHash_thresh=self.SIMPLE_CLONE_SLIDER_SIMILAR_P.value()
                    )
                
                self.SIMPLE_CLONE_WORKER.finished.connect(self.scaleImage)
                self.SIMPLE_CLONE_WORKER.start()
    
    def updateAdvancedClone(self):
        if self.CURRENT_FILE != None:
            if self.ADVANCED_CLONE_WORKER.isRunning():
                QTimer.singleShot(500, self.updateAdvancedClone)
            else:
                self.ADVANCED_CLONE_WORKER = detectingSIFTWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[6],
                    blur = self.ADVANCED_CLONE_SLIDER_BLUR_AMOUNT.value(),
                    blur_size = self.ADVANCED_CLONE_SLIDER_BLUR_SIZE.value(),
                    adaThre = self.ADVANCED_CLONE_SLIDER_ADAPTIVE_SIZE.value(),
                    min_similar=self.ADVANCED_CLONE_SLIDER_MINIMAL_SIMILAR.value(),
                    min_matches=self.ADVANCED_CLONE_SLIDER_MINIMAL_MATCH.value()
                )
                self.ADVANCED_CLONE_WORKER.finished.connect(self.scaleImage)
                self.ADVANCED_CLONE_WORKER.start()
    
    def updateAIClone(self):
        if self.CURRENT_FILE != None:
            if self.AI_CLONE_WORKER.isRunning():
                QTimer.singleShot(500, self.updateAIClone)
            else:
                self.AI_CLONE_WORKER = aiCloneWorker(
                    self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 
                    self.CURRENT_FILE.images[7],
                    minMatches=self.AI_CLONE_MINMATCH_SLIDER.value(),
                    minSimilar=self.AI_CLONE_SLIDER_MINIMAL_SIMILAR.value()
                )
                self.AI_CLONE_WORKER.finished.connect(self.scaleImage)
                self.AI_CLONE_WORKER.start()



class TableDialog(QDialog):
    def __init__(self, data, parent=None):
        super(TableDialog, self).__init__(parent)
        self.setWindowTitle('Metadata')
        
        desktop = QApplication.desktop().screenGeometry()
        width = desktop.width()
        height = desktop.height()
        
        self.setGeometry(width // 4 + width // 2, height // 4, width // 5, height // 2)
        
        
        layout = QVBoxLayout()
        
        if data[0] == "No data found":
            self.textWidget = QPlainTextEdit()
            self.textWidget.setPlainText("No data found")
            self.textWidget.setDisabled(True)
            layout.addWidget(self.textWidget)
        else:
            self.tableWidget = QTableWidget(len(data), 2)
            self.tableWidget.setHorizontalHeaderLabels(['Tag', 'Value'])

            for row_num, row_data in enumerate(data):
                for col_num, col_data in enumerate(row_data):
                    self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(col_data)))
            layout.addWidget(self.tableWidget)
            
            
        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = Imestigator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()