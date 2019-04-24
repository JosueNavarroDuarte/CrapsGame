from sys import path
from die import *
import sys
import crapsResources_rc
from logging import basicConfig, getLogger, DEBUG, INFO, CRITICAL
from pickle import dump, load
from os import path
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QTimer, QCoreApplication
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox

startingBankDefault = 100
maximumBetDefault = 100
minimumBetDefault = 10
logFilenameDefault = 'craps.log'
createLogFileDefault = False
pickleFilenameDefault = ".crapsSavedObjects.pl"


class Craps(QMainWindow):
    """A game of Craps."""
    die1 = die2 = None

    def __init__(self, parent=None):
        """Build a game with two dice."""

        super().__init__(parent)

        self.logger = getLogger("Fireheart.craps")
        self.appSettings = QSettings()
        self.quitCounter = 0;  # used in a workaround for a QT5 bug.

        uic.loadUi("Craps.ui", self)

        self.payouts = [0, 0, 0, 0, 2.0, 1.5, 1.2, 0, 1.2, 1.5, 2.0, 0, 0]
        self.pickleFilename = pickleFilenameDefault

        self.restoreSettings()

        if path.exists(self.pickleFilename):
            self.die1, self.die2, self.firstRoll, self.results, self.playerLost, self.firstRollValue, self.buttonText, self.wins, self.losses, self.currentBet, self.currentBank = self.restoreGame()
        else:
            self.restartGame()

        self.rollButton.clicked.connect(self.rollButtonClickedHandler)
        self.bailButton.clicked.connect(self.bailButtonClickedHandler)
        self.preferencesSelectButton.clicked.connect(self.preferencesSelectButtonClickedHandler)
        self.restartButton.clicked.connect(self.restartButtonClickedHandler)

    def __str__(self):
        """String representation for Dice.
        """
        return "Die1: %s\nDie2: %s" % (str(self.die1), str(self.die2))

    def updateUI(self):
        if self.createLogFile:
            self.logger.info("Die1: %i, Die2: %i" % (self.die1.getValue(), self.die2.getValue()))
        self.bidSpinBox.setRange(self.minimumBet, self.maximumBet)
        self.bidSpinBox.setSingleStep(5)
        self.die1View.setPixmap(QtGui.QPixmap(":/" + str(self.die1.getValue())))
        self.die2View.setPixmap(QtGui.QPixmap(":/" + str(self.die2.getValue())))
        if self.firstRoll:
            self.rollingForLabel.setText("")
        else:
            self.rollingForLabel.setText(str("%i" % self.firstRollValue))
        self.resultsLabel.setText(self.results)
        self.rollButton.setText(self.buttonText)
        self.winsLabel.setText(str("%i" % self.wins))
        self.lossesLabel.setText(str("%i" % self.losses))
        self.bankValue.setText(str("%i" % self.currentBank))

    def restartGame(self):
        if self.createLogFile:
            self.logger.debug("Restarting game")
        self.die1 = Die()
        self.die2 = Die()
        self.die1.setValue(5)
        self.die2.setValue(6)
        self.firstRoll = True
        self.bailButton.setEnabled(False)
        self.results = ""
        self.playerLost = False
        self.firstRollValue = 0
        self.buttonText = "Roll"
        self.wins = 0
        self.losses = 0
        self.currentBet = 0
        self.currentBank = self.startingBank

    def saveGame(self):
        if self.createLogFile:
            self.logger.debug("Saving game")
        saveItems = (self.die1, self.die2, self.firstRoll, self.results, self.playerLost, self.firstRollValue, self.buttonText, self.wins, self.losses, self.currentBet, self.currentBank)
        if self.appSettings.contains('pickleFilename'):
            with open(path.join(path.dirname(path.realpath(__file__)),
                                self.appSettings.value('pickleFilename', type=str)), 'wb') as pickleFile:
                dump(saveItems, pickleFile)
        elif self.createLogFile:
            self.logger.critical("No pickle Filename")

    def restoreGame(self):
        if self.appSettings.contains('pickleFilename'):
            self.appSettings.value('pickleFilename', type=str)
            with open(path.join(path.dirname(path.realpath(__file__)),
                                self.appSettings.value('pickleFilename', type=str)), 'rb') as pickleFile:
                return load(pickleFile)
        else:
            self.logger.critical("No pickle Filename")

    def restoreSettings(self):
        if appSettings.contains('createLogFile'):
            self.createLogFile = appSettings.value('createLogFile')
        else:
            self.createLogFile = createLogFileDefault
            appSettings.setValue('createLogFile', createLogFile)

        if self.createLogFile:
            self.logger.debug("Starting restoreSettings")
        # Restore settings values, write defaults to any that don't already exist.
        if self.appSettings.contains('startingBank'):
            self.startingBank = self.appSettings.value('startingBank', type=int)
        else:
            self.startingBank = startingBankDefault
            self.appSettings.setValue('startingBank', self.startingBank)

        if self.appSettings.contains('maximumBet'):
            self.maximumBet = self.appSettings.value('maximumBet', type=int)
        else:
            self.maximumBet = maximumBetDefault
            self.appSettings.setValue('maximumBet', self.maximumBet)

        if self.appSettings.contains('minimumBet'):
            self.minimumBet = self.appSettings.value('minimumBet', type=int)
        else:
            self.minimumBet = minimumBetDefault
            self.appSettings.setValue('minimumBet', self.minimumBet)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('pickleFilename'):
            self.pickleFilename = self.appSettings.value('pickleFilename', type=str)
        else:
            self.pickleFilename = pickleFilenameDefault
            self.appSettings.setValue('pickleFilename', self.pickleFilename)

    @pyqtSlot()  # Player asked for another roll of the dice.
    def rollButtonClickedHandler(self):
        self.currentBet = self.bidSpinBox.value()
        # Play the first roll
        self.results = ""
        if self.firstRoll:
            self.die1.roll()
            self.die2.roll()
            if (self.die1.getValue() + self.die2.getValue()) == 7 or (
                    self.die1.getValue() + self.die2.getValue()) == 11:
                self.results = "Craps, You win!"
                self.wins += 1
                self.currentBank += self.currentBet
                self.firstRoll = True
                self.bailButton.setEnabled(False)
            elif self.die1.getValue() + self.die2.getValue() == 2 or self.die1.getValue() + self.die2.getValue() == 3 or self.die1.getValue() + self.die2.getValue() == 12:
                self.results = "You lose!"
                self.losses += 1
                self.firstRoll = True
                self.bailButton.setEnabled(False)
                self.currentBank -= self.currentBet
            else:
                self.firstRollValue = self.die1.getValue() + self.die2.getValue()
                self.firstRoll = False
                self.bailButton.setEnabled(True)
                self.results = "{0}".format(self.die1.getValue() + self.die2.getValue())
                self.buttonText = "Roll Again"
        else:
            # Play the following rolls
            self.die1.roll()
            self.die2.roll()
            if self.createLogFile:
                self.logger.info("First Roll %s, New Winner: %i, Die1: %i, Die2 %i" % (
            self.firstRoll, self.firstRollValue, self.die1.getValue(), self.die2.getValue()))
            thisRoll = self.die1.getValue() + self.die2.getValue()
            if thisRoll == self.firstRollValue:
                if self.createLogFile:
                    self.logger.info("You win!!")
                self.results = "You win!"
                self.currentBank += self.currentBet * self.payouts[thisRoll]
                self.wins += 1
                self.bailButton.setEnabled(False)
                self.firstRoll = True
            else:
                if self.createLogFile:
                    self.logger.info("You lose!")
                self.results = "You lose!"
                self.losses += 1
                self.currentBank -= self.currentBet * self.payouts[thisRoll]
                self.firstRoll = True
                self.bailButton.setEnabled(False)
                self.buttonText = "Roll"
        self.updateUI()
        if self.createLogFile:
            self.logger.debug("Roll button clicked")

    @pyqtSlot()  # Player asked for another roll of the dice.
    def bailButtonClickedHandler(self):
        if self.createLogFile:
            self.logger.debug("Bail button clicked")
        self.losses += 1
        self.currentBank -= self.currentBet
        self.firstRoll = True
        self.results = "Bailed!"
        self.bailButton.setEnabled(False)
        self.buttonText = "Roll"
        self.updateUI()

    @pyqtSlot()  # User is requesting preferences editing dialog box.
    def preferencesSelectButtonClickedHandler(self):
        if self.createLogFile:
            self.logger.info("Setting preferences")
        preferencesDialog = PreferencesDialog()
        preferencesDialog.show()
        preferencesDialog.exec_()
        self.restoreSettings()  # 'Restore' settings that were changed in the dialog window.
        self.updateUI()

    @pyqtSlot()  # User is requesting the game be restarted.
    def restartButtonClickedHandler(self):
        if self.createLogFile:
            self.logger.debug("Restart button clicked")
        self.restartGame()
        self.saveGame()
        self.updateUI()

    @pyqtSlot()  # Player asked to quit the game.
    def closeEvent(self, event):
        if self.createLogFile:
            self.logger.debug("Closing app event")
        if self.quitCounter == 0:
            self.quitCounter += 1
            quitMessage = "Are you sure you want to quit?"
            reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.saveGame()
            event.accept()
        else:
            event.ignore()
            return super().closeEvent(event)


class PreferencesDialog(QDialog):
    def __init__(self, parent=Craps):
        super(PreferencesDialog, self).__init__()

        uic.loadUi('preferencesDialog.ui', self)
        self.logger = getLogger("Fireheart.craps")

        self.appSettings = QSettings()
        if self.appSettings.contains('startingBank'):
            self.startingBank = self.appSettings.value('startingBank', type=int)
        else:
            self.startingBank = startingBankDefault
            self.appSettings.setValue('startingBank', self.startingBank)

        if self.appSettings.contains('maximumBet'):
            self.maximumBet = self.appSettings.value('maximumBet', type=int)
        else:
            self.maximumBet = maximumBetDefault
            self.appSettings.setValue('maximumBet', self.logFilename)

        if self.appSettings.contains('minimumBet'):
            self.minimumBet = self.appSettings.value('minimumBet', type=int)
        else:
            self.minimumBet = minimumBetDefault
            self.appSettings.setValue('minimumBet', self.minimumBet)

        if self.appSettings.contains('logFile'):
            self.logFilename = self.appSettings.value('logFile', type=str)
        else:
            self.logFilename = logFilenameDefault
            self.appSettings.setValue('logFile', self.logFilename)

        if self.appSettings.contains('createLogFile'):
            self.createLogFile = self.appSettings.value('createLogFile')
        else:
            self.createLogFile = logFilenameDefault
            self.appSettings.setValue('createLogFile', self.createLogFile)

        self.buttonBox.rejected.connect(self.cancelClickedHandler)
        self.buttonBox.accepted.connect(self.okayClickedHandler)
        self.startingBankValue.editingFinished.connect(self.startingBankValueChanged)
        self.maximumBetValue.editingFinished.connect(self.maximumBetValueChanged)
        self.minimumBetValue.editingFinished.connect(self.minimumBetValueChanged)
        self.createLogfileCheckBox.stateChanged.connect(self.createLogFileChanged)

        self.updateUI()

    # @pyqtSlot()
    def startingBankValueChanged(self):
        self.startingBank = int(self.startingBankValue.text())

    # @pyqtSlot()
    def maximumBetValueChanged(self):
        self.maximumBet = int(self.maximumBetValue.text())

    # @pyqtSlot()
    def minimumBetValueChanged(self):
        self.minimumBet = int(self.minimumBetValue.text())

    # @pyqtSlot()
    def createLogFileChanged(self):
        self.createLogFile = self.createLogfileCheckBox.isChecked()

    def updateUI(self):
        self.startingBankValue.setText(str(self.startingBank))
        self.maximumBetValue.setText(str(self.maximumBet))
        self.minimumBetValue.setText(str(self.minimumBet))
        if self.createLogFile:
            self.createLogfileCheckBox.setCheckState(Qt.Checked)
        else:
            self.createLogfileCheckBox.setCheckState(Qt.Unchecked)

    # @pyqtSlot()
    def okayClickedHandler(self):
        # write out all settings
        self.preferencesGroup = (('startingBank', self.startingBank), \
                                 ('maximumBet', self.maximumBet), \
                                 ('minimumBet', self.minimumBet), \
                                 ('logFile', self.logFilename), \
                                 ('createLogFile', self.createLogFile), \
                                 )
        # Write settings values.
        for setting, variableName in self.preferencesGroup:
            # if self.appSettings.contains(setting):
            self.appSettings.setValue(setting, variableName)

            self.close()

    # @pyqtSlot()
    def cancelClickedHandler(self):
        self.close()


if __name__ == "__main__":
    QCoreApplication.setOrganizationName("Fireheart Software");
    QCoreApplication.setOrganizationDomain("fireheartsoftware.com");
    QCoreApplication.setApplicationName("Craps");
    appSettings = QSettings()
    if appSettings.contains('createLogFile'):
        createLogFile = appSettings.value('createLogFile')
    else:
        createLogFile = createLogFileDefault
        appSettings.setValue('createLogFile', createLogFile)
    if createLogFile:
        startingFolderName = path.dirname(path.realpath(__file__))
        if appSettings.contains('logFile'):
            logFilename = appSettings.value('logFile', type=str)
        else:
            logFilename = logFilenameDefault
            appSettings.setValue('logFile', logFilename)
            basicConfig(filename=path.join(startingFolderName, logFilename), level=INFO,
                        format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
    app = QApplication(sys.argv)
    diceApp = Craps()
    diceApp.show()
    diceApp.updateUI()
    sys.exit(app.exec())
