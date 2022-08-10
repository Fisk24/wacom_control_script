#! /usr/bin/python3

"""
INTRODUCTION:
        This script edits the settings for wacom tablets and saves them

        This is a graphical application.

settings used: https://wiki.archlinux.org/index.php/Wacom_Tablet#Permanent_configuration
access method: http://www.tutorialspoint.com/python/os_access.htm

Locally Stored Tablet Info: /usr/share/libwacom


Big TODO: Make the application obey dark theme settings

read up on Qt Style Sheets (based on CSS with some things that aren't supported.) https://doc.qt.io/Qt-5/stylesheet-syntax.html

Then take a look at the QPalette class.
It allows doing complete pallet (i.e. black, light, purple) changes and load them from files: https://doc.qt.io/qt-5/qpalette.html

One my last project we used both. QSS for over size and choice of fonts, QPalette to offer light and dark modes.
There is an example that let's you change the pallette and save it, but I can't find it right now. It is worth checking out.

"""
import sys
from PyQt6.QtGui        import QIcon
from PyQt6.QtWidgets    import *
from PyQt6.QtCore       import QTimer, pyqtSignal

from lib                import logger
from lib.daemon         import Daemon
from lib.configUiWidget import ConfigUI
from lib.trayApplet     import TrayApplet

class Main(QMainWindow):

    def __init__(self, app, parent=None):
        super(Main, self).__init__(parent)

        '''
        SUPER IMPORTANT!
        We need to make it so that the user MAY NOT OPEN more than one instance of this application
        '''

        #### WIDGETS ####
        self.app           = app
        self.parent        = parent
        self.centralWidget = QWidget(self)
        self.mainLayout    = QVBoxLayout(self)
        self.configUI      = ConfigUI(self)
        self.trayApplet    = TrayApplet(self)
        self.noTabletLabel = QLabel(self)
        self.updateTrayAppletProfileList()
        self.determineInitialUIState()

        #### BUILD ####
        self.app.setQuitOnLastWindowClosed(False)
        self.centralWidget.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.configUI)
        self.mainLayout.addWidget(self.noTabletLabel)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setCentralWidget(self.centralWidget)

        #### POPULATE ####
        # TODO: Create a nice and pretty ui to display this text.
        self.noTabletLabel.setText("No tablet detected! Please connect a tablet...")

        #### MANIPULATE SIGNALS ####
        self.configUI.startDaemon.emit()
        self.configUI.resetUI.connect(self.toggleUILater)
        self.configUI.profileListChanged.connect(self.updateTrayAppletProfileList)

        self.trayApplet.menuActionShowWindow.triggered.connect(self.handleShowMainWindow)
        self.trayApplet.menuActionToggleTouch.triggered.connect(self.handleToggleTouch)
        self.trayApplet.menuActionQuitApp.triggered.connect(self.handleQuit)
        self.trayApplet.profileSelectionChangedSignal.connect(self.handleProfileSelectionChanged)

    def handleQuit(self):
        self.configUI.stopDaemon.emit()
        self.app.quit()

    def handleShowMainWindow(self):
        self.show()

    def handleHideMainWindow(self):
        self.hide()

    def handleToggleTouch(self):
        # This kind of shit makes accessing settings really difficult. Consider making settings staticly accessable
        state = self.configUI.settings.get('enable_touch')
        if state == "on":
            self.configUI.settings.set('enable_touch', 'off')
            print("Toggle Touch: was:", state, "- now: off")

        else:
            self.configUI.settings.set('enable_touch', 'on')
            print("Toggle Touch: was:", state, "- now: on")

        self.configUI.settings.applyTouch()
        self.configUI.populateTouchEnabled()

    def handleProfileSelectionChanged(self, profileIndex):
        self.configUI.doSwitchActiveProfile(profileIndex)

    def closeEvent(self, event):
        self.handleHideMainWindow()

    def updateTrayAppletProfileList(self):
        if self.configUI.buttons != None:
            self.trayApplet.setProfileMenuItems(self.configUI.buttons.getProfiles())

    def setNoTabletUiModel(self):
        self.configUI.hide()
        self.configUI.profileListChanged.emit()
        self.trayApplet.tabletPresent.emit(0)
        self.noTabletLabel.show()
        self.setWindowTitle("No tablet is detected! - Tablet Config")

    def setTabletPresentUiModel(self):
        self.configUI.show()
        self.configUI.populateFeilds()
        self.configUI.profileListChanged.emit()
        self.trayApplet.tabletPresent.emit(1)
        self.noTabletLabel.hide()
        genericName = self.configUI.tabInfo.getGenericName()
        modelName   = self.configUI.tabInfo.getModel()
        self.setWindowTitle("Device: {} {} - Tablet Config".format(genericName, modelName))

    def determineInitialUIState(self):
        if self.configUI.tabInfo.isTabletPresent():
            self.setTabletPresentUiModel()
            self.configUI.populateFeilds()
            self.configUI.applyAllSettings()
        else:
            self.setNoTabletUiModel()

    def toggleUILater(self, isTabletPresent):
        print("Scheduling UI Reset...")
        QTimer.singleShot(1000, lambda: self.toggleUI(isTabletPresent))

    def toggleUI(self, isTabletPresent):

        print("Resetting UI")
        print("Tablet Present:", isTabletPresent)
        if isTabletPresent:
            self.configUI.reloadDataObjects() # Reload all data objects to reflect the new tablet
            self.configUI.applyAllSettings()  # Re-apply all device settings, specific to the new tablet
            self.setTabletPresentUiModel()
        else:
            self.configUI.deloadDataObjects()
            self.setNoTabletUiModel()

if __name__ == "__main__":
    try:
        logger.tear()
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon.fromTheme('input-tablet'))
        win = Main(app)
        win.show()
        sys.exit(app.exec())
    except:
        logger.report()
