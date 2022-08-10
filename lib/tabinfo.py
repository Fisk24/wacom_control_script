import re, os
try:
    from lib.util              import *
    from lib.commandInterfaces import xsetwacom
except ModuleNotFoundError:
    from util                  import *
    from commandInterfaces     import xsetwacom

from pyudev import Context, Device

from subprocess import Popen, PIPE
from copy       import deepcopy

'''
    For reference, this is what the mouse button numbers mean

    0 = ignore tablet button event
    1 = left buttonRight Click
    2 = middle button (pressing the scroll wheel)
    3 = right button
    4 = turn scroll wheel up
    5 = turn scroll wheel down
    6 = push scroll wheel left
    7 = push scroll wheel right
    8 = 4th button (aka browser backward button)
    9 = 5th button (aka browser forward button)

    Really useful commands:

    udevadm
    xinput
    xsetwacom

'''

class TabletInfo():
    def __init__(self):
        '''
        This class is designed to be informational. It should not be in charge of changing or maintaining settings

        As well, create a class dedicated to managing the buttons. If we are to implement button presets, this will be manditory.
        All button operations should be handled there and not in TabletInfo.
        '''

        self.libwacom = "/usr/share/libwacom/"
        self.devices  = xsetwacom.getDevices()

        self.tabletMetaFile = None
        self.tabletLayoutFile = None
        self.findTabletFileAndLayout()

        self.metadata = None
        self.loadTabletMetadata()

        #VVV These just straight up dont belong here
        #self.tabletKeybinds = []
        #self.stylusKeybinds = []
        #self.getTabletButtons()
        #self.getStylusButtons()

    def getVendor(self):
        # Return vendor according to the PAD device
        if self.devices != None:
            return self.devices["PAD"].udev.properties.get("ID_VENDOR").replace("_", " ")

    def getModel(self):
        # Return model according to the PAD device
        if self.devices != None:
            return self.devices["PAD"].udev.properties.get("ID_MODEL").replace("_", " ")

    def getGenericName(self):
        return self.metadata.device.name

    def getIdPath(self):
        if self.devices != None:
            return self.devices["PAD"].getUdev("ID_PATH")

    def getDevMatch(self):
        # Return vendor according to the PAD device
        if self.devices != None:
            idVendorId = self.devices["PAD"].udev.properties.get("ID_VENDOR_ID")
            idModelId  = self.devices["PAD"].udev.properties.get("ID_MODEL_ID")
            idBus      = self.devices["PAD"].udev.properties.get("ID_BUS")
            devmatch = "{}:{}:{}".format(idBus, idVendorId, idModelId)
            return devmatch

    def getInfoString(self):
        if self.devices != None:
            info = "---------------------\n"
            info += "Vendor: {}\n".format(self.getVendor())
            info += "Model: {}\n".format(self.getModel())
            info += "--------------------\n"
            info += "Generic Name: {}\n".format(self.metadata.device.name)
            info += "Generic Class: {}\n".format(self.metadata.device._class)
            info += "--------------------\n"
            info += "Device Node (PAD): {}\n".format(self.devices["PAD"].node)
            info += "Device Match (PAD): {}\n".format(self.getDevMatch())
            info += "Metadata File: {}\n".format(self.tabletMetaFile)
            info += "Layout Svg File: {}\n".format(self.tabletLayoutFile)
            info += "--------------------\n"
            info += "Has Stylus: {}\n".format(self.metadata.features.stylus)
            info += "Has Touch: {}\n".format(self.metadata.features.touch)
            info += "Reversable: {}\n".format(self.metadata.features.reversible)

            info += "--------------------\n"
            info += "Xinput IDs: \n"
            for deviceType in self.devices.keys():
                info += " id: {} belongs to device {}\n".format(self.devices[deviceType].id, self.devices[deviceType].name)

            info += "--------------------\n"
            
            return info

        else:
            return "No device"

    def findTabletFileAndLayout(self):
        for file in os.listdir(self.libwacom):
            fullfile = os.path.join(self.libwacom, file)
            if not os.path.isdir(fullfile):
                with open(fullfile, "r") as tablet:
                    contents = tablet.readlines()
                    for line in contents:
                        if "DeviceMatch=" in line:
                            devMatchFromFile = line.strip("\n").split("=")[-1]
                            if devMatchFromFile == self.getDevMatch():
                                self.tabletMetaFile   = os.path.join(self.libwacom, file)
                                layout = file.split(".")[0]+".svg"
                                self.tabletLayoutFile = os.path.join(self.libwacom, "layout/"+layout)

    def loadTabletMetadata(self):
        # Load info from libwacom .tablet file

        if self.tabletMetaFile == None:
            return None

        self.metadata = TabletMetadata()
        with open(self.tabletMetaFile, 'r') as metaFile:
            lines = metaFile.readlines()
            currentCatagoryKey = ""
            for line in lines:
                catagoryMatch = re.search(r"\[.*\]", line)
                if catagoryMatch != None:
                    key = catagoryMatch.group().strip("[").strip("]").lower()
                    currentCatagoryKey = key
                    # init metadata catagory
                    self.metadata[key] = TabletMetadata()

                itemMatch = re.search(r".*=.*", line)
                if itemMatch != None:
                    # currentCatagoryKey -> itemMatch.group()
                    keyValuePair = itemMatch.group().split("=")
                    key = keyValuePair[0].lower()
                    value = keyValuePair[1]
                    if key == "class":
                        key = "_class"
                    # init key value pair in catagory
                    self.metadata[currentCatagoryKey][key] = value

    def isTabletPresent(self):
        if not xsetwacom.getDevices():
            return False
        else:
            return True

class TabletMetadata(dict):
    # Implementation of dot accesable dict
    def __init__(self, *args, **kwargs):
        super(TabletMetadata, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __str__(self):
        infoString = ""
        for catagory in self:
            infoString += "[" + catagory + "]\n"
            for key in self[catagory]:
                infoString += key + " -> " + self[catagory][key] + "\n"
        return infoString

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(TabletMetadata, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(TabletMetadata, self).__delitem__(key)
        del self.__dict__[key]

if __name__ == "__main__":
    tabInfo = TabletInfo()
    print(tabInfo.isTabletPresent())
