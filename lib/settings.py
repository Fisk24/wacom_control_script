import os, json

from pathlib import Path

try:
    from commandInterfaces import xsetwacom
except ImportError:
    from lib.commandInterfaces import xsetwacom

'''
SettingsManager:
    This class is responsable for managing and maintaining the tablet settings.
    Via this class we can apply all of our xsetwacom prefrences from a single
    method call. As well, we can save or load these preferences from a file.

    when the larger tablet configuration app starts:
    - load settings file
    - apply settings to xsetwacom
    - populate the ui with info from this class

    from that point forward any settings that get changed in the ui should:
    - make the appropriate changes to settings data
    - apply new setting to xsetwacom
    - save settings to file

    the settings should be saved immediatly when changes are made.

'''
CONFIGDIR    = os.path.join(Path.home(), ".config")
SETTINGSDIR  = os.path.join(CONFIGDIR, "TabletCfg")
SETTINGSFILE = os.path.join(SETTINGSDIR, "settings.json")

class SettingsManager():
    def __init__(self, settingsFile):
        self.settingsFile = settingsFile
        self.perDeviceDir = os.path.dirname(self.settingsFile)
        self.devices      = xsetwacom.getDevices()
        self.data         = {}

        os.makedirs(os.path.dirname(self.settingsFile), exist_ok=True)

    def __str__(self):
        printStr = "------------------------------------\n"
        printStr += "Settings:\n"
        printStr += "\tfile: {}\n".format(self.settingsFile)
        printStr += "\tdir : {}\n".format(self.perDeviceDir)
        printStr += "------------------------------------\n"
        printStr += "Current Settings:\n"
        for setting in self.data.keys():
            printStr += "\t{} : {}\n".format(setting, self.data[setting])
        printStr += "------------------------------------\n"
        return printStr

    def load(self):
        with open(self.settingsFile, 'r') as settingsData:
            jsonString = settingsData.read()
            self.data = json.loads(jsonString)

    def save(self):
        with open(self.settingsFile, 'w') as settingsData:
            jsonString = json.dumps(self.data)
            settingsData.write(jsonString)

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value

    def applyAll(self):
        print("Applying all settings...")
        self.devices["TOUCH"].setProp('touch', self.data['enable_touch'])
        self.devices["STYLUS"].setProp('mode', self.data['tracking_mode'])
        self.devices["STYLUS"].setProp('rotate', self.data['orientation']) # IMPORTANT: rotation needs to be applied BEFORE mapToOutput
        self.devices["TOUCH"].setProp('rotate', self.data['orientation'])
        self.devices["STYLUS"].setProp('maptooutput', self.data['monitor_output'])
        self.devices["STYLUS"].setProp('pressurecurve', self.data['pressure_curve'])
        self.devices["STYLUS"].setButton(2, self.data['stylus_primary'])
        self.devices["STYLUS"].setButton(3, self.data['stylus_secondary'])
        self.devices["STYLUS"].setButton(8, self.data['stylus_tertiary'])
        self.save()

    def applyTouch(self):
        setting = self.get("enable_touch")
        print("Setting: \"Touch\" has been set to:", setting)
        self.devices["TOUCH"].setProp('touch', setting)
        self.save()

    def applyTrackingMode(self):
        setting = self.get("tracking_mode")
        print("Setting: \"Tracking Mode\" has been set to:", setting)
        self.devices["STYLUS"].setProp('mode', setting)
        self.save()

    def applyOrientation(self):
        # From "man xsetwacom" maptooutput:
        # When used with tablet rotation, the tablet must be rotated BEFORE it is mapped to the new screen.
        # Consideration:
        # Does this mean we need to re-apply the monitor mapping every time we apply orientation?
        setting = self.get("orientation")
        print("Setting: \"Orientation\" has been set to:", setting)
        self.devices["STYLUS"].setProp('rotate', setting)
        self.devices["TOUCH"].setProp('rotate', setting)
        self.save()

    def applyMonitorMapping(self):
        # From "man xsetwacom" maptooutput:
        # the command needs to be RE-RUN whenever the output configuration changes.
        # Consideration:
        # Add this monitor watching functionality to the Daemon. Can pyUdev do this? Or do i need to use XrandR?
        setting = self.get('monitor_output')
        print("Setting: \"MapToOutput\" has been set to:", setting)
        self.devices["STYLUS"].setProp('maptooutput', setting)
        self.save()

    def applyPressureCurve(self):
        setting = self.get("pressure_curve")
        print("Setting: \"Pressure Curve\" has been set to:", setting)
        self.devices["STYLUS"].setProp('pressurecurve', setting)
        self.save()

    def applyStylusPrimary(self):
        setting = self.get('stylus_primary')
        print("Setting: \"Stylus Primary\" has been set to:", setting)
        self.devices["STYLUS"].setButton(2, setting)
        self.save()

    def applyStylusSecondary(self):
        setting = self.get('stylus_secondary')
        print("Setting: \"Stylus Secondary\" has been set to:", setting)
        self.devices["STYLUS"].setButton(3, setting)
        self.save()

    def applyStylusTertiary(self):
        setting = self.get('stylus_tertiary')
        print("Setting: \"Stylus Tertiary\" has been set to:", setting)
        self.devices["STYLUS"].setButton(8, setting)
        self.save()

    def genDefaultSettings(self):
        #Get Settings
        self.data = {
            'enable_touch'    : self.devices["TOUCH"].getProp('touch'),
            'tracking_mode'   : self.devices["STYLUS"].getProp('mode'),
            'orientation'     : self.devices["STYLUS"].getProp('rotate'),
            'monitor_output'  : 'desktop',
            'active_profile'  : 'default.json',
            'pressure_curve'  : self.devices["STYLUS"].getProp('pressurecurve'),
            'stylus_primary'  : self.devices["STYLUS"].getButton(2),
            'stylus_secondary': self.devices["STYLUS"].getButton(3),
            'stylus_tertiary' : self.devices["STYLUS"].getButton(8)
        }
        self.save()

if __name__ == "__main__":
    settings = SettingsManager(SETTINGSFILE)
    settings.genDefaultSettings()
    settings.load()
    print(settings.data)
