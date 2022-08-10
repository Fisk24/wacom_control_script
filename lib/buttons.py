import os, re, json

from pathlib import Path

try:
    from util              import legalize
    from commandInterfaces import xsetwacom
    from settings          import SETTINGSDIR
except ImportError:
    from lib.util              import legalize
    from lib.commandInterfaces import xsetwacom
    from lib.settings          import SETTINGSDIR

'''
ButtonManager:
    This class is responsable for managing and maintaining the button settings.
    Via this class we can apply all of our xsetwacom prefrences from a single
    method call. As well, we can save or load these preferences to and from a file.

    when the larger tablet configuration app starts:
    - load settings file
    - apply settings to xsetwacom
    - populate the ui with info from this class

    from that point forward any settings that get changed in the ui should:
    - make the appropriate changes to settings data
    - apply new setting to xsetwacom
    - save settings to file

    the profile settings should be saved immediatly when changes are made.

'''
BUTTONPROFILESDIR = os.path.join(SETTINGSDIR, "ButtonProfiles")

class ButtonManager():
    def __init__(self, profilesDir, activeProfile=None):
        self.profilesDir       = profilesDir
        self.activeProfile     = self.assembleProfileUri(activeProfile) # <- Currently active profile uri
        self.activeProfileData = {} # <- Currently active profile data, yet to be loaded
        self.profiles          = []
        self.devices           = xsetwacom.getDevices()

        os.makedirs(self.profilesDir, exist_ok=True)

    def __str__(self):
        printStr = "------------------------------------\n"
        printStr += "Buttons:\n"
        printStr += "\tDir : {}\n".format(self.profilesDir)
        printStr += "\tFile: {}\n".format(self.activeProfile)
        printStr += "------------------------------------\n"
        printStr += "Profile Name: {}\n".format(self.activeProfileData["name"])
        printStr += "Bindings:\n"
        for button in self.activeProfileData["buttons"]:
            printStr += "\t{}: \"{}\"\n".format(button["id"], button["value"])
        printStr += "------------------------------------\n"

        return printStr

    def applyButton(self, index, suppressOutput=False):

        if self.devices != None:
            id    = self.getButtons()[index]['id']
            value = self.getButtons()[index]['value']

            self.devices["PAD"].setButton(id, value) # <- tell xsetwacom to change the button binding

            correctedButtonString = self.devices["PAD"].getButton(id) # After you apply a setting in xsetwacom
                                                                      # the tool may correct it in order to sanitize it
                                                                      # Eg. +ctrl becomes +Control_L
                                                                      # Ideally, we want to display the sanitized settings
                                                                      # So we get the new keybinding again from Xsetwacom
                                                                      # and adjust our settings to match the sanitized version

            self.setButton(index, correctedButtonString) # <- adjust the setting to match xsetwacom's corrected/sanitized version
            if not suppressOutput:
                print("Tablet Button {}: set to value: {}".format(id, correctedButtonString))

            self.save()

    def applyButtons(self, suppressOutput=False):

        if (self.devices != None) and (self.activeProfileData != {}):
            buttons = self.getButtons()
            for button in buttons:
                if not suppressOutput:
                    print("Tablet Button {}: set to value: {}".format(button['id'], button['value']))

                self.devices["PAD"].setButton(button['id'], button['value'])
            self.save()

    def load(self):
        # Load active profile
        with open(self.activeProfile, 'r') as profileFile:
            jsonString = profileFile.read()
            self.activeProfileData = json.loads(jsonString)

    def loadProfileList(self):
        profileList = []
        for profile in os.listdir(self.profilesDir):
            uri = os.path.join(self.profilesDir, profile)
            if not os.path.isdir(uri):
                with open(uri, 'r') as proFile:
                    jString = proFile.read()
                    loadedProfile = json.loads(jString)
                    newProfile = {'name': loadedProfile['name'], 'icon': loadedProfile['icon'], 'uri': uri}
                    if loadedProfile['name'] == "Default":
                        profileList.insert(0, newProfile)

                    else:
                        profileList.append(newProfile)

        self.profiles = profileList

    def loadOtherProfileData(self, profileUri):
        # Load a profiles data and return it
        otherProfileData = {}
        with open(profileUri, 'r') as profileFile:
            jsonString = profileFile.read()
            otherProfileData = json.loads(jsonString)
        return otherProfileData

    def save(self):
        # Save active profile
        with open(self.activeProfile, 'w') as profileFile:
            jsonString = json.dumps(self.activeProfileData)
            profileFile.write(jsonString)

    def saveOtherProfileData(self, profileUri, profileData):
        # Save a profile other then the activly loaded one
        with open(profileUri, 'w') as profileFile:
            jsonString = json.dumps(profileData)
            profileFile.write(jsonString)

    def assembleProfileUri(self, activeProfile):
        if activeProfile == None:
            return os.path.join(self.profilesDir, "default.json")
        else:
            return os.path.join(self.profilesDir, activeProfile)

    def switchProfile(self, profileIndex):
        newActiveProfileMetaData = self.getProfiles()[profileIndex]
        self.activeProfile = newActiveProfileMetaData['uri']
        self.load()

    def getName(self):
        if self.activeProfileData != {}:
            return self.activeProfileData['name']

    def getButton(self, index):
        # Search for button containing id, return it.
        if self.getButtons() != []:
            try:
                return self.getButtons()[index]
            except IndexError:
                print("ButtonManager -> getButton: No button exists at index", index)
                return None

    def getButtons(self):
        if self.activeProfileData != {}:
            return self.activeProfileData['buttons']
        else:
            return []

    def getButtonById(self, id):
        for button in self.getButtons():
            if button['id'] == str(id):
                return button

        return None

    def getProfiles(self):
        return self.profiles

    def getProfileIndexByName(self, name):
        for index in range(0, len(self.getProfiles())):
            profile = self.getProfiles()[index]
            if profile['name'] == name:
                return index

    def getProfileFileByIndex(self, index):
        uri = self.getProfiles()[index]['uri']
        return os.path.basename(uri)

    def getProfileFileByName(self, name):
        for profile in self.getProfiles():
            if profile['name'] == name:
                return os.path.basename(profile['uri'])

    def setName(self, name):
        if self.activeProfileData != {}:
            self.activeProfileData['name'] = name

    def setIcon(self, icon):
        if self.activeProfileData != {}:
            self.activeProfileData['icon'] = icon

    def setButton(self, index, value):
        if self.getButtons() != []:
            self.activeProfileData['buttons'][index]['value'] = value

    def resetButtons(self):
        # Reset Buttons
        buttons = self.getButtons()
        for button in buttons:
            index = buttons.index(button)
            self.setButton(index, "")
            self.applyButton(index)
        self.save()
        print("Buttons Reset!")

    def parseTabletButtons(self):
        # Figure out how many button there are, given that the button count in the metadata is a fucking lier
        devices = xsetwacom.getDevices()
        buttons = []
        if devices != None:
            props = devices["PAD"].getProp('all', s=True)
            for line in props.splitlines():
                match = re.search("\"Button\" \"[\d+]\".*", line)
                if match != None:
                    buttonNum = match.group().split()[1].strip("\"")
                    buttonVal = " ".join(match.group().split()[2:]).strip("\"")
                    entry = {
                        'id'   : buttonNum,
                        'value': buttonVal
                    }
                    buttons.append(entry)

            return buttons
        else:
            return []

    def genDefaultProfile(self):
        #Get Settings
        self.activeProfileData = {
            'name'   : 'Default', # Profile Name visible in Profiles list
            'icon'   : 'none',    # Icon: Uri or System Theme Icon Name
            'buttons': self.parseTabletButtons()
        }
        self.save()

    def genNewProfile(self, newProfileInfo):
        #print(newProfileInfo)
        inheritedUri = self.getProfiles()[newProfileInfo['inherits']]['uri']
        inheritedData = self.loadOtherProfileData(inheritedUri)
        #print("Inherited Data", inheritedData)
        inheritedData['name'] = newProfileInfo['name']
        inheritedData['icon'] = newProfileInfo['icon']
        #print("New Data", inheritedData)
        newProfileFileName = legalize(newProfileInfo['name'].lower()) + ".json"
        newProfilePath     = os.path.join(self.profilesDir, newProfileFileName)
        self.saveOtherProfileData(newProfilePath, inheritedData)
        self.loadProfileList()

if __name__ == "__main__":
    buttons = ButtonManager(BUTTONPROFILESDIR)
    print(buttons.profilesDir)
    # buttons.genDefaultProfile()
    buttons.load()
    print(buttons.profiles)
