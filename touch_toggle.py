#! /usr/bin/python3

import re, os, sys, time, subprocess
from gi.repository import Notify

class Main():
	def __init__(self):
		self.delay  = 0.8
		self.model  = "Something or Other"
		self.id     = ""
		self.notify = Notify.Notification.new("", "", "")
		Notify.init("touch_toggle")
		self.notify.set_timeout(1)

		self.detectTabletInfo()
		self.changeState()
		#self.notify.close()

	def changeState(self):
		self.resp = subprocess.Popen(["xsetwacom", "--get", self.id, "touch"], stdout = subprocess.PIPE)
		self.out, self.err = self.resp.communicate()
		#print(self.out)
		if self.out == b'on\n':
			os.system("xsetwacom --set "+self.id+" touch off")
			print("TURNED TO OFF")
			self.notify.update("Touch OFF", "The touch setting for your \""+self.model+"\" was disabled!", "/home/fisk/Projects/python/wacom_control_script/touch_off.ico")
			self.notify.show()
			
		elif self.out == b'off\n':
			os.system("xsetwacom --set "+str(self.id)+" touch on")
			print("TURNED TO ON")
			self.notify.update("Touch ON", "The touch setting for your \""+self.model+"\" was enabled!", "/home/fisk/Projects/python/wacom_control_script/touch_on.ico")
			self.notify.show()
			#("Touch ON", "The touch setting for your \""+self.model+"\" was enabled!", msecs=3000)
			
		else:
			self.notify.update("ERROR", "The tablet may not be plugged in.")
			self.notify.show()
			self.delay = 5
			#("ERROR", "The tablet may not be plugged in.", msecs=3000)
			print("ERROR")

	def detectTabletInfo(self):
		self.resp = subprocess.Popen(["xsetwacom", "--list", "devices"], stdout = subprocess.PIPE)
		self.out, self.err = self.resp.communicate()
		x = self.out.decode("utf-8")
		print(x)
		for i in x.split("\n"):
			if re.search("TOUCH", i):
				x = re.search(r"id: (?P<number>\d+)", i)
				print("ID is: ",x.group("number"))
				self.id = x.group("number")
				self.model = i

if __name__ == "__main__":
	#app = QApplication(sys.argv)
	main = Main()
	time.sleep(main.delay)
	main.notify.close()
	#sys.exit(app.exec_())

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

'''
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
'''
