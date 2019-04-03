#!/usr/bin/env python

import sys
from time import sleep
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import  QMainWindow, QApplication

class Demo(QMainWindow) :
    """Build a game demo."""

    def __init__( self, parent=None ):
        super().__init__(parent)
        uic.loadUi("Demo.ui", self)

        self.button.clicked.connect(self.buttonClickedHandler)

    def updateUI ( self ):
        self.outputLabel.setText("Click!")        # Add your code here to update the GUI view so it matches the game state.

    def buttonClickedHandler( self ):
        print("Button clicked")            # Replace this line with your roll event handler
        self.updateUI()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    diceApp = Demo()
    diceApp.show()
    sys.exit(app.exec_())


