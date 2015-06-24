#! /usr/bin/python3

# DBus to turn USB on or off (by unbinding the driver)

from gi.repository import Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import usb_on
import usb_off

class USB_DBus(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.me.usb', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/me/usb')

	@dbus.service.method('org.me.usb')
	def usb_no(self, bus_id):
		usb_off.usb_disable(bus_id)

	@dbus.service.method('org.me.usb')
	def usb_yes(self, bus_id):
		usb_on.usb_enable(bus_id)

DBusGMainLoop(set_as_default=True)
dbus_service = USB_DBus()
Gtk.main() 
