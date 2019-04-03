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
   pickleFilenameDefault = ".crapsSavedObjects.pl"

   class Craps(QMainWindow):
       """A game of Craps."""
       die1 = die2 = None

       def __init__(self, parent=None):
           """Build a game with two dice."""

           super().__init__(parent)

           self.logger = getLogger("Fireheart.craps")
           self.appSettings = QSettings()
           self.quitCounter = 0;       # used in a workaround for a QT5 bug.

           uic.loadUi("Craps.ui", self)

           self.payouts = [0, 0, 0,  0,  2.0,  1.5,  1.2,  0,  1.2,  1.5,  2.0,  0,  0]
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

           return "Die1: %s\nDie2: %s" % (str(self.die1),  str(self.die2))

       def updateUI(self):
           if self.createLogFile:
               self.logger.info("Die1: %i, Die2: %i" % (self.die1.getValue(),  self.die2.getValue()))
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
86           self.buttonText = "Roll"
87           self.wins = 0
88           self.losses = 0
89           self.currentBet = 0
90           self.currentBank = self.startingBank
91
92       def saveGame(self):
93           if self.createLogFile:
94               self.logger.debug("Saving game")
95           saveItems = (self.die1, self.die2, self.firstRoll, self.results, self.playerLost, self.firstRollValue, self.buttonText,self.wins, self.losses, self.currentBet, self.currentBank)
96           if self.appSettings.contains('pickleFilename'):
97               with open(path.join(path.dirname(path.realpath(__file__)),  self.appSettings.value('pickleFilename', type=str)), 'wb') as pickleFile:
98                   dump(saveItems, pickleFile)
99           elif self.createLogFile:
100                  self.logger.critical("No pickle Filename")
101
102      def restoreGame(self):
103          if self.appSettings.contains('pickleFilename'):
104              self.appSettings.value('pickleFilename', type=str)
105              with open(path.join(path.dirname(path.realpath(__file__)),  self.appSettings.value('pickleFilename', type=str)), 'rb') as pickleFile:
106                  return load(pickleFile)
107          else:
108              self.logger.critical("No pickle Filename")
109
110      def restoreSettings(self):
111          if self.createLogFile:
112              self.logger.debug("Starting restoreSettings")
113          # Restore settings values, write defaults to any that don't already exist.
114          if self.appSettings.contains('startingBank'):
115              self.startingBank = self.appSettings.value('startingBank', type=int)
116          else:
117              self.startingBank = startingBankDefault
118              self.appSettings.setValue('startingBank', self.startingBank )
119
120          if self.appSettings.contains('maximumBet'):
121              self.maximumBet = self.appSettings.value('maximumBet', type=int)
122          else:
123              self.maximumBet = maximumBetDefault
124              self.appSettings.setValue('maximumBet', self.maximumBet )
125
126          if self.appSettings.contains('minimumBet'):
127              self.minimumBet = self.appSettings.value('minimumBet', type=int)
128          else:
129              self.minimumBet = minimumBetDefault
130              self.appSettings.setValue('minimumBet', self.minimumBet )
131
132          if self.appSettings.contains('createLogFile'):
133              self.createLogFile = self.appSettings.value('createLogFile')
134          else:
135              self.createLogFile = logFilenameDefault
136              self.appSettings.setValue('createLogFile', self.createLogFile )
137
138          if self.appSettings.contains('logFile'):
139              self.logFilename = self.appSettings.value('logFile', type=str)
140          else:
141              self.logFilename = logFilenameDefault
142              self.appSettings.setValue('logFile', self.logFilename )
143
144          if self.appSettings.contains('pickleFilename'):
145              self.pickleFilename = self.appSettings.value('pickleFilename', type=str)
146          else:
147              self.pickleFilename = pickleFilenameDefault
148              self.appSettings.setValue('pickleFilename', self.pickleFilename)
149
150      @pyqtSlot()				# Player asked for another roll of the dice.
151      def rollButtonClickedHandler ( self ):
152          self.currentBet = self.bidSpinBox.value()
153          # Play the first roll
154          self.results = ""
155          if self.firstRoll:
156              self.die1.roll()
157              self.die2.roll()
158              if (self.die1.getValue() + self.die2.getValue()) == 7 or (self.die1.getValue() + self.die2.getValue()) == 11:
159                  self.results = "Craps, You win!"
160                  self.wins += 1
161                  self.currentBank += self.currentBet
162                  self.firstRoll = True
163                  self.bailButton.setEnabled(False)
164              elif self.die1.getValue() + self.die2.getValue() == 2 or self.die1.getValue() + self.die2.getValue() == 3 or self.die1.getValue() + self.die2.getValue() == 12:
165                  self.results = "You lose!"
166                  self.losses += 1
167                  self.firstRoll = True
168                  self.bailButton.setEnabled(False)
169                  self.currentBank -= self.currentBet
170              else:
171                  self.firstRollValue = self.die1.getValue() + self.die2.getValue()
172                  self.firstRoll = False
173                  self.bailButton.setEnabled(True)
174                  self.buttonText = "Roll Again"
175          else:
176              # Play the following rolls
177              self.die1.roll()
178              self.die2.roll()
179              if self.createLogFile:
180                  self.logger.info("First Roll %s, New Winner: %i, Die1: %i, Die2 %i" % (self.firstRoll, self.firstRollValue, self.die1.getValue(), self.die2.getValue()))
181              thisRoll =  self.die1.getValue() + self.die2.getValue()
182              if thisRoll == self.firstRollValue:
183                  if self.createLogFile:
184                      self.logger.info("You win!!")
185                  self.results = "You win!"
186                  self.currentBank += self.currentBet * self.payouts[thisRoll]
187                  self.wins += 1
188                  self.firstRoll = True
189                  self.bailButton.setEnabled(False)
190              else:
191                  if self.createLogFile:
192                      self.logger.info("You lose!")
193                  self.results = "You lose!"
194                  self.losses += 1
195                  self.currentBank -= self.currentBet * self.payouts[thisRoll]
196                  self.firstRoll = True
197                  self.bailButton.setEnabled(False)
198                  self.buttonText = "Roll"
199          self.updateUI()
200          if self.createLogFile:
201              self.logger.debug("Roll button clicked")
202
203      @pyqtSlot()				# Player asked for another roll of the dice.
204      def bailButtonClickedHandler ( self ):
205          if self.createLogFile:
206              self.logger.debug("Bail button clicked")
207          self.losses += 1
208          self.currentBank -= self.currentBet
209          self.firstRoll = True
210          self.results = "Bailed!"
211          self.bailButton.setEnabled(False)
212          self.buttonText = "Roll"
213          self.updateUI()
214
215      @pyqtSlot()  # User is requesting preferences editing dialog box.
216      def preferencesSelectButtonClickedHandler(self):
217          if self.createLogFile:
218              self.logger.info("Setting preferences")
219          preferencesDialog = PreferencesDialog()
220          preferencesDialog.show()
221          preferencesDialog.exec_()
222          self.restoreSettings()              # 'Restore' settings that were changed in the dialog window.
223          self.updateUI()
224
225      @pyqtSlot()  # User is requesting the game be restarted.
226      def restartButtonClickedHandler(self):
227          if self.createLogFile:
228              self.logger.debug("Restart button clicked")
229          self.restartGame()
230          self.saveGame()
231          self.updateUI()
232
233      @pyqtSlot()				# Player asked to quit the game.
234      def closeEvent(self, event):
235          if self.createLogFile:
236              self.logger.debug("Closing app event")
237          if self.quitCounter == 0:
238              self.quitCounter += 1
239              quitMessage = "Are you sure you want to quit?"
240              reply = QMessageBox.question(self, 'Message', quitMessage, QMessageBox.Yes, QMessageBox.No)
241
242              if reply == QMessageBox.Yes:
243                  self.saveGame()
244                  event.accept()
245              else:
246                  event.ignore()
247              return super().closeEvent(event)
248
249  class PreferencesDialog(QDialog):
250      def __init__(self, parent = Craps):
251          super(PreferencesDialog, self).__init__()
252
253          uic.loadUi('preferencesDialog.ui', self)
254          self.logger = getLogger("Fireheart.craps")
255
256          self.appSettings = QSettings()
257          if self.appSettings.contains('startingBank'):
258              self.startingBank = self.appSettings.value('startingBank', type=int)
259          else:
260              self.startingBank = startingBankDefault
261              self.appSettings.setValue('startingBank', self.startingBank)
262
263          if self.appSettings.contains('maximumBet'):
264              self.maximumBet = self.appSettings.value('maximumBet', type=int)
265          else:
266              self.maximumBet = maximumBetDefault
267              self.appSettings.setValue('maximumBet', self.logFilename)
268
269          if self.appSettings.contains('minimumBet'):
270              self.minimumBet = self.appSettings.value('minimumBet', type=int)
271          else:
272              self.minimumBet = minimumBetDefault
273              self.appSettings.setValue('minimumBet', self.minimumBet)
274
275          if self.appSettings.contains('logFile'):
276              self.logFilename = self.appSettings.value('logFile', type=str)
277          else:
278              self.logFilename = logFilenameDefault
279              self.appSettings.setValue('logFile', self.logFilename )
280
281          if self.appSettings.contains('createLogFile'):
282              self.createLogFile = self.appSettings.value('createLogFile')
283          else:
284              self.createLogFile = logFilenameDefault
285              self.appSettings.setValue('createLogFile', self.createLogFile )
286
287          self.buttonBox.rejected.connect(self.cancelClickedHandler)
288          self.buttonBox.accepted.connect(self.okayClickedHandler)
289          self.startingBankValue.editingFinished.connect(self.startingBankValueChanged)
290          self.maximumBetValue.editingFinished.connect(self.maximumBetValueChanged)
291          self.minimumBetValue.editingFinished.connect(self.minimumBetValueChanged)
292          self.createLogfileCheckBox.stateChanged.connect(self.createLogFileChanged)
293
294          self.updateUI()
295
296      # @pyqtSlot()
297      def startingBankValueChanged(self):
298          self.startingBank = int(self.startingBankValue.text())
299
300      # @pyqtSlot()
301      def maximumBetValueChanged(self):
302          self.maximumBet = int(self.maximumBetValue.text())
303
304      # @pyqtSlot()
305      def minimumBetValueChanged(self):
306          self.minimumBet = int(self.minimumBetValue.text())
307
308      # @pyqtSlot()
309      def createLogFileChanged(self):
310          self.createLogFile = self.createLogfileCheckBox.isChecked()
311
312      def updateUI(self):
313          self.startingBankValue.setText(str(self.startingBank))
314          self.maximumBetValue.setText(str(self.maximumBet))
315          self.minimumBetValue.setText(str(self.minimumBet))
316          if self.createLogFile:
317              self.createLogfileCheckBox.setCheckState(Qt.Checked)
318          else:
319              self.createLogfileCheckBox.setCheckState(Qt.Unchecked)
320
321      # @pyqtSlot()
322      def okayClickedHandler(self):
323          # write out all settings
324          self.preferencesGroup = (('startingBank', self.startingBank), \
325                              ('maximumBet', self.maximumBet), \
326                              ('minimumBet', self.minimumBet), \
327                              ('logFile', self.logFilename), \
328                              ('createLogFile', self.createLogFile), \
329                              )
330          # Write settings values.
331          for setting, variableName in self.preferencesGroup:
332              # if self.appSettings.contains(setting):
333              self.appSettings.setValue(setting, variableName)
334
335          self.close()
336
337      # @pyqtSlot()
338      def cancelClickedHandler(self):
339          self.close()
340
341  if __name__ == "__main__":
342      QCoreApplication.setOrganizationName("Fireheart Software");
343      QCoreApplication.setOrganizationDomain("fireheartsoftware.com");
344      QCoreApplication.setApplicationName("Craps");
345      appSettings = QSettings()
346      if appSettings.contains('createLogFile'):
347          createLogFile = appSettings.value('createLogFile')
348      else:
349          logFilename = logFilenameDefault
350          appSettings.setValue('logFile', logFilename)
351      if createLogFile:
352          startingFolderName = path.dirname(path.realpath(__file__))
353          if appSettings.contains('logFile'):
354              logFilename = appSettings.value('logFile', type=str)
355          else:
356              logFilename = logFilenameDefault
357              appSettings.setValue('logFile', logFilename)
358          basicConfig(filename = path.join(startingFolderName, logFilename), level=INFO,
359                      format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
360      app = QApplication(sys.argv)
361      diceApp = Craps()
362      diceApp.show()
363      diceApp.updateUI()
364      sys.exit(app.exec())