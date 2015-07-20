#!/usr/bin/env python3 

import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop  

		
bus2 = dbus.SystemBus()
usb_service_proxy = bus2.get_object('org.gnome.USBBlocker', '/org/gnome/USBBlocker')

def notificationScreen(bus, message):
	print(message)
	if message.get_member() != "ActiveChanged":
		return


	args = message.get_args_list()

	# Check if the screen is locked or unlocked
	print (args)

	if args[0] == True:
		print("Screen Locked")
		usb_service.get_dbus_method('start_monitor', 'org.gnome.USBBlocker.monitor')()
	else:
		print("Screen Unlocked")
		usb_service.get_dbus_method('stop_monitor', 'org.gnome.USBBlocker.monitor')()

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
