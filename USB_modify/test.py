#! /usr/bin/env/python3
from gi.repository import Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

class MyDBUSService(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.me.test', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/me/test')

		@dbus.service.method('org.me.test')
		def hello(self):
			#Gtk.main_quit()   # Terminate after running. Daemons don't use this.
			return "Hello,World!"

DBusGMainLoop(set_as_default=True)
myservice = MyDBUSService()
Gtk.main()
