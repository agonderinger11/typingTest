from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from typeGui import *

class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.startButton.clicked.connect(self.startButton)
        self.resetButton.clicked.connect(self.resetButton)

    def startButton(self):
        pass
    
    def resetButton(self):
        pass
    
    def getRadioButton(self):
        if self.radioButton.isChecked():
            return 5 #number of words for test
        elif self.radioButton_2.isChecked():
            return 10
        elif self.radioButton_3.isChecked():
            return 15