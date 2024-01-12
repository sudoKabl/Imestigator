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
from app.autoSIFT import autoSIFTWorker
from app.detectingSIFT import detectingSIFTWorker

class Imestigator(QMainWindow):
    FILESTATE = True
    MODESTATE = True
    ACTIVE_MODE = 0
    
    CURRENT_FILE = None
    
    SIFT_OPTION = 0
    
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
        
        def filterTree():
            search_text = search_field.text()
            if QDir(search_text).exists():
                self.tree.setRootIndex(model.setRootPath(search_text))
            else:
                self.tree.setRootIndex(model.index(QDir.rootPath()))
                model.setNameFilters([f'*{search_text}*'])
        
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
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tree.setWindowTitle("Search for Files")
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h_scrollbar = self.tree.horizontalScrollBar()
        h_scrollbar.valueChanged.connect(lambda value: self.debugScrollbar(h_scrollbar))
        
        for column in range(1, model.columnCount()):
            self.tree.hideColumn(column)
            
        def openImage(index):
            print(self.isSomethingRunning())
            path = model.filePath(index)
            if self.CURRENT_FILE != None and self.CURRENT_FILE.ORIGINAL_IMAGE_PATH != path:
                self.CURRENT_FILE.cleanup()
                
            if QFileInfo(path).isFile():
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
        
        def noaClick():
            if self.SLIDER_IS_PRESSED == False:
                self.updateNoa()
        
        self.NOA_INTENSITY_GROUPBOX = QGroupBox()
        noa_l = QVBoxLayout()
        self.NOA_SLIDER_FILTER_INTENSITY = self.hSlider(3, 3, 15)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_INTENSITY.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_INTENSITY.sliderPressed.connect(sliderDisabler)
        
        self.NOA_BRIGHTNESS_GROUPBOX = QGroupBox()
        noa_b = QVBoxLayout()
        self.NOA_SLIDER_FILTER_BRIGHTNESS = self.hSlider(100, 1, 500)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderReleased.connect(self.updateNoa)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.valueChanged.connect(noaClick)
        self.NOA_SLIDER_FILTER_BRIGHTNESS.sliderPressed.connect(sliderDisabler)
        
        noa_l.addWidget(self.NOA_SLIDER_FILTER_INTENSITY)
        noa_l.addLayout(self.hSliderLabels(self.NOA_SLIDER_FILTER_INTENSITY))
        
        noa_b.addWidget(self.NOA_SLIDER_FILTER_BRIGHTNESS)
        noa_b.addLayout(self.hSliderLabels(self.NOA_SLIDER_FILTER_BRIGHTNESS))
        
        self.NOA_INTENSITY_GROUPBOX.setLayout(noa_l)
        self.NOA_INTENSITY_GROUPBOX.setTitle("Filter intensity")
        self.NOA_INTENSITY_GROUPBOX.hide()
        
        self.NOA_BRIGHTNESS_GROUPBOX.setLayout(noa_b)
        self.NOA_BRIGHTNESS_GROUPBOX.setTitle("Brightness")
        self.NOA_BRIGHTNESS_GROUPBOX.hide()
        
        # ----- SIFT clone detection
        
        self.SIFT_BUTTON = QPushButton("SIFT Clone Detection")
        self.SIFT_BUTTON.clicked.connect(self.siftClicked)
        
        self.SIFT_RADIO_AUTO = QRadioButton("Frames")
        self.SIFT_RADIO_AUTO.toggled.connect(self.radioButtonToggled)
        self.SIFT_RADIO_AUTO.toggle()
        
        self.SIFT_RADIO_DETECTING = QRadioButton("Object detection")
        self.SIFT_RADIO_DETECTING.toggled.connect(self.radioButtonToggled)
        self.SIFT_RADIO_DETECTING.setEnabled(False)
        
        sift_radiobuttons = QVBoxLayout()
        sift_radiobuttons.addWidget(self.SIFT_RADIO_AUTO)
        sift_radiobuttons.addWidget(self.SIFT_RADIO_DETECTING)
        
        self.SIFT_RADIO_GROUPBOX = QGroupBox()
        self.SIFT_RADIO_GROUPBOX.setLayout(sift_radiobuttons)
        self.SIFT_RADIO_GROUPBOX.setTitle("Comparison options")
        self.SIFT_RADIO_GROUPBOX.hide()
        
        self.SIFT_AUTO_GROUPBOX = QGroupBox()
        self.SIFT_DETECTING_GROUPBOX = QGroupBox()
        
        self.SIFT_AUTO_GROUPBOX.setTitle("Options")
        self.SIFT_DETECTING_GROUPBOX.setTitle("Options")
        
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
        layout.addWidget(self.NOA_INTENSITY_GROUPBOX)
        layout.addWidget(self.NOA_BRIGHTNESS_GROUPBOX)
        
        layout.addWidget(self.makeLine())
        
        layout.addWidget(self.SIFT_BUTTON)
        layout.addWidget(self.SIFT_RADIO_GROUPBOX)
        
        
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
        
        self.NOA_INTENSITY_GROUPBOX.hide()
        self.NOA_BRIGHTNESS_GROUPBOX.hide()
        
        self.SIFT_RADIO_GROUPBOX.hide()
        self.SIFT_AUTO_GROUPBOX.hide()
        self.SIFT_DETECTING_GROUPBOX.hide()
    
    
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
        self.NOA_INTENSITY_GROUPBOX.show()
        self.NOA_BRIGHTNESS_GROUPBOX.show()
        
        self.scaleImage()


    def siftClicked(self):
        self.ACTIVE_MODE = 4
        self.SIFT_OPTION = 0
        self.SIFT_RADIO_AUTO.toggle()
        self.collapse()
        
        self.SIFT_RADIO_GROUPBOX.show()
        
        self.scaleImage()
        
        
    def radioButtonToggled(self):
        if self.SIFT_RADIO_AUTO.isChecked():
            self.SIFT_OPTION = 0
            self.ACTIVE_MODE = 4
        else:
            self.SIFT_OPTION = 1
            self.ACTIVE_MODE = 5
        if self.CURRENT_FILE != None:
            self.scaleImage()

    # ----- Image processing
    
    def buildImages(self):
        self.BUTTONS = [self.COLOR_BUTTON, self.ELA_BUTTON, self.NOA_BUTTON, self.SIFT_BUTTON, self.SIFT_RADIO_DETECTING]
        
        for button in self.BUTTONS:
            button.setEnabled(False)
        
        
        self.CLR_WORKER = ColorWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 100, 100, 100, self.CURRENT_FILE.images[1])
        self.ELA_WORKER = ELAWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, 90, self.CURRENT_FILE.images[2], 0, 0)
        self.NOA_WORKER = NoiseWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, self.CURRENT_FILE.images[3], 3, 100)
        self.AUTO_SIFT_WORKER = autoSIFTWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, self.CURRENT_FILE.images[4])
        self.DETECTING_SIFT_WORKER = detectingSIFTWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, self.CURRENT_FILE.images[5])
        
        
        self.WORKERS = [self.CLR_WORKER, self.ELA_WORKER, self.NOA_WORKER, self.AUTO_SIFT_WORKER, self.DETECTING_SIFT_WORKER]
        
        for i in range(len(self.WORKERS)):
            print(i)
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
                    value = self.ELA_SLIDER.value()
                    x = self.ELA_OFFSET_SLIDER_X.value()
                    y = self.ELA_OFFSET_SLIDER_Y.value()
                    self.ELA_WORKER = ELAWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, value, self.CURRENT_FILE.images[2], x, y)
                    self.ELA_WORKER.finished.connect(self.scaleImage)
                    self.ELA_WORKER.start()
    
           
    def updateNoa(self):
        if self.CURRENT_FILE != None:
            if self.NOA_WORKER.isRunning():
                QTimer.singleShot(500, self.updateNoa())
            else:
                self.NOA_WORKER = NoiseWorker(self.CURRENT_FILE.ORIGINAL_IMAGE_PATH, self.CURRENT_FILE.images[3], self.NOA_SLIDER_FILTER_INTENSITY.value(), self.NOA_SLIDER_FILTER_BRIGHTNESS.value())
                self.NOA_WORKER.finished.connect(self.scaleImage)
                self.NOA_WORKER.start()
    
    
def main():
    app = QApplication(sys.argv)
    window = Imestigator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()