from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from typeGui import *
import random
import time
import csv
from datetime import datetime

#add type hinting, docstrings, private class variables, error handlin

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
        self.updateInGameLeaderboard()

    def startFunc(self):
        if not self.running:
            self.lineEdit.setReadOnly(False)
            self.lineEdit.setText("") #clear boxes
            self.wordString = ""
            self.label.setText("")
        
            self.setWordsForTest() #get the number of words and which words from the list/
            self.startTime()
    
    def resetFunc(self):
        self.label.setText(f'Click "Start" to begin')
        self.lineEdit.setText("")
        self.wordString = ""
        self.running = False
        self.initialTime = 0
        self.elapsedTime = 0
        self.lastTime = 0
        self.lastTyped = ""
        self.errors = 0
    
    def keyPressEvent(self, event):
        # Call the base class implementation to ensure default event handling
        super().keyPressEvent(event)

        if event.key() == Qt.Key.Key_Return and self.running == True:
            self.stopTime()
        elif event.key() == Qt.Key.Key_Return and self.running == False: 
            self.startFunc()
    
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
        
        with open("files/englishWords.txt", 'r') as file: #Put the OS seperator thing in here later
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
            self.lineEdit.setReadOnly(True)

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
        #net wpm = gross wpm * (accuracy)
        numChars = len(self.wordString)
        timeInMin = self.lastTime / 60 #number of seconds in a minute
        grossWPM = (numChars / 5) / timeInMin
        # print(self.errors)
        netWPM = grossWPM * (accuracy/100)
        self.wpmLabel.setText(f'Gross WPM: {grossWPM:.2f} | Net WPM: {netWPM:.2f} | Acc: {accuracy:.2f}%')
        
        self.updateLeaderboardCSV(netWPM, grossWPM, accuracy)
        # print(self.errors)
        
    def updateLeaderboardCSV(self, net, gross, acc):
        csvOutput = []
        now = datetime.now()
        formatted_date = now.strftime("%m/%d/%y") #googled this 
        data = [round(net, 3), round(gross, 3), round(acc, 3), round(self.lastTime, 3), formatted_date]
        try: 
            with open("files/leaderboard.csv", "r") as input:
                CSVreader = csv.reader(input)
                for line in CSVreader:
                    csvOutput.append(line)
                
                numEntries = len(csvOutput)
                inserted = False
                for i in range(1, numEntries):
                    if net > float(csvOutput[i][0]): #check to see if the current score is bigger than the first in the list
                        csvOutput.insert(i, data)
                        inserted = True
                        break
                if not inserted:
                    csvOutput.append(data)
                
        except FileNotFoundError: #Add to the list to be writen
            csvOutput.append(['Net WPM', 'Gross WPM', 'Accuracy', 'Time in Seconds', 'Date'])
            csvOutput.append(data)
            
        with open("files/leaderboard.csv", 'w', newline='') as output:
            CSVwriter = csv.writer(output)
            CSVwriter.writerows(csvOutput)
        
        self.updateInGameLeaderboard()
        
    def updateInGameLeaderboard(self):
        csvOutput = []
        try: 
            with open("files/leaderboard.csv", "r") as input:
                CSVreader = csv.reader(input)
                for line in CSVreader:
                    csvOutput.append(line)
                    
        except FileNotFoundError:
            for i in range(1, 6):   
                num = 3 + i
                label = getattr(self, f"label_{num}", None) #This function came from the google AI overview
                if label and len(csvOutput) > i:
                    label.setText(f'')

        entries = len(csvOutput)
        if entries > 6:
            entries = 6
            
        for i in range(1, entries):   
            num = 3 + i
            label = getattr(self, f"label_{num}", None) #This function came from the google AI overview
            if label and len(csvOutput) > i:
                wpm = float(csvOutput[i][0])
                label.setText(f'{i}) WPM: {wpm:.2f}, {csvOutput[i][4]}')
                    