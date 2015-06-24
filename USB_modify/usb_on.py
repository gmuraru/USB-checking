#! /usr/bin/python333

import sys

def usb_enable(bus_id):
	try:
		with open("/sys/bus/usb/drivers/usb/bind", "w") as bind_device:
			bind_device.write(bus_id)
	except IOError:
		print("Check if the bus_id exists")

if __name__ == "__main__":
	try:
		usb = sys.argv[1]
		usb_enable(usb)
	except IndexError:
		print("Must have as argument the usb port!")
