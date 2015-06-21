#!/usr/bin/python
import dbus
import gobject

class DeviceAddedListener:
	def __init__(self):
		self.bus = dbus.SystemBus()
		self.hal_manager_obj = self.bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
		self.hal_manager = dbus.Interface(self.hal_manager_obj,"org.freedesktop.Hal.Manager")

		self.hal_manager.connect_to_signal("DeviceAdded", self._filter) 

	def _filter(self, udi):
		device_obj = self.bus.get_object ("org.freedesktop.Hal", udi)
		device = dbus.Interface(device_obj, "org.freedesktop.Hal.Device")
		self.do_something(device)

	def do_something(self, device):
		try:

			usb = device.GetProperty("storage.bus")
			info = device.GetProperty("info.product")
			removable = device.GetProperty("storage.removable")
			print info
		  
		except:
		  	pass#blah blah


if __name__ == '__main__':
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)
	loop = gobject.MainLoop()
	DeviceAddedListener()
	loop.run()
