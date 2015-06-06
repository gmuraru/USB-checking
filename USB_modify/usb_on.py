#! /usr/bin/python

import sys

if __name__ == "__main__":

	try:
		usb = sys.argv[1]
	except IndexError:
		print "Must have as argument the usb port!"

	with open("/sys/bus/usb/drivers/usb/bind", "w") as unbind_device:
		unbind_device.write(usb)
