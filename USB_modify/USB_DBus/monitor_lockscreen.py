#!/usr/bin/env python3 

import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop  
from usb_inhibit import USB_inhibit

		
usb_inhibit = USB_inhibit(True)

bus2 = dbus.SystemBus()
usb_service = bus2.get_object('org.me.usb', '/org/me/usb')

def notificationScreen(bus, message):
	print(message)
	if message.get_member() != "ActiveChanged":
		return


	args = message.get_args_list()

	# Check if the screen is locked or unlocked
	print (args)

	if args[0] == True:
		print("Screen Locked")
		usb_service.get_dbus_method('start_monitor', 'org.me.usb')()
	else:
		print("Screen Unlocked")
		usb_service.get_dbus_method('stop_monitor', 'org.me.usb')()

DBusGMainLoop(set_as_default=True)


bus = dbus.SessionBus()
bus.add_match_string("type='signal', interface='org.gnome.ScreenSaver'")
bus.add_message_filter(notificationScreen)

mainloop = GLib.MainLoop()

try:
	mainloop.run()
except KeyboardInterrupt:
	print("\nThe MainLoop will close...")
	mainloop.quit()
