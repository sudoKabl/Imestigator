from PyQt5.QtGui import QContextMenuEvent, QMouseEvent, QResizeEvent
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math

# ----- For dragable checkboxes in custom filter 

class DragCheckbox(QCheckBox):
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.customOptions = []
        self.menu = QMenu()
        
        self.updateActions()
        
    def getOptions(self):
        return self.customOptions
        
            
    def updateActions(self):
        self.menu.clear()
            
        title = QLabel(self.text() + " options")
        titleAction = QWidgetAction(title)
        titleAction.setDefaultWidget(title)
        self.menu.addAction(titleAction)
        self.customOptions.clear()
        self.customOptions = [("No options", None, 0)]
        
        cType = self.text()
        
        def changeKernelSize():
            num, ok = QInputDialog.getInt(self, "Set size of kernel", f"Current: {self.customOptions[0][2]}")
            if ok:
                num = math.floor(num)
                self.customOptions = [("Kernel size", changeKernelSize, num)]
                
        def adaThreshBlock():
            num, ok = QInputDialog.getInt(self, "Set block size", f"Current: {self.customOptions[0][2]}")
            if ok:
                num = math.floor(num)
                self.customOptions[0] = ("Block size", adaThreshBlock, num)
                
        def adaThreshMax():
            num, ok = QInputDialog.getInt(self, "Set max value", f"Current: {self.customOptions[1][2]}")
            if ok:
                if num > 255:
                    num = 255
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[1] = ("Max value", adaThreshMax, num)
                
        def cannyUpper():
            num, ok = QInputDialog.getInt(self, "Set upper threshold", f"Current: {self.customOptions[0][2]}")
            if ok:
                if num > 255:
                    num = 255
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[0] = ("Upper threshold", cannyUpper, num)
                
        def cannyLower():
            num, ok = QInputDialog.getInt(self, "Set lower threshold", f"Current: {self.customOptions[1][2]}")
            if ok:
                if num > 255:
                    num = 255
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[1] = ("Lower threshold", cannyLower, num)
                
        def ela():
            num, ok = QInputDialog.getInt(self, "Set Q Value", f"Current: {self.customOptions[0][2]}")
            if ok:
                if num > 100:
                    num = 100
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[0] = ("Q Value", ela, num)
                
        
        def contrast():
            num, ok = QInputDialog.getInt(self, "Set Contrast Value", f"Current: {self.customOptions[0][2]}")
            if ok:
                if num > 3:
                    num = 3
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[0] = ("Contrast", contrast, num)
         
        def brightness():
            num, ok = QInputDialog.getInt(self, "Set Brightness Value", f"Current: {self.customOptions[1][2]}")
            if ok:
                if num > 100:
                    num = 100
                if num < 0:
                    num = 0
                num = math.floor(num)
                self.customOptions[1] = ("Brightness", brightness, num)
                       
        
        if cType == "Gaussian Blur" or cType == "Median Filter":
            self.customOptions[0] = ("Kernel Size", changeKernelSize, 3)
            
        elif cType == "Adaptive Threshold":
            self.customOptions = [("Block size", adaThreshBlock, 11), 
                                  ("Max value", adaThreshMax, 255)]
            
        elif cType == "Canny Edge":
            self.customOptions = [("Upper threshold", cannyUpper, 200),
                                  ("Lower threshold", cannyLower, 100)]
            
        elif cType == "ELA":
            self.customOptions = [("Q Value", ela, 90)]
            
        elif cType == "Noise Analysis":
            self.customOptions[0] = ("Kernel Size", changeKernelSize, 3)
        
        elif cType == "Brightness and Contrast":
            self.customOptions = [("Contrast", contrast, 1),
                                  ("Brightness", brightness, 20)]
        
        for (label, function, _) in self.customOptions:
            ac = QAction(label, self)
            
            if function != None:
                ac.triggered.connect(function)
                
            self.menu.addAction(ac)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.pos()
            
        if event.button() == Qt.RightButton:
            self.menu.popup(QCursor.pos())
            
            
        
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, e):
        if e.buttons() != Qt.LeftButton:
            return
        if ((e.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            return

        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.text())
        drag.setMimeData(mimeData)
        drag.exec()
        

# ----- For dragable checkboxes in custom filter       
class DragGroubox(QGroupBox):
    elementMoved = pyqtSignal()
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.layoutSaver = QVBoxLayout()
    
    def reset(self):
        while self.layoutSaver.count() != 0:
            w = self.layoutSaver.itemAt(0).widget()
            w.hide()
            self.layoutSaver.removeWidget(w)
        
    
    def addCheckbox(self, checkbox):
        self.layoutSaver.addWidget(checkbox)
        
    def dragEnterEvent(self, event):
        event.accept()


    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        half = widget.size().height() // 2
        a_y = pos.y()
        
        for n in range(self.layoutSaver.count()):
            w = self.layoutSaver.itemAt(n).widget()
            b_y = w.y()
            
            if a_y <= b_y + half:
                if n == 0:
                    self.layoutSaver.insertWidget(0, widget)
                else:
                    self.layoutSaver.insertWidget(n-1, widget)
                self.elementMoved.emit()
                e.accept()
                return
            
        self.layoutSaver.insertWidget(self.layoutSaver.count(), widget)
        self.elementMoved.emit()
        e.accept()