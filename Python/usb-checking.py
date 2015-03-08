#! /usr/bin/python

import usb


class USB_ports():
	buss_more = []
	def __init__(self):
		self.buss_more = usb.busses()
	
	def show_devices(self):
		for bus in self.buss_more:
			print bus
			devices = bus.devices
			for dev in devices:
				print "Device:", dev.filename
				print "  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor)
				print "  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct)

a = USB_ports()
a.show_devices()

