from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor
from typeGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class TypingDisplay(QTextEdit):      #I had AI give guidance for this section but it is not copy and pasted
    def __init__(self, parent=None):            #This is essentially a new object similar to a label or line edit. 
        
        super().__init__(parent)
        self.targetText = ""  # The  sentence the user needs to type
        self.typedText = "" #What they actually typed
        self.parent_logic = None #Connects this to the other logic class and its functions
        self.testActive = False
        
        self.setReadOnly(True)
        font = QFont("Courier New", 18) 
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        #Create the style and colors for the typing display
        self.setStyleSheet("background-color: rgb(51, 51, 51); color: rgb(180, 180, 180); border: 2px solid white; border-color: #BB86FC; border-radius: 8px;")
        self.correctChar = QTextCharFormat()
        self.correctChar.setForeground(QColor("#03DAC5"))
        self.correctChar.setBackground(QColor("transparent"))
        
        self.wrongChar = QTextCharFormat()
        self.wrongChar.setForeground(QColor("#CF6679"))
        self.wrongChar.setBackground(QColor("transparent"))
        
        self.defaultFormat = QTextCharFormat()
        self.defaultFormat.setForeground(QColor("#bbbbbb"))
        
        self.backChar = QTextCharFormat()
        self.backChar.setForeground(QColor("#bbbbbb"))
        self.backChar.setBackground(QColor("transparent"))
        
        self.setCursorWidth(0)

        # Create the Translucent Block Cursor Style
        self.blockCursorFormat = QTextCharFormat()
        self.blockCursorFormat.setBackground(QColor(255, 215, 0, 100)) # Gold/Yellow translucent
        self.blockCursorFormat.setForeground(QColor("#bbbbbb")) # Keep text grey
        
    def highlightNextChar(self):
        # 1. Create a cursor to manipulate the text
        cursor = self.textCursor()
        
        # 2. Go to the current typing position
        current_index = len(self.typedText)
        
        # Stop if we are at the end of the text
        if current_index >= len(self.targetText):
            if self.parent_logic:
                self.parent_logic.stopTime() #This is why they needed connected so you can stop time automatically
            return

        # 3. Select the NEXT character (the one we want to highlight)
        cursor.setPosition(current_index)
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        
        # 4. Apply the translucent background
        cursor.setCharFormat(self.blockCursorFormat)
        
    def startTest(self, text):
        self.targetText = text
        self.typedText = ""
        self.setText(text)
        self.testActive = True
        cursor = self.textCursor()         #AI specifically helped with this part ->
        cursor.select(QTextCursor.SelectionType.Document)
        
        # Apply the default grey color to everything
        cursor.setCharFormat(self.backChar)
        
        # Deselect everything and move the blinking cursor to the start
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)   
        # Make sure this widget is active so the user can start typing immediately
        self.setFocus()                  
        self.highlightNextChar()       #<-
    
    def stopTest(self):
        self.testActive = False
    
    def resetTest(self): #Resets it to default color. 
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(self.defaultFormat)
        
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)
        
        self.setCursorWidth(0) # Hide real cursor
        self.is_active = False
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            # Call the parent event to let the signal bubble up
            super().keyPressEvent(event)
            return
        
        if not self.targetText:
            return
        
        if not self.testActive:
            return
        
        if event.key() == Qt.Key.Key_Backspace:
            if len(self.typedText) > 0:
                current_index = len(self.typedText)
                
                # First, remove the highlight from the CURRENT character (the one we're about to leave)
                cursor = self.textCursor()
                cursor.setPosition(current_index)
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor) #<-- This is AI
                cursor.setCharFormat(self.defaultFormat)
                cursor.clearSelection()
                
                # Now go back and reset the previous character to default
                self.typedText = self.typedText[:-1]
                
                cursor.setPosition(current_index - 1)
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(self.defaultFormat)
                cursor.clearSelection()
                self.setTextCursor(cursor)
                
                # Finally, highlight the NEW current character
                self.highlightNextChar()
                
            return

        # We want the Main Window to handle "Enter" (to stop the game), not this widget.
        
        if not event.text() or len(self.typedText) >= len(self.targetText):
            return

        char_typed = event.text()               # The letter the user pressed
        current_index = len(self.typedText)    # Where we are in the string
        expected_char = self.targetText[current_index] # The letter they SHOULD have pressed

        # Update our logical memory
        self.typedText += char_typed

        # update colors 
        cursor = self.textCursor()
        
        # Move the cursor to the current character
        cursor.setPosition(current_index)
        
        # Select the NEXT character so we can color it
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
        
        # Check if they typed the right key
        if char_typed == expected_char:
            cursor.setCharFormat(self.correctChar) # Color Green
        else:
            cursor.setCharFormat(self.wrongChar)   # Color Red
            
        # Finalize the update
        cursor.clearSelection()
        self.setTextCursor(cursor)
        
        self.highlightNextChar()