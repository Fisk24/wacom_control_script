import os

from PyQt6.QtGui     import QIcon, QAction
from PyQt6.QtCore    import pyqtSignal
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu

class ProfileSelectorAction(QAction):
    profileSelected = pyqtSignal(int)
    def __init__(self, icon, name, index, parent):
        super(ProfileSelectorAction, self).__init__(icon, name, parent)
        self.profileIndex = index
        self.triggered.connect(self.emitProfileSelected)

    def emitProfileSelected(self):
        self.profileSelected.emit(self.profileIndex)

class TrayApplet(QSystemTrayIcon):
    #showWindowSignal              = pyqtSignal()
    #toggleTouchSignal             = pyqtSignal()
    #quitApplicationSignal         = pyqtSignal()
    tabletPresent                 = pyqtSignal(int)
    profileSelectionChangedSignal = pyqtSignal(int)

    def __init__(self, parent):
        super(TrayApplet, self).__init__(parent)
        self._menu    = QMenu()
        self._icon    = QIcon.fromTheme('input-tablet')
        self._submenu = QMenu("Choose Profile", parent)
        self._submenu.setIcon(QIcon.fromTheme('view-more'))

        self.menuActionShowWindow  = QAction(QIcon.fromTheme('document-edit'), "Edit Settings")
        self.menuActionToggleTouch = QAction(QIcon.fromTheme('object-select'), "Toggle Touch (On)")
        self.menuActionQuitApp     = QAction(QIcon.fromTheme('process-stop'), "Quit")

        self.tabletPresent.connect(self.handleTabletPresence)

        self.setIcon(self._icon)
        self.setContextMenu(self._menu)
        self.setVisible(True)

    def buildMenuTabletPresent(self):
        self._menu.clear()
        self._menu.addAction(self.menuActionShowWindow)
        self._menu.addMenu(self._submenu)
        self._menu.addAction(self.menuActionToggleTouch)
        self._menu.addSeparator()
        self._menu.addAction(self.menuActionQuitApp)

    def buildMenuTabletAbsent(self):
        self._menu.clear()
        self._menu.addAction(self.menuActionShowWindow)
        self._menu.addSeparator()
        self._menu.addAction(self.menuActionQuitApp)

    def handleTabletPresence(self, presence):
        if presence == 1: # Tablet Present
            self.buildMenuTabletPresent()
        elif presence == 0: # Tablet Absent
            self.buildMenuTabletAbsent()

    def getIconFromString(self, iconString):
        if os.path.isfile(iconString):
            return QIcon(iconString)
        else:
            return QIcon.fromTheme(iconString, QIcon.fromTheme('input-tablet'))

    def setProfileMenuItems(self, profiles):
        self._submenu.clear()
        for profileIndex in range(0, len(profiles)):
            profile = profiles[profileIndex]
            #print(profile)
            name = profile['name']
            icon = self.getIconFromString(profile['icon'])
            subMenuItem = ProfileSelectorAction(icon, name, profileIndex, self)
            subMenuItem.profileSelected.connect(self.profileSelectionChangedSignal.emit)
            self._submenu.addAction(subMenuItem)
















#
