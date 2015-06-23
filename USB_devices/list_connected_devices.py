#! /usr/bin/python3

import pyudev
import json

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
	import pdb;pdb.set_trace()
	print('ID_Product: %s' %device.get('ID_PRODUCT'))
	print('Vendor: %s' % device.get('ID_VENDOR_FROM_DATABASE'))
	print('\n\n')
