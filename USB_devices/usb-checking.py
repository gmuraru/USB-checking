#! /usr/bin/python

import re
import subprocess
import json

# http://stackoverflow.com/questions/8110310/simple-way-to-query-connected-usb-devices-info-in-python
class USB_ports:	
	# Matching after this string
	device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<ID>\w+:\w+)\s(?P<name>.+)$", re.I)

	# The output of the command `lsusb` will be verified
	df = subprocess.check_output("lsusb", shell=True)
	
	# Start with no device
	connected_devices = []
	known_devices = []
	def get_connected_devices(self):
		for dev in self.df.split('\n'):
			if dev:
				dev_info = self.device_re.match(dev)
				if dev_info:
					dev_info_dic = dev_info.groupdict()
					dev_info_dic['device'] = '/dev/bus/usb/%s/%s' \
									% (dev_info_dic.pop('bus'), dev_info_dic.pop('device'))
					self.connected_devices.append(dev_info_dic)
		

#	def get_known_devices(self):
		

	# Show all connected devices
	def show_connected_devices(self):
		for dev in self.connected_devices:
			print "Location: " + dev['device']
			print "Name: " + dev['name']
			print "ID: " + dev['ID']
			print "-------------------"
	
	
	def write_all_devices(self):
		with open('known_devices', 'a') as f_out:
			json.dump(self.connected_devices, f_out, indent = 4)

a = USB_ports()
a.get_connected_devices()
a.show_connected_devices()
a.write_all_devices()

