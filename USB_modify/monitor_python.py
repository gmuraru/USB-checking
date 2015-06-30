#!/usr/bin/env python  

import dbus
import glib
from dbus.mainloop.glib import DBusGMainLoop  
from usb_inhibit import USB_inhibit

		
usb_inhibit = USB_inhibit(True)

def notificationScreen(bus, message):
	if message.get_member() != "ActiveChanged":
		return

	args = message.get_args_list()

	# Check if the screen is locked or unlocked
	if args[0] == True:
		print ("Screen Locked")
		usb_inhibit.start()
	else:
		print ("Screen Unlocked")
		usb_inhibit.stop()

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string("type='signal',interface='org.gnome.ScreenSaver'")
bus.add_message_filter(notificationScreen)

mainloop = glib.MainLoop()
mainloop.run()
