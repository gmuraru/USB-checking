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


import sys

try:
    import usb.core

except ImportError:
    sys.exit("Check if you have installed the module pyusbga:\n "\
			"Installation: pip install pyusb --pre")

def usb_enable(bus_id):
    try:
	with open("/sys/bus/usb/devices/" + bus_id + "/busnum", "rt") as f_in:
	    busnum = int(f_in.read())

	with open("/sys/bus/usb/devices/" + bus_id + "/devnum", "rt") as f_in:
    	    devnum = int(f_in.read())
		
	device = usb.core.find(address=devnum, bus=busnum)
	device.set_configuration()

	for num_interface in range(device.get_active_configuration().bNumInterfaces):
	    if not device.is_kernel_driver_active(num_interface):
		device.attach_kernel_driver(num_interface)

    except IOError:
        print("Check if the bus_id exists")

if __name__ == "__main__":
    try:
	usb_id = sys.argv[1]
	usb_enable(usb_id)

    except IndexError:
	print("Must have as argument the usb port!")
