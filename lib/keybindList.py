from PyQt6.uic       import loadUi
from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

from lib.util        import dump

class KeybindListElement(QWidget):
    def __init__(self, name, keys, bindIndex, parent):
        super().__init__()
        loadUi("lib/qtUI/keybind_list_element.ui", self)
        self.parent    = parent
        self.bindIndex = bindIndex

        # populate feilds
        self.buttonNameLabel.setText(name)
        self.currentBindingLabel.setText(self.determineBindingText(keys))

        # tell button to open dialog box
        self.configureBindingToolButton.clicked.connect(self.emitDialogOpenSignal)

    def determineBindingText(self, keys):
        if "button +0" in keys:
            return "Do Nothing"
        else:
            return keys

    def emitDialogOpenSignal(self):
        self.parent.showDialogButtonClicked.emit(self.bindIndex)

    def test(self):
        print(self.bindIndex)

    def setInfoRef(self, ref):
        self.infoRef = ref

class KeybindList(QWidget):
    showDialogButtonClicked = pyqtSignal(int)

    def __init__(self, parent):
        super(KeybindList, self).__init__(parent)

        self.parent = parent

        self.items    = []
        self.elements = [] #List containing KeybindListElements
        self.layout   = QVBoxLayout()
        self.setLayout(self.layout)

    def setItems(self, items):
        self.items = items

    def _resetElements(self):
        for element in self.elements:
            element.deleteLater()
            
        self.elements = [] # Reset element list
        for i in self.items:
            newElement = KeybindListElement(name = "Button {}".format(i["id"]),
                                            keys = i["value"],
                                            bindIndex=self.items.index(i),
                                            parent = self)
            newElement.setInfoRef(self.parent.tabInfo)
            self.elements.append(newElement)

    def _renderElements(self):
        for element in self.elements:
            self.layout.addWidget(element)
        self.layout.addStretch()

    def _clearSelf(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def notifyDataSetChanged(self):
        self._clearSelf()
        self._resetElements()
        self._renderElements()
