from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from typeGui import *
import random
import time
import csv
from datetime import datetime
from typingWindowLogic import *
import os

class Logic(QMainWindow, Ui_MainWindow): 
    """
    This class provides the logic for the main window such as handling button presses/ radio buttons, leaderboard updating,
    WPM Calculations, setting words for the test, and handling time 
    """
    def __init__(self) -> None:
        """
        This creates an instance of the main window for which the user interacts with. 
        Initilizes class variables such as running, time vars and errors.
        Creates an instance fo the typing widget on itself.
        Intiliazes the leaderboard
        """
        super().__init__()
        self.setupUi(self)
        
        self.label.hide() #Hides first iteration without deleting work 
        self.lineEdit.hide() #Same thing
        
        #Creating the typing window
        self.typingWidget = TypingDisplay(self.centralwidget)
        self.typingWidget.parentLogic = self 
        self.typingWidget.setGeometry(50, 40, 521, 110)
        self.typingWidget.setText("Click 'Start', or press Enter to begin")

        # Initialize instance variables
        self.__running: bool = False
        self.__initialTime: float = 0
        self.__elapsedTime: float = 0
        
        # Connecting buttons
        self.startButton.clicked.connect(self.startFunc)
        self.resetButton.clicked.connect(self.resetFunc)
        self.updateInGameLeaderboard()
    
    
    def startFunc(self) -> None:
        """
        Connects to the start button on the home page as well as the enter/ return key.
        Resets prior labels displaying results and starts the time.
        """
        self.typingWidget.setReadOnly(True) # Ensure it stays read-only   
        self.wpmLabel.setText("Words Per Minute:")
        self.setWordsForTest() #get the number of words and which words from the list
        
        self.__initialTime = time.perf_counter() #from python time documentation
        self.__running = True
        self.typingWidget.setFocus() # Automatically click into the box
    
    def resetFunc(self) -> None:
        """
        Used to stop a test in the middle and not enter a time to the leaderboard
        Resets the typing widget and its text.
        """ 
        self.typingWidget.setText("Click 'Start', or press Enter to begin")
        self.typingWidget.setReadOnly(True)
        self.typingWidget.typedText = ""
        self.typingWidget.targetText = ""
        
        self.__running = False
        self.__initialTime = 0
        self.__elapsedTime = 0
        
        self.typingWidget.resetTest()
        
    def stopTime(self) -> None:
        """
        Get the time when the runs ends and subtracts it fromt the intial time to get the elapsed time
        Sets running to false and then calls the calculate WPM function and then resets the class level variables. 
        Also calls the typing widget logic to stop the test.
        """
        if self.__running:
            endTime = time.perf_counter()
            self.__elapsedTime = endTime - self.__initialTime
            self.__running = False
            
            accuracy = self.getAccuracy()
            self.calculateWPM(accuracy)
            
            self.__initialTime = 0
            self.__elapsedTime = 0.0
            self.lineEdit.setReadOnly(True)
            
            self.typingWidget.stopTest()
    
    def keyPressEvent(self, event) -> None:
        """
        Handles keyboard input, specifically the return/enter key which either starts or stops the time.
        If it is not return/ enter let PyQt6 handle the keypress.
        """
        if event.key() == Qt.Key.Key_Return and self.__running == True:
            self.stopTime()
        elif event.key() == Qt.Key.Key_Return and self.__running == False: 
            self.startFunc()
        else: 
            super().keyPressEvent(event)
    
    def getRadioButton(self) -> int:
        """
        Logic for the radio buttons which correlates to how many words are on your test. 
        Returns a number that equals the number of words. 
        """
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

    def setWordsForTest(self) -> None:
        """
        This function randomly gets words from the 5000 most commonm english words which I got from Google.
        Looks to see how many words were selected in the getRadioButton() function and creates a string with 
        concatenation. This then passes the string to the typing display which updates its display and shows the words. 
        """
        amount = self.getRadioButton()
        wordString = ''
        path = os.path.join('files', 'englishWords.txt')
        with open(path, 'r') as file: #Put the OS seperator thing in here later
            lines = file.readlines()
            for i in range(amount):
                randomNumber = random.randint(1, 5000)
                randomWord = lines[randomNumber].strip()
                wordString = wordString + randomWord + " "
        
        wordString = wordString[:-1] #gets rid of ending space
        self.typingWidget.startTest(wordString)    
        

    def getAccuracy(self) -> float:
        """
        Calculates accuracy of words typed based on what was typed vs what supposed to be typed
        Accounts for if the amount of words typed was too long or too short to ensure no index errors and provide accurate accuracy
        """
        actualChars = list(self.typingWidget.targetText)
        typedChars = list(self.typingWidget.typedText)

        correct = 0
        errors = 0
        total = len(actualChars)
        numTyped = len(typedChars)
        
        if numTyped < total:
            length = numTyped
            errors += (total - numTyped) #these account for typing too much or too little
        elif numTyped > total:
            length = total
            errors += (numTyped - total)
        else:
            length = numTyped
        
        for i in range(length):
            if typedChars[i] == actualChars[i]:
                correct += 1
            else: 
                errors += 1
            
        return (correct / total) * 100 #accuracy 
    
    def calculateWPM(self, accuracy: float) -> None:
        """
        Calculates both the gross WPM and net words per minute using the standard equations
        Gross wpm = (total characters / 5) / time in minutes -> from google 
        net wpm = gross wpm * (accuracy)
        Updates the label that tells you your score
        """
        numChars = len(self.typingWidget.targetText)
        timeInMin = self.__elapsedTime / 60 #number of seconds in a minute
        
        grossWPM = (numChars / 5) / timeInMin
        netWPM = grossWPM * (accuracy/100)
        
        self.wpmLabel.setText(f'Gross WPM: {grossWPM:.2f} | Net WPM: {netWPM:.2f} | Acc: {accuracy:.2f}%')
        
        self.updateLeaderboardCSV(netWPM, grossWPM, accuracy)
        
    def updateLeaderboardCSV(self, net: float, gross: float, acc: float) -> None:
        """
        Updates the stored leaderboard CSV.
        If a CSV has not been created then it handles the error and creates one. 
        If there is a CSV then it is updated with information passed to when called.
        Data in the CSV is formatted as: Net WPM, Gross WPM, Accuracy, Time in Min, Date
        The update in game leaderboard function is called at the end as well.
        """
        csvOutput = []
        now = datetime.now()
        formatted_date = now.strftime("%m/%d/%y") #googled this 
        data = [round(net, 3), round(gross, 3), round(acc, 3), round(self.__elapsedTime, 3), formatted_date]
        path = os.path.join('files', 'leaderboard.csv')
        try: 
            with open(path, "r") as input:
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
            
        with open(path, 'w', newline='') as output:
            CSVwriter = csv.writer(output)
            CSVwriter.writerows(csvOutput)
        
        self.updateInGameLeaderboard()
        
    def updateInGameLeaderboard(self):
        """
        Gets data from the leaderboard CSV and updates the in game display. 
        Handles the error of finding no file and sets all the lines to blank.
        Also accounts for less than 5 entries
        """
        csvOutput = []
        path = os.path.join('files', 'leaderboard.csv')
        try: 
            with open(path, "r") as input:
                CSVreader = csv.reader(input)
                for line in CSVreader:
                    csvOutput.append(line)
                    
        except FileNotFoundError:
            for i in range(1, 6):   
                num = 3 + i
                label = getattr(self, f"label_{num}", None) #The getattr function came from the google AI overview
                if label and len(csvOutput) > i:
                    label.setText(f'')

        entries = len(csvOutput)
        if entries > 6:
            entries = 6
            
        for i in range(1, entries):   
            num = 3 + i
            label = getattr(self, f"label_{num}", None) #The getattr function came from the google AI overview
            if label and len(csvOutput) > i:
                wpm = float(csvOutput[i][0])
                label.setText(f'{i}) WPM: {wpm:.2f}, {csvOutput[i][4]}')