#! /usr/bin/env python

#                                                                             
#    Copyright 2015 George-Cristian Muraru <murarugeorgec@gmail.com>            
#    Copyright 2015 Tobias Mueller <muelli@cryptobitch.de>                      
#                                                                               
#    This file is part of USB Inhibitor.                                        
#                                                                               
#    USB Inhibitor is free software: you can redistribute it and/or modify      
#    it under the terms of the GNU General Public License as published by       
#    the Free Software Foundation, either version 3 of the License, or          
#    (at your option) any later version.                                        
#                                                                               
#    USB Inhibitor and the afferent extension is distributed in the hope that it
#    will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              
#    GNU General Public License for more details.                               
#                                                                               
#    You should have received a copy of the GNU General Public License          
#    along with USB Inhibitor.  If not, see <http://www.gnu.org/licenses/>.     
# 


import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop  

		

'''
    The first ideea -> later make a gnome-shell-extension
    This program has the role to block the USB ports when the screen is locked
'''

def notificationScreen(bus, message):
    if message.get_member() != "ActiveChanged":
    	return

    args = message.get_args_list()

    # Check if the screen is locked or unlocked
    print (args[0])

    if args[0] == True:
	print("Screen Locked")
	usb_service_proxy.get_dbus_method('start_monitor', 'org.gnome.USBBlocker.inhibit')()
    
    else:
	print("Screen Unlocked")
	usb_service_proxy.get_dbus_method('stop_monitor', 'org.gnome.USBBlocker.inhibit')()


if __name__ == "__main__":
    bus_system = dbus.SystemBus()
    usb_service_proxy = bus_system.get_object('org.gnome.USBBlocker', '/org/gnome/USBBlocker')

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
