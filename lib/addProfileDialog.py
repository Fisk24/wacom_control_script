import os

from lib.util import legalize

from PyQt6.uic       import loadUi
from PyQt6.QtGui     import QIcon
from PyQt6.QtCore    import QSize
from PyQt6.QtWidgets import QDialog, QFileDialog

class AddProfileDialog(QDialog):
    def __init__(self, profileList, editProfileData=None, parent=None):
        super(AddProfileDialog, self).__init__(parent)
        loadUi("lib/qtUI/newProfileDialog.ui", self)

        self.profileList     = profileList
        self.editProfileData = editProfileData

        self.finalValues = {}

        self.profileNameLineEdit.textChanged.connect(self.validateProfileName)
        self.profileIconLineEdit.textChanged.connect(self.updateIconSelectionPreview)
        self.browseIconsToolButton.clicked.connect(self.doShowBrowseIconsDialog)
        self.createProfilePushButton.clicked.connect(self.finishForm)
        self.cancelPushButton.clicked.connect(self.reject)

        self.setupWarnings()
        self.populateFeilds()

    def setupWarnings(self):
        icon = QIcon.fromTheme('dialog-error')
        pixmap = icon.pixmap(QSize(16, 16))
        self.warningIconLabel.setPixmap(pixmap)
        self.warningIconLabel.hide()
        self.warningMessageLabel.hide()

    #### POPULATORS ####
    def populateFeilds(self):
        if self.editProfileData == None:
            self.populateProfileSelection()
        else:
            self.populateName()
            self.populateIcon()
            self.populateEditMode()

    def populateEditMode(self):
        self.setWindowTitle("Edit Profile")
        self.profileSelectionComboBox.hide()
        self.profileSelectionLabel.hide()
        self.createProfilePushButton.setText("Save Profile")
        self.resize(QSize(483, 160))

    def populateName(self):
        self.profileNameLineEdit.setText(self.editProfileData['name'])

    def populateIcon(self):
        self.profileIconLineEdit.setText(self.editProfileData['icon'])

    def populateProfileSelection(self):
        self.profileSelectionComboBox.blockSignals(True) # <- Block signal output while we prepair the ui element
        for profile in self.profileList:
            self.profileSelectionComboBox.addItem(profile['name'])

        # Unblock signals
        self.profileSelectionComboBox.blockSignals(False)

    #### UPDATERS ####
    def updateIconSelectionPreview(self, iconString):
        if os.path.isfile(iconString):
            if iconString[-4:] in [".bmp", ".gif", ".jpg", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".svg", ".xbm", ".xpm"]:
                icon = QIcon(iconString)
            else:
                icon = QIcon.fromTheme('dialog-error')
        else:
            icon = QIcon.fromTheme(iconString, QIcon.fromTheme('dialog-error'))

        self.iconPreviewLabel.setPixmap(icon.pixmap(QSize(16, 16)))

    #### Do'ers ####
    def doShowBrowseIconsDialog(self):
        #BMP,GIF,JPG,JPEG,PNG,PBM,PGM,PPM,XBM and XPM
        iconFileName = QFileDialog.getOpenFileName(self, "Select Icon", "/usr/share/icons/", "Icons (*.bmp *.gif *.jpg *.jpeg *.png *.pbm *.pgm *.ppm *.svg *.xbm *.xpm)")

        if iconFileName:
            self.profileIconLineEdit.setText(iconFileName[0])

    #### Validators ####
    def finishForm(self):
        if self.validateProfileName():
            self.finalValues = {
            'name': self.profileNameLineEdit.text(),
            'icon': self.profileIconLineEdit.text(),
            'inherits': self.profileSelectionComboBox.currentIndex()
            }
            self.accept()

    def validateProfileName(self, name=None):
        # Profile name must also be an exceptable file name so no illegal characters are allowed
        # Profile name must not be empty (after striping spaces, and legalizing the string)
        # Profile name cannot be the same as an existing profile, that is, we cannot have duplicate profile names
        valid = True

        if name == None:
            name = self.profileNameLineEdit.text()

        cleanName = legalize(name.strip())
        if cleanName == "":
            self.warningMessageLabel.setText("Profile Name must contain at least one letter or number")
            valid = False

        if len(cleanName) > 20:
            self.warningMessageLabel.setText("Profile Name must be between 1 - 20 characters")
            valid = False

        for profile in self.profileList:
            if cleanName.lower() == profile["name"].lower():
                if self.editProfileData != None:
                    if name.lower() == self.editProfileData['name'].lower():
                        valid = True
                        break
                self.warningMessageLabel.setText("Duplicate profile names are not allowed.")
                valid = False

        if valid:
            self.warningMessageLabel.hide()
            self.warningIconLabel.hide()
        else:
            self.warningMessageLabel.show()
            self.warningIconLabel.show()

        return valid

    def validateIconName(self):
        # Icon can be either "System Theme Icon" or ".png, .svg File Icon"
        # Short of checking that the "File Icon" is in fact a file that exists, there isnt much we can validate here
        # because "System Theme Icon" is also an option "File Exists" type validation will fail
        pass
