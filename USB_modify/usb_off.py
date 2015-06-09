#! /usr/bin/python

import sys

def usb_disable(bus_id):
	try:
		with open("/sys/bus/usb/drivers/usb/unbind", "w") as unbind_device:
			unbind_device.write(bus_id)
	except IOError:
		print "Check if the bus_id exists"
		exit(-2)
if __name__ == "__main__":
	try:
		usb = sys.argv[1]
	except IndexError:
		print "Must have as argument the usb port!"
		exit(-1)

	usb_disable(usb)
