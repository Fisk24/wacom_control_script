from PyQt6.uic       import loadUi
from PyQt6.QtWidgets import QDialog
# TODO: refactor to KeyBindEditorDialog, class and file name
# TODO: Dialog should have a button to set the tablet binding to "Do Nothing"
class SetKeyBindDialog(QDialog):
    def __init__(self, keybindDict, parent=None):
        super(SetKeyBindDialog, self).__init__(parent)
        loadUi("lib/qtUI/set_keybind_dialog.ui", self)

        self.originalBinding = keybindDict
        self.newBinding      = keybindDict
        self.dismissedEarly  = False

        self.buttonNameLabel.setText("Button {}".format(self.originalBinding["id"]))
        self.keybindLineEdit.setText(self.originalBinding["value"])
        self.keybindLineEdit.textChanged.connect(self.setNewBindingDict)
        self.keybindLineEdit.returnPressed.connect(self.submitClose)
        self.okPushButton.clicked.connect(self.submitClose)
        self.cancelPushButton.clicked.connect(self.reject)

        parent.earlyDismisalSignal.connect(self.handleEarlyDismisal)

    def handleEarlyDismisal(self):
        self.dismissedEarly = True
        self.reject()

    def setNewBindingDict(self, newValue):
        self.newBinding["value"] = newValue

    def submitClose(self):
        self.accept()
