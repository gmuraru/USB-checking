#!/usr/bin/env python3

import pyudev


if __name__ == '__main__':
	
	context = pyudev.Context()
	monitor = pyudev.Monitor.from_netlink(context)
	monitor.filter_by(subsystem='usb')
	monitor.start()

	for device in monitor:
		print device
		print "WTF"
