#! /usr/bin/env python3

# DBus to turn USB on or off (by unbinding the driver)

import dbus
import dbus.service
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from usb_inhibit import USB_inhibit

class USB_DBus(dbus.service.Object):
	monitor_work = False

	def __init__(self):
		self.usb_inhibit = USB_inhibit(True)
		bus_name = dbus.service.BusName('org.gnome.USBBlocker', bus=dbus.SystemBus())
		dbus.service.Object.__init__(self, bus_name, '/org/gnome/USBBlocker')

	@dbus.service.method(dbus_interface = 'org.gnome.USBBlocker.monitor', in_signature = '', out_signature='b')
	def get_status(self):
		return self.monitor_work
		

	@dbus.service.method(dbus_interface = 'org.gnome.USBBlocker.monitor')
	def start_monitor(self):
		print("Start monitoring dbus message")
		if not self.monitor_work:
			self.usb_inhibit.start()
			self.monitor_work = True

	@dbus.service.method(dbus_interface = 'org.gnome.USBBlocker.monitor')
	def stop_monitor(self):
		print("Stop monitoring dbus message")
		if self.monitor_work:
			self.monitor_work = False
			self.usb_inhibit.stop()

DBusGMainLoop(set_as_default=True)
dbus_service = USB_DBus()

mainloop = GLib.MainLoop()

try:
	mainloop.run()
except KeyboardInterrupt:
	print("\nThe MainLoop will close...")
	mainloop.quit()
