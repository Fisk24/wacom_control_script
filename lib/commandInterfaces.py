import re
from pyudev     import Context, Devices
from subprocess import Popen, PIPE

try:
    from lib.util      import *
except ModuleNotFoundError:
    from util      import *

# TODO create command interface class for xinput and xrandr

class Device():

    def __init__(self, name, id, type, node, udev):
        self.name = name # Device name according to xsetwacom
        self.id   = id   # Device id   according to xsetwacom
        self.type = type # Device type according to xsetwacom
        self.node = node # Device node according to xinput
        self.udev = udev # udev Device Object from pyudev

        self.interface = Xsetwacom()

    def __str__(self):
        return "Device(Name: {}, Id: {} Type: {})".format(self.name, self.id, self.type)

    def getUdev(self, prop):
        return self.udev.properties.get(prop)

    def getProp(self, prop, s=False):
        if s:
            return self.interface.getProp(self.name, prop, s=s)
        else:
            return self.interface.getProp(self.name, prop)

    def getButton(self, number):
        return self.interface.getButton(self.name, number)

    def setProp(self, prop, value):
        self.interface.setProp(self.name, prop, value)

    def setButton(self, number, value):
        self.interface.setButton(self.name, number, value)

class CommandInterface():
    def checkOutput(self, command, shell=False):
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)
        output = proc.communicate()
        return output

class Xsetwacom(CommandInterface):

    def _xsetwacom(self, *args, **kwargs):
        # Execute xsetwacom command with arguments passed as *args
        if args:
            command = ["xsetwacom"] + list(args)
            #print(command)
            output = self.checkOutput(command)
            return output[0].decode('utf-8').strip('\n').strip()
            '''
            if output[1] == b'':
                return output[0].decode('utf-8').strip('\n').strip()
            else:
                # If command execution fails, raise ValueError to tell me why.
                raise ValueError(output[1].decode('utf-8').strip('\n'))
            '''
        else:
            # If no arguments are passed, return no information
            return None

    def setProp(self, name, prop, value):
        self._xsetwacom('set', name, prop, str(value))

    def setButton(self, name, number, value):
        self._xsetwacom("set", name, "button", str(number), str(value))

    def getProp(self, name, prop, s=False):
        if s:
            return self._xsetwacom('-s', 'get', name, str(prop))
        else:
            return self._xsetwacom('get', name, str(prop))

    def getButton(self, name, number):
        return self._xsetwacom("get", name, "button", str(number))

    def getDevices(self):
        # Return a list of device objects.
        # These objects can be interacted with to get or change settings directly
        try:
            devices = {}
            deviceList = self._xsetwacom('list', 'devices').splitlines()
            for line in deviceList:
                deviceName  = " ".join(line.split()[:-4])                        # Isolate the part of Line that contains the device name
                deviceID    = re.search(r"id: [0-9]*", line).group().split()[-1] # Isolate the part of Line that contains the device ID
                deviceType  = line.split()[-1]
                                                   # Isolate the part of Line that contains the device type
                node = xinput.getDeviceNode(deviceName)
                udev = Devices.from_name(Context(), 'input', node.split('/')[-1])

                devices[deviceType] = Device(name=deviceName, id=deviceID, type=deviceType, node=node, udev=udev)

            if devices != {}:
                return devices
            else:
                return None

        except Exception as e:
            print(e)

    def getDeviceId(self, deviceType):
        devices = self.getDevices()
        if devices != None:
            return devices[deviceType].id

class Xinput(CommandInterface):

    def _xinput(self, *args, **kwargs):
        # Execute xinput command with arguments passed as *args
        if args:
            command = ["xinput"] + list(args)
            #print(command)
            output = self.checkOutput(command)
            if output[1] == b'':
                return output[0].decode('utf-8')
            else:
                # If command execution fails, raise ValueError to tell me why.
                raise ValueError(output[1].decode('utf-8').strip('\n'))
        else:
            # If no arguments are passed, return no information
            return None

    def getButtonStates(self, id):
        # WARNING: This totally fails if the tablet is set to a non default binding
        # Set all key binds to default first?
        try:
            cmdRaw = self._xinput('--query-state', id)
            states = []
            for line in cmdRaw.splitlines():
                match = re.search(r"button\[[0-9]*\]=.*", line)
                if match != None:
                    stateString = match.group().split('=')[-1]
                    if stateString == "up":
                        states.append(0)
                    else:
                        states.append(1)

            return states
        except ValueError:
            return []

    def getDeviceNode(self, name):
        props = self._xinput('list-props', name)
        nodeMatch = re.search("Device Node.*\n", props)
        if nodeMatch != None:
            return nodeMatch.group().split()[-1].strip("\"")
        else:
            return None

class XrandR(CommandInterface):
    def _xrandr(self, *args, **kwargs):
        # Execute xrandr command with arguments passed as *args
        if args:
            command = ["xrandr"] + list(args)
            #print(command)
            output = self.checkOutput(command)
            if output[1] == b'':
                return output[0].decode('utf-8')
            else:
                # If command execution fails, raise ValueError to tell me why.
                raise ValueError(cmdout[1].decode('utf-8').strip('\n'))
        else:
            # If no arguments are passed, return no information
            return None

    def getActiveMonitorList(self):
        activeMonitors = []
        activeMonitorsString = self._xrandr("--listactivemonitors")
        print(activeMonitorsString)
        for line in activeMonitorsString.splitlines():
            if not ("Monitors:" in line):
                activeMonitors.append(line.split()[-1])
        return activeMonitors

xsetwacom = Xsetwacom()
xinput    = Xinput()
xrandr    = XrandR()

if __name__ == '__main__':
    #### Button States Test ####
    bindings = []
    devices = xsetwacom.getDevices()
    # Clear bindings first, or we cant read them
    # Just give the user fair warning, since the use case for this involves rebinding all the buttons...
    for i in range(1, 10):
        bindings.append(devices['PAD'].getButton(i))
        devices['PAD'].setButton(i, "") # <-- reset buttons by setting them to an empty string

    padId = xsetwacom.getDeviceId('PAD')
    currentButtonStates = xinput.getButtonStates(padId)
    print(currentButtonStates)
    #devices["PAD"].setButton(1, "button +1")
    #print(devices["PAD"].getButton(1))
    '''
    for i in devices["PAD"].udev.properties:
        print(i, "-", devices["PAD"].udev.properties[i])
    '''
