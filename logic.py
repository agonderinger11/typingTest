from PyQt6.QtWidgets import *
from typeGui import *
import random
import time

class Logic(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Initialize instance variables
        self.wordString = ""
        self.running = False
        self.initialTime = 0
        self.elapsedTime = 0
        self.lastTime = 0
        self.lastTyped = ""
        self.errors = 0
        
        self.startButton.clicked.connect(self.startFunc)
        self.resetButton.clicked.connect(self.resetFunc)

    def startFunc(self):
        if not self.running:
            self.lineEdit.setText("") #clear boxes
            self.wordString = ""
            self.label.setText("")
        
        self.setWordsForTest() #get the number of words and which words from the list/
        self.startTime()
    
    def resetFunc(self):
        self.stopTime() #DONT FORGET THIS
        
        self.label.setText(f'Click "Start" to begin')
        self.lineEdit.setText("")
    
    def getRadioButton(self):
        if self.radioButton.isChecked():
            return 5 #number of words for test
        elif self.radioButton_2.isChecked():
            return 10
        elif self.radioButton_3.isChecked():
            return 15
        elif self.radioButton_4.isChecked():
            return 20
        else: 
            return 10 #make sure a value is returned

    def setWordsForTest(self):
        amount = self.getRadioButton()
        
        with open("files/englishWords.txt", 'r') as file:
            lines = file.readlines()
            for i in range(amount):
                randomNumber = random.randint(1, 5000)
                randomWord = lines[randomNumber].strip()
                self.wordString = self.wordString + randomWord + " "
        
        self.wordString = self.wordString[:-1] #gets rid of ending space
        self.label.setText(self.wordString)
    
    def startTime(self):
        if not self.running:
            self.initialTime = time.perf_counter() #from python time documentation
            self.running = True
            
    def stopTime(self):
        if self.running:
            endTime = time.perf_counter()
            self.elapsedTime = endTime - self.initialTime
            self.running = False
            
            self.lastTime = self.elapsedTime
            accuracy = self.getAccuracy()
            self.calculateWPM(accuracy)
            
            self.initialTime = 0
            self.elapsedTime = 0.0

    def getAccuracy(self):
        actualChars = list(self.wordString)
        typedChars = list(self.lineEdit.text())
        # print(typedChars) 
        correct = 0
        self.errors = 0
        total = len(actualChars)
        numTyped = len(typedChars)
        
        if numTyped < total:
            length = numTyped
            self.errors += (total - numTyped) #these account for typing too much or too little
        elif numTyped > total:
            length = total
            self.errors += (numTyped - total)
        else:
            length = numTyped
        
        for i in range(length):
            if typedChars[i] == actualChars[i]:
                correct += 1
            else: 
                self.errors += 1
            
        return (correct / total) * 100 #accuracy 
    
    def calculateWPM(self, accuracy):
        #gross wpm = (total chars / 5) / time in minutes -> from google 
        #net wpm = gross wpm - (erros/ time in minutes)
        numChars = len(self.wordString)
        timeInMin = self.lastTime / 60 #number of seconds in a minute
        grossWPM = (numChars / 5) / timeInMin
        print(self.errors)
        netWPM = grossWPM - (self.errors / timeInMin)
        self.wpmLabel.setText(f'Gross WPM: {grossWPM:.2f} | Net WPM: {netWPM:.2f} | Acc: {accuracy:.2f}')