#! /usr/bin/python3

import re, os, sys, time, subprocess
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *

class Window(QWidget):
	def __init__(self, controller):
		super(Window, self).__init__()
		self.controller = controller
	### SYSTRAY MENU ###
		### DEFINE ###
		self.contextMenu  = QMenu(self)
		self.actionToggle = self.contextMenu.addAction("Toggle")
		self.actionQuit   = self.contextMenu.addAction("Quit")
		### CONNECT ###
		self.actionToggle.triggered.connect(self.controller.changeState)
		self.actionQuit.triggered.connect(sys.exit)
		### KEYSTROKE ###
		#self.actionToggle.setShortcut(QKeySequence("Shift+Alt+T"))
	### SYSTRAY ###
		self.tray = QSystemTrayIcon()
		self.tray.setIcon(QIcon("touch_on.ico"))
		self.tray.setContextMenu(self.contextMenu)
		#self.tray.activated.connect()
		self.tray.show()

class Main():
	def __init__(self):
		self.window = Window(self)
		self.model  = "Something or Other"
		self.id     = ""
		self.detectTabletInfo()

		self.changeState()

	def changeState(self):
		self.resp = subprocess.Popen(["xsetwacom", "--get", "20", "touch"], stdout = subprocess.PIPE)
		self.out, self.err = self.resp.communicate()
		print(self.out)
		if self.out == b'on\n':
			os.system("xsetwacom --set 20 touch off")
			print("TURNED TO OFF")
			self.window.tray.showMessage("Touch OFF", "The touch setting for your \""+self.model+"\" was disabled!", msecs=3000)
			#self.window.tray.setIcon(QIcon("touch_off.ico"))
			
		elif self.out == b'off\n':
			os.system("xsetwacom --set 20 touch on")
			print("TURNED TO ON")
			self.window.tray.showMessage("Touch ON", "The touch setting for your \""+self.model+"\" was enabled!", msecs=3000)
			#self.window.tray.setIcon(QIcon("touch_on.ico"))
			
		else:
			self.window.tray.showMessage("ERROR", "The tablet may not be plugged in.", msecs=3000)
			print("ERROR")

	def detectTabletInfo(self):
		self.window.tray.showMessage("Tablet Detected!", "Model: " + self.model, msecs=3000)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	main = Main()
	sys.exit(app.exec_())

"""
#!/usr/bin/python

# kermit-internal-pytouch 0|1

import re, sys, subprocess
resp = subprocess.Popen(['xinput', '-list'], stdout = subprocess.PIPE)
out, err = resp.communicate()
WacomLine = re.compile('Wacom')
FingerLine = re.compile('Finger')
idExpr=re.compile('id=(?P<number>\d+)')
for line in out.split("\n"):
    if WacomLine.search(line) and FingerLine.search(line):
        identifier = idExpr.search(line)
        num = identifier.group("number")
        subprocess.call(['xinput', '-set-prop', num, "Device Enabled", sys.argv[1]])
resp = subprocess.Popen(['xinput', '-list'], stdout = subprocess.PIPE)
out, err = resp.communicate()
print(out)
"""
