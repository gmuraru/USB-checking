#! /usr/bin/env python

# DBus to turn USB on or off (by unbinding the driver)
# The Session D-bus

import dbus
import dbus.service
from gi.repository import GLib
import read_device
from dbus.mainloop.glib import DBusGMainLoop
from os.path import expanduser
import json

try:
    from pyudev import Context, Monitor, MonitorObserver

except ImportError: 
    sys.exit("Check if you have installed the module pyudev:\n "\
			"Installation: pip install pyudev")


class USB_Session_Blocker(dbus.service.Object):

    # Create context
    context = Context()

    # Create monitor
    monitor = Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb', device_type='usb_device')

    def __init__(self):

        try:
            with open(expanduser("~") + '/.local/share/trusted_devices', 'rt') as f_in:
                try:
                    self.trusted_devices = json.load(f_in)
                except ValueError:
                    self.trusted_devices = []
        
        except IOError:
            self.trusted_devices = []

        self.usb_blocker = dbus.SystemBus().get_object('org.gnome.USBBlocker', '/org/gnome/USBBlocker')
        self.notifier = dbus.SessionBus().get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
        self.observer = None
        self.number_notifications = {}

        self.allowed_devices = []
	bus_name = dbus.service.BusName('org.gnome.USBInhibit', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/gnome/USBInhibit')


    @dbus.service.method(dbus_interface='org.gnome.USBInhibit', \
						in_signature='', out_signature='b')
    def get_status(self):
        return self.usb_blocker.get_dbus_method('get_status', 'org.gnome.USBBlocker.inhibit')()

	
    @dbus.service.method(dbus_interface='org.gnome.USBInhibit')
    def start_inhibit(self):
        self.notification = self.notifier.get_dbus_method('Notify', \
                    'org.freedesktop.Notifications')

        self.observer = MonitorObserver(self.monitor, callback = self.device_detected,
		                                      name='monitor-usb-session') 
    
        self.notifier.connect_to_signal('ActionInvoked', self.action_new_device)
        

        self.observer.daemon = True
        self.observer.start()

        print("Start monitoring Dbus session message")
        self.usb_blocker.get_dbus_method('start', 'org.gnome.USBBlocker.inhibit')()
                
    
    def action_new_device(self, id, action):
        if id in self.number_notifications:
            if action == "Allow":
                print "Allowed"
                bus_id, dev_id = self.number_notifications.pop(id)
                if self.usb_blocker.get_dbus_method('enable_device', 'org.gnome.USBBlocker.device')(bus_id, dev_id):
                    self.trusted_devices.append(dev_id)
                    self.write_trusted_devices()

                print (bus_id)
                print (dev_id)

            # If the action is Block then the device must remain blocked
            if action == "Block":
                print "Blocked"
        

    @dbus.service.method(dbus_interface='org.gnome.USBInhibit')
    def stop_inhibit(self):
        print("Stop monitoring Dbus session message")

        if self.observer != None:
           self.observer.stop()
           self.usb_blocker.get_dbus_method('stop', 'org.gnome.USBBlocker.inhibit')()


    @dbus.service.method(dbus_interface='org.gnome.USBInhibit', \
                                            in_signature='n', out_signature='')
    def add_nonblock_device(self, bDeviceClass):
        print ("Add device with the bDeviceClass code " + str(bDeviceClass))
        self.allowed_devices.append(bDeviceClass)

    
    @dbus.service.method(dbus_interface='org.gnome.USBInhibit', \
                                            in_signature='n', out_signature='')
    def remove_nonblock_device(self, bDeviceClass):
        print ("Remove device with the bDeviceClass code " + str(bDeviceClass))
        if bDeviceClass in self.allowed_devices:
            self.allowed_devices.remove(bDeviceClass)


    @dbus.service.method(dbus_interface='org.gnome.USBInhibit', \
                                            in_signature='', out_signature='s')
    def show_nonblock_devices(self):
        return str(self.allowed_devices)


    def device_detected(self, device):
        import usb.core

        bus_id = device.sys_name
        action = device.action

        # Check only new connected devices to see if they are on an allowed list
        if action == 'add':
            print ("Device attached")
     
            devnum = int(device.attributes.get("devnum"))
            busnum = int(device.attributes.get("busnum"))
       
            dev = usb.core.find(address=devnum, bus=busnum)

            # Get the device unique id
            dev_id = read_device.get_descriptors(dev)

            if dev_id in self.trusted_devices:
                self.usb_blocker.get_dbus_method('enable_device', 'org.gnome.USBBlocker.device')(bus_id, dev_id)
                return

            if read_device.find_device(dev, list(usb.core.find(find_all = True,
                custom_match = read_device.custom_search(self.allowed_devices)))):

                print ("Device found on the non blocking list -- session")
                if self.usb_blocker.get_dbus_method('enable_device', 'org.gnome.USBBlocker.device')(bus_id, dev_id):
                    self.trusted_devices.append(dev_id)
                    self.write_trusted_devices()

                return


            id_notification = self.notification("USB-inhibitor",
                                                "0",
                                                "",
                                                "Unknown device connected",
                                                "An unknown device has been connected to the system. Do you want to allow it to connect?",
                                                ["Allow", "Connect", "Block", "Block"],
                                                {},
                                                5)

            self.number_notifications[id_notification] = [bus_id, dev_id]

            



    def write_trusted_devices(self):
        with open(expanduser("~") + '/.local/share/trusted_devices', 'wt') as f_out:
            json.dump(self.trusted_devices, f_out)

        
DBusGMainLoop(set_as_default=True)
dbus_service = USB_Session_Blocker()

mainloop = GLib.MainLoop()

try:
    mainloop.run()
except KeyboardInterrupt:
    print("\nThe MainLoop will close...")
    mainloop.quit()
