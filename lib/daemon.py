from pyudev import Context, Monitor, MonitorObserver

from lib.util import dump

class Daemon():
    # Consideration:
    # If we made Daemon inherit QObject it could emit signals, instead of using standard callbacks
    def __init__(self):
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='input')
        self.observer = MonitorObserver(self.monitor, self.handleEvent)
        self.addHandler = self.dummy
        self.removeHandler = self.dummy

    def start(self):
        print("Starting Device Daemon...")
        self.observer.start()
        print("Device Daemon Started!")

    def stop(self):
        print("Stoping Device Daemon...")
        self.observer.stop()

    def setAddHandler(self, method):
        self.addHandler = method

    def setRemoveHandler(self, method):
        self.removeHandler = method

    def dummy(self, device):
        pass

    def handleEvent(self, action, device):
        if action == "add":
            self.addHandler(device)
        elif action == "remove":
            self.removeHandler(device)
