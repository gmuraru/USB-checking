#! /usr/bin/env python

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
