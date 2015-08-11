#! /usr/bin/python3

import sys

def usb_disable(bus_id):
    try:
	with open("/sys/bus/usb/drivers/usb/unbind", "w") as unbind_device:
		unbind_device.write(bus_id)
    except IOError:
	print ("Check if the bus_id exists")
		
if __name__ == "__main__":
    try:
	usb = sys.argv[1]
	usb_disable(usb)
    except IndexError:
	print ("Must have as argument the usb port!")
