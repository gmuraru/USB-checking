#! /usr/bin/python

import os.path
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
	connected_devices = {}
	known_devices = {}
	def get_connected_devices(self):
		for dev in self.df.split('\n'):
			if dev:
				dev_info = self.device_re.match(dev)
				if dev_info:
					dev_info_dic = dev_info.groupdict()
					dev_info_dic['device'] = '/dev/bus/usb/%s/%s' \
									% (dev_info_dic.pop('bus'), dev_info_dic.pop('device'))
					ID_device = dev_info_dic.pop("ID", None)
				
					self.connected_devices[ID_device] = dev_info_dic
		

	def get_known_devices(self):
		if (not os.path.isfile('known_devices')):
			return
		
		with open('known_devices', 'rt') as f_in:
			self.known_devices = json.load(f_in)		

	# Show all connected devices
	def show_connected_devices(self):
		for dev in self.connected_devices:
			print "ID: " + dev
			print "Location: " + self.connected_devices[dev]['device']
			print "Name: " + self.connected_devices[dev]['name']
			print "-------------------"
	
	# Show all known devices
	def show_known_devices(self):
		for dev in self.connected_devices:
			print "Location: " + dev
			print "Name: " + self.know_devices[dev]['device']
			print "ID: " + self.know_devices[dev]['name']
			print "-------------------"

	# Show all devices (connected + known_devices)	
	def show_all_devices(self):
		print "CONNECTED DEVICES:"
		print "***********************"
		self.show_connected_devices()
		
		print "KNOWN DEVICES:"
		print "***********************"
		self.show_known_devices()
	

	# Write connected devices to a `knowned_device` file, also check if they appear more times
	def write_connected_devices(self):
		if (len(self.known_devices) == 0):
			self.get_known_devices()

		# All devices = known devices + connected devices
		all_devices = self.known_devices
		with open('known_devices', 'wt') as f_out:
			for dev in self.connected_devices.keys():
				# The device is already on the known list 
				if dev in self.known_devices.keys():
					continue
				
				# Add him to `not_know_devices` dictionary
				all_devices[dev] = self.connected_devices[dev]

			json.dump(all_devices, f_out, indent = 4)

if __name__ == "__main__":
	a = USB_ports()
	a.get_connected_devices()
	a.show_connected_devices()
	a.write_connected_devices()

