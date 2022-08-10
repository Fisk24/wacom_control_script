## System Imports ##
import os, sys, time

## Qt Classes ##
from PyQt6.QtWidgets    import *
from PyQt6.QtGui        import QIcon, QPixmap, QPainter
from PyQt6.QtCore       import QSize, QTimer, pyqtSignal
from PyQt6.QtSvg        import QSvgRenderer
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6              import uic

## Local Imports ##
from lib.tabinfo           import TabletInfo
from lib.settings          import SettingsManager, SETTINGSDIR
from lib.buttons           import ButtonManager
from lib.daemon            import Daemon
from lib.commandInterfaces import xrandr

## Custom Widgets ##
from lib.keybindList          import KeybindList, KeybindListElement
from lib.setKeyBindDialog     import SetKeyBindDialog
from lib.quickSetDialog       import QuickSetDialog
from lib.warningResetBindings import WarningResetBindingsDialog
from lib.addProfileDialog     import AddProfileDialog

class ConfigUI(QWidget):
    #### DEFINE SIGNALS ####
    startDaemon = pyqtSignal()
    stopDaemon  = pyqtSignal()
    resetUI     = pyqtSignal(bool) # Signal Returns: True if tablet is present, False if tablet is not present

    profileListChanged  = pyqtSignal()
    earlyDismisalSignal = pyqtSignal()


    def __init__(self, parent=None):
        super(ConfigUI, self).__init__(parent)
        #### LOAD UI FILES ####
        self.ui = uic.loadUi("lib/qtUI/configUI.ui", self)

        #### VARIABLES ####
        self.parent   = parent
        self.daemon   = Daemon()
        self.tabInfo  = TabletInfo()
        self.settings = self.doLoadSettings()
        self.buttons  = self.doLoadActiveButtonProfile()
        self.monitors = xrandr.getActiveMonitorList()

        #### Widgets ####
        self.keybindList = KeybindList(self)

        #### Connect Signals ####
        self.startDaemon.connect(self.setupDaemon)
        self.stopDaemon.connect(self.daemon.stop)
        self.modeComboBox.currentIndexChanged.connect(self.doChangeTrackingMode)
        self.orientationComboBox.currentIndexChanged.connect(self.doChangeOrientation)
        self.mapToMonitorComboBox.currentIndexChanged.connect(self.doChangeMonitorMapping)
        self.enableTouchCheckBox.stateChanged.connect(self.doChangeTouchEnabled)
        self.stylusPrimaryComboBox.currentIndexChanged.connect(self.doChangeStylusPrimary)
        self.stylusSecondaryComboBox.currentIndexChanged.connect(self.doChangeStylusSecondary)
        self.keybindList.showDialogButtonClicked.connect(self.doShowKeybindDialogByIndex)
        self.addProfileToolButton.clicked.connect(self.doShowAddProfileDialog)
        self.editProfileToolButton.clicked.connect(self.doShowEditProfileDialog)
        self.removeProfileToolButton.clicked.connect(self.doShowRemoveProfileDialog)
        self.initiateQuickSetPushButton.clicked.connect(self.doShowQuickSetDialog)
        self.resetBindingsPushButton.clicked.connect(self.doShowResetBindingsDialog)
        self.selectProfileComboBox.currentIndexChanged.connect(self.doSwitchActiveProfile)

        self.ui.viewTabletButtonsLabel.linkActivated.connect(self.testMethod)

    #### Data Handling ####
    def deloadDataObjects(self):
        self.tabInfo  = None
        self.settings = None
        self.buttons  = None
        self.monitors = None

    def reloadDataObjects(self):
        self.tabInfo  = TabletInfo()
        self.settings = self.doLoadSettings()
        self.buttons  = self.doLoadActiveButtonProfile()
        self.monitors = xrandr.getActiveMonitorList()

    def applyAllSettings(self):
        self.settings.applyAll()
        self.buttons.applyButtons(suppressOutput=True)

    def setupDaemon(self):

        self.daemon.setAddHandler(self.devicePlugged)
        self.daemon.setRemoveHandler(self.deviceUnplugged)
        self.daemon.start()

    def deviceUnplugged(self, device):
        # Fired when any device is unplugged/removed via USB
        try:
            idPath = device.properties["ID_PATH"]
            idTabletPad = device.properties["ID_INPUT_TABLET_PAD"]
            if (idTabletPad == "1") and (idPath == self.tabInfo.getIdPath()):
                # Was the device im processing a tablet pad
                # And if so, was it MY tablet pad
                print("Tablet device at {} was removed".format(idPath))
                # Shut down all window interaction here
                self.earlyDismisalSignal.emit()
                self.resetUI.emit(False)

        except KeyError:
            pass

    def devicePlugged(self, device):
        # Fired when any device is plugged in/added via USB
        try:
            '''
            for i in device.properties:
                print(i, device.properties[i])
            '''
            idSerial    = device.properties["ID_SERIAL"].replace("_", " ")
            idTabletPad = device.properties["ID_INPUT_TABLET_PAD"]
            if idTabletPad == "1":
                print("Found new tablet device:", idSerial)
                self.resetUI.emit(True)

        except KeyError:
            pass

    #### Determiners #####
    def determineStylusComboBoxIndex(self, setting):
        # Based on the loaded settings, determine what the index of the combo box should be
        if setting == "button +0":
            return 0
        elif setting == "button +2":
            return 1
        elif setting == "button +3":
            return 2
        elif setting == "button +8":
            return 3
        elif setting == "button +9":
            return 4
        else:
            return 0

    def determineStylusComboBoxSetting(self, index):
        if index == 0:
            return "button +0"
        elif index == 1:
            return "button +2"
        elif index == 2:
            return "button +3"
        elif index == 3:
            return "button +8"
        elif index == 4:
            return "button +9"

    #### Do'ers ####

    def doLoadSettings(self):
        if not self.tabInfo.isTabletPresent():
            return None

        name = self.tabInfo.getGenericName()
        model = self.tabInfo.getModel()
        # Assertain a good directory name for per model settings
        perDeviceName = "{} {}".format(name, model).replace(" ", "_")
        perDeviceDir  = os.path.join(SETTINGSDIR, perDeviceName)
        perDeviceSettings = os.path.join(perDeviceDir, "settings.json")
        # Create settings object.
        settings = SettingsManager(perDeviceSettings)
        # Load settings if they exist, or generate new ones
        if os.path.isfile(perDeviceSettings):
            print("Loaded per device settings from:", perDeviceSettings)
            settings.load()
        else:
            print("Generating new per device settings at:", perDeviceSettings)
            settings.genDefaultSettings()

        return settings

    def doLoadActiveButtonProfile(self):
        if not self.tabInfo.isTabletPresent():
            return None

        perDeviceDir = self.settings.perDeviceDir
        # Given that we know where per device settings are saved
        # Assemble the ButtonProfiles directory and Last Active Profile Uri
        profilesDir  = os.path.join(perDeviceDir, "ButtonProfiles") # <-- The location where button profiles are saved
        lastActiveProfile = self.settings.get('active_profile') # <-- Last loaded profile json file
        lastActiveProfileUri = os.path.join(profilesDir, lastActiveProfile) # <-- The exact location of the last loaded profile json file

        # Load profile data if it exists, or generate a new default one
        if os.path.isfile(lastActiveProfileUri):
            print("Loaded button profile settings from last known active profile:", lastActiveProfileUri)
            buttons = ButtonManager(profilesDir, activeProfile=lastActiveProfile)
            buttons.load()

        else:
            print("Could not find last active button profile:", lastActiveProfile)
            print("Loaded default button profile...")
            self.settings.set('active_profile', 'default.json')
            buttons = ButtonManager(profilesDir)
            if os.path.isfile(os.path.join(profilesDir, "default.json")):
                buttons.load()

            else:
                buttons.genDefaultProfile()
                buttons.load()

        buttons.loadProfileList()

        return buttons

    def doShowKeybindDialogByIndex(self, bindIndex):
        bindDict = self.buttons.getButton(bindIndex)

        if bindDict != None:
            dialog = SetKeyBindDialog(bindDict, self)
            exitStatus = dialog.exec()
            if exitStatus:
                self.buttons.setButton(bindIndex, dialog.newBinding['value'])
                self.buttons.applyButton(bindIndex)
                self.keybindList.setItems(self.buttons.getButtons())
                self.keybindList.notifyDataSetChanged()
            return exitStatus

        else:
            return 0

    def doShowKeybindDialogByDict(self, bindDict):
        bindIndex = self.buttons.getButtons().index(bindDict)

        if bindDict != None:
            dialog = SetKeyBindDialog(bindDict, self)
            exitStatus = dialog.exec()
            if exitStatus:
                self.buttons.setButton(bindIndex, dialog.newBinding['value'])
                self.buttons.applyButton(bindIndex)
                self.keybindList.setItems(self.buttons.getButtons())
                self.keybindList.notifyDataSetChanged()
                return 1 # <- dialog accepted
            else:
                if dialog.dismissedEarly:
                    return 2 # <- dialog dismissed early, with out user input

        else:
            return 0 # <- dialog cancled

    def doShowAddProfileDialog(self):
        dialog = AddProfileDialog(self.buttons.getProfiles(), parent=self)
        if dialog.exec():
            newProfileInfo = dialog.finalValues
            self.buttons.genNewProfile(newProfileInfo)

            newProfileIndex = self.buttons.getProfileIndexByName(newProfileInfo['name'])
            self.doSwitchActiveProfile(newProfileIndex)
            self.profileListChanged.emit()

    def doShowEditProfileDialog(self):
        # Mostly the same as doShowAddProfileDialog but in edit mode
        dialog = AddProfileDialog(self.buttons.getProfiles(), editProfileData=self.buttons.activeProfileData, parent=self)
        if dialog.exec():
            self.buttons.setName(dialog.finalValues['name'])
            self.buttons.setIcon(dialog.finalValues['icon'])
            self.buttons.save()
            self.buttons.loadProfileList()
            self.populateButtonProfileComboBox()
            self.profileListChanged.emit()

    def doShowRemoveProfileDialog(self):
        reply = QMessageBox.warning(self,
            "Warning",
            "Are you sure you want to delete: {}".format(self.buttons.getName()),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            os.remove(self.buttons.activeProfile)
            self.buttons.loadProfileList()
            self.doSwitchActiveProfile(0)
            self.profileListChanged.emit()

    def doShowQuickSetDialog(self):
        warning = WarningResetBindingsDialog(self)
        if warning.exec():
            # Continue Only if the user clicked OK
            self.doResetButtons()

            notDone = True
            while notDone:
                # Loop until the user is finished
                quickSetDialog = QuickSetDialog(self)
                if quickSetDialog.exec(): # <- show quick bind dialog
                    buttonId = quickSetDialog.buttonId
                    button   = self.buttons.getButtonById(buttonId)
                    #print("quick set wants to modify key id", buttonId)
                    #print("This should be it:", button)
                    exitCode = self.doShowKeybindDialogByDict(button)
                    if exitCode == 2:
                        notDone = False

                else:
                    print("quick set has been cancled!")
                    notDone = False
                    return

    def doShowResetBindingsDialog(self):

        reply = QMessageBox.warning(self,
            "Warning",
            "Your bindings will be irreversably reset. Are you sure?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel)

        if reply == QMessageBox.StandardButton.Ok:
            self.doResetButtons()

    def doResetButtons(self):
        self.buttons.resetButtons()
        self.keybindList.setItems(self.buttons.getButtons())
        self.keybindList.notifyDataSetChanged()

    def doSwitchActiveProfile(self, profileIndex):
        self.buttons.switchProfile(profileIndex)
        newProfileFileName = self.buttons.getProfileFileByIndex(profileIndex)
        print("Switching active profile to:", newProfileFileName)
        self.settings.set('active_profile', newProfileFileName)
        self.settings.save()
        self.populateButtonProfileComboBox()
        self.populateKeybindScrollableArea()
        self.buttons.applyButtons(suppressOutput=True)
        # TODO: Create notification informing user of the change

    def doChangeTrackingMode(self, index):
        if index == 0:
            self.settings.set('tracking_mode', 'Absolute')
        elif index == 1:
            self.settings.set('tracking_mode', 'Relative')

        self.settings.applyTrackingMode()

    def doChangeOrientation(self, index):
        if index == 0:
            # Set to left handed
            self.settings.set('orientation', 'half')
        elif index == 1:
            # Set to right handed
            self.settings.set('orientation', 'none')

        self.settings.applyOrientation()

    def doChangeMonitorMapping(self, index):
        if index == 0:
            self.settings.set('monitor_output', 'desktop')
        else:
            newMonitor = self.monitors[index-1]
            #print(newMonitor)
            self.settings.set('monitor_output', newMonitor)

        self.settings.applyMonitorMapping()

    def doChangeTouchEnabled(self, state):
        if state:
            self.settings.set('enable_touch', 'on')
        else:
            self.settings.set('enable_touch', 'off')

        self.settings.applyTouch()

    def doChangeStylusPrimary(self, index):
        newSetting = self.determineStylusComboBoxSetting(index)
        self.settings.set('stylus_primary', newSetting)
        self.settings.applyStylusPrimary()

    def doChangeStylusSecondary(self, index):
        newSetting = self.determineStylusComboBoxSetting(index)
        self.settings.set('stylus_secondary', newSetting)
        self.settings.applyStylusSecondary()

    #### POPULATORS ####
    def populateFeilds(self):

        self.populateTabletMode()
        self.populateHandedness()
        self.populateMonitorMapping()
        self.populateTouchEnabled()
        self.populateStylus()
        self.populateButtonProfileComboBox()
        self.populateKeybindScrollableArea()
        self.populateInfoTab()

    def populateTabletMode(self):
        self.modeComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        mode = self.settings.get('tracking_mode')
        #print(mode)
        if mode == "Absolute":
            self.modeComboBox.setCurrentIndex(0)
        elif mode == "Relative":
            self.modeComboBox.setCurrentIndex(1)
        # Unblock signals
        self.modeComboBox.blockSignals(False)

    def populateHandedness(self):
        self.orientationComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        orientation = self.settings.get('orientation')
        #print(orientation)
        if orientation == "none":
            #print("righty")
            self.orientationComboBox.setCurrentIndex(1)
        elif orientation == "half":
            #print("lefty")
            self.orientationComboBox.setCurrentIndex(0)

        # Unblock signals
        self.orientationComboBox.blockSignals(False)

    def populateMonitorMapping(self):
        # Populate the combo box based on the currently active displays in xrandr
        self.mapToMonitorComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        for monitor in self.monitors:
            self.mapToMonitorComboBox.addItem(monitor)

        currentMonitor = self.settings.get('monitor_output')
        if currentMonitor == "desktop":
            self.mapToMonitorComboBox.setCurrentIndex(0)
        elif currentMonitor in self.monitors:
            newComboBoxIndex = self.monitors.index(currentMonitor) + 1
            #print(newComboBoxIndex)
            self.mapToMonitorComboBox.setCurrentIndex(newComboBoxIndex)

        # Unblock signals
        self.mapToMonitorComboBox.blockSignals(False)

    def populateTouchEnabled(self):
        self.enableTouchCheckBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        enableTouch = self.settings.get('enable_touch').strip()
        if enableTouch == 'on':
            self.enableTouchCheckBox.setChecked(True)
        else:
            self.enableTouchCheckBox.setChecked(False)

        # Unblock signals
        self.enableTouchCheckBox.blockSignals(False)

    def populateStylus(self):
        self.stylusPrimaryComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        self.stylusSecondaryComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        primary   = self.settings.get('stylus_primary').strip()
        secondary = self.settings.get('stylus_secondary').strip()
        tertiary  = self.settings.get('stylus_tertiary').strip()
        self.stylusPrimaryComboBox.setCurrentIndex(self.determineStylusComboBoxIndex(primary))
        self.stylusSecondaryComboBox.setCurrentIndex(self.determineStylusComboBoxIndex(secondary))
        #self.stylusTertiaryComboBox.setCurrentIndex(self.determineStylusComboBoxIndex(tertiary))
        # ^ Currently not used. Consider detecting stylus with real eraser
        # Unblock signals
        self.stylusPrimaryComboBox.blockSignals(False)
        self.stylusSecondaryComboBox.blockSignals(False)

    def populateButtonProfileComboBox(self):
        # Load every profile that exists for this device
        # Assemble a list of Profile Names, and their corrosponding File Names
        self.selectProfileComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        self.selectProfileComboBox.clear()
        profileList = self.buttons.getProfiles()
        for index in range(0, len(profileList)):
            profile = profileList[index]
            self.selectProfileComboBox.addItem(profile['name'])
            if os.path.isfile(profile['icon']):
                icon = QIcon(profile['icon'])
            else:
                icon = QIcon.fromTheme(profile['icon'])

            self.selectProfileComboBox.setItemIcon(index, icon)

            filename = os.path.basename(profile['uri'])
            if filename == self.settings.get('active_profile'):
                activeProfileIndex = self.buttons.getProfileIndexByName(profile['name'])
                self.selectProfileComboBox.setCurrentIndex(activeProfileIndex)
                # Disable remove button if default profile is selected
                if activeProfileIndex == 0:
                    self.removeProfileToolButton.setEnabled(False)
                    self.editProfileToolButton.setEnabled(False)
                else:
                    self.removeProfileToolButton.setDisabled(False)
                    self.editProfileToolButton.setDisabled(False)

        # Unblock signals
        self.selectProfileComboBox.blockSignals(False)

    def populateKeybindScrollableArea(self):
        self.ui.keybindScrollArea.setWidget(self.keybindList)
        self.keybindList.setItems(self.buttons.getButtons())
        self.keybindList.notifyDataSetChanged()

    def populateInfoTab(self):
        self.tabletDataTextBrowser.setText(self.tabInfo.getInfoString())

    # ==========================================================================

    def multiplyQSize(self, sizeObj, scale):
        self.dump(sizeObj)
        height = sizeObj.height() * scale
        width  = sizeObj.width() * scale
        return QSize(width, height)

    def setTabletButtonLayoutGraphic(self):
        #### Create SVG and Insert ####
        #self.svgPlaceholder.setPixmap(QPixmap("/usr/share/libwacom/layouts/bamboo-16fg-s-t.svg"))
        testSvg = "/usr/share/libwacom/layouts/bamboo-16fg-s-t.svg"
        svgRenderer = QSvgRenderer(testSvg)
        svgWidget = QSvgWidget(testSvg)
        svgWidget.setFixedSize(self.multiplyQSize(svgRenderer.defaultSize(), 3))
        self.ui.deviceButtonsVerticalLayout.addWidget(svgWidget)
        svgWidget.show()

    def testMethod(self):
        print("Test!!!")
