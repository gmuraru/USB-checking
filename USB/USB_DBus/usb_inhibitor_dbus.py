#! /usr/bin/env python

# DBus to turn USB on or off (by unbinding the driver)

import dbus
import dbus.service
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from usb_inhibit import USB_inhibit

class USB_DBus(dbus.service.Object):
    inhibitor_work = False

    def __init__(self):
	self.usb_monitor = USB_inhibit(True)
	bus_name = dbus.service.BusName('org.gnome.USBBlocker', bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/org/gnome/USBBlocker')

    @dbus.service.method(dbus_interface='org.gnome.USBBlocker.inhibit', \
						in_signature='', out_signature='b')
    def get_status(self):
        return self.inhibitor_work
	
    @dbus.service.method(dbus_interface='org.gnome.USBBlocker.inhibit')
    def start_monitor(self):
        print("Start monitoring dbus message")
        if not self.inhibitor_work:
	    self.usb_monitor.start()
            self.inhibitor_work = True
                

    @dbus.service.method(dbus_interface='org.gnome.USBBlocker.inhibit')
    def stop_monitor(self):
        print("Stop monitoring dbus message")
        if self.inhibitor_work:
	    self.usb_monitor.stop()
	    self.inhibitor_work = False

DBusGMainLoop(set_as_default=True)
dbus_service = USB_DBus()

mainloop = GLib.MainLoop()

try:
    mainloop.run()
except KeyboardInterrupt:
    print("\nThe MainLoop will close...")
    mainloop.quit()
