import time
from threading import Thread

try:
    from lib.commandInterfaces import xinput, xsetwacom
except ImportError:
    from commandInterfaces import xinput, xsetwacom

# xinput --query-state {id/name} <-- for potential tablet button listener

class TabletButtonListener():
    def __init__(self):
        self._doContinue       = False
        self._workerThread     = Thread(target=self._doListen, daemon=True)
        self._listenerCallback = self._dummy

    def _dummy(self, *args, **kwargs):
        pass

    def setListenerCallback(self, callback):
        self._listenerCallback = callback

    def _doListen(self):
        # Listen for tablet keys
        # Parse into list of keys [0, 0, 0, 0, 0] <- pressed keys = 1
        # Pass keys list to callback
        padId = xsetwacom.getDevices()["PAD"].id
        while self._doContinue:
            currentKeyStates = xinput.getButtonStates(padId)
            buttonNumber = 1
            for state in currentKeyStates:
                if state == 1:
                    self._listenerCallback(buttonNumber)
                    break

                buttonNumber += 1

    def start(self):
        self._doContinue = True
        self._workerThread.start()

    def stop(self):
        self._doContinue = False

class Listener():
    def __init__(self):
        self._workerThread = Thread(target=self.workerExecutor, daemon=True)

    def workerExecutor(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass
