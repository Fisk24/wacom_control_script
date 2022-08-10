from PyQt6.uic       import loadUi
from PyQt6.QtWidgets import QDialog

class WarningResetBindingsDialog(QDialog):
    def __init__(self, parent=None):
        super(WarningResetBindingsDialog, self).__init__(parent)
        loadUi("lib/qtUI/warningResetBindings.ui", self)
