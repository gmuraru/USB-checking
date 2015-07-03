#! /usr/bin/env python3

# DBus to turn USB on or off (by unbinding the driver)

from gi.repository import Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from usb_inhibit import USB_inhibit

class USB_DBus(dbus.service.Object):
	def __init__(self):
		self.usb_inhibit = USB_inhibit(True)
		bus_name = dbus.service.BusName('org.me.usb', bus=dbus.SystemBus())
		dbus.service.Object.__init__(self, bus_name, '/org/me/usb')


	@dbus.service.method('org.me.usb')
	def start_monitor(self):
		print("Start monitoring dbus message")
		self.usb_inhibit.start()


	@dbus.service.method('org.me.usb')
	def stop_monitor(self):
		print("Stop monitoring dbus message")
		self.usb_inhibit.stop()

DBusGMainLoop(set_as_default=True)
dbus_service = USB_DBus()
Gtk.main() 
