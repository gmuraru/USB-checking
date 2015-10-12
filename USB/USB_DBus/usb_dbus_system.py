#! /usr/bin/env python

# DBus to turn USB on or off (by unbinding the driver)
# The System D-bus

import dbus
import dbus.service
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from usb_inhibit import USB_inhibit

class USB_Service_Blocker(dbus.service.Object):
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
    def start(self):
        print("Start monitoring Dbus system message")
        if not self.inhibitor_work:
	    self.usb_monitor.start()
            self.inhibitor_work = True
                

    @dbus.service.method(dbus_interface='org.gnome.USBBlocker.inhibit')
    def stop(self):
        print("Stop monitoring Dbus system message")
        if self.inhibitor_work:
	    self.usb_monitor.stop()
	    self.inhibitor_work = False

    @dbus.service.method(dbus_interface='org.gnome.USBBlocker.device',
                                                in_signature='ss', out_signature='b')
    def enable_device(self, bus_id, dev_id):
        print (bus_id)
        print (dev_id)

        import time; time.sleep(0.03)    
        return self.usb_monitor.bind_driver(bus_id, dev_id)


DBusGMainLoop(set_as_default=True)
dbus_service = USB_Service_Blocker()

mainloop = GLib.MainLoop()

try:
    mainloop.run()
except KeyboardInterrupt:
    print("\nThe MainLoop will close...")
    mainloop.quit()
