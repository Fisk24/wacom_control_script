
from lib.listeners import TabletButtonListener

from PyQt6.uic       import loadUi
from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QDialog
'''
Temporaraly disable tablet keybinds, so they dont interfere. <- Cant set buttons to 0, because the event will be ignored.
Start Listening for buttons
React to buttons "use the first available pressed key, incase user presses more then one button"
Stop Listening
Set button preference with out applying (Because they are disabled)
'''
class QuickSetDialog(QDialog):
    def __init__(self, parent=None):
        super(QuickSetDialog, self).__init__(parent)
        loadUi('lib/qtUI/quickSetDialog.ui', self)

        self.listener = TabletButtonListener()
        self.buttonId = 0
        self.dismissedEarly = False

        self.listener.setListenerCallback(self.reactToKey)
        self.listener.start()

        self.pushButton.clicked.connect(self.reject)

        parent.earlyDismisalSignal.connect(self.handleEarlyDismisal)

    def handleEarlyDismisal(self):
        self.listener.stop()
        self.dismissedEarly = True
        self.reject()

    def reactToKey(self, index):
        self.buttonId = index
        self.listener.stop()
        self.accept()
