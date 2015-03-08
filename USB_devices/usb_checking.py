#! /usr/bin/python




import os.path
import re
import subprocess
import json

# http://stackoverflow.com/questions/8110310/simple-way-to-query-connected-usb-devices-info-in-python
class USB_ports:	
	# Matching after this string
	device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<ID>\w+:\w+)\s(?P<name>.+)$", re.I)

	
	# Start with no device
	new_devices = {}
	connected_devices = {}
	known_devices = {}

	def get_connected_devices(self):
		# The output of the command `lsusb` will be verified
		df = subprocess.check_output("lsusb", shell=True)
	
		for dev in df.split('\n'):
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



	def __init__(self):
		self.get_known_devices()		



	def get_new_devices(self):
		if (len(self.connected_devices) == 0):
			self.get_connected_devices()
		
		for dev in self.connected_devices.keys():
			# The device is already on the known list 
			if dev in self.known_devices.keys():
				continue
			self.new_devices[dev] = self.connected_devices[dev]			



	def reset(self):
		self.known_devices = {}
		self.new_devices = {}
		self.connected_devices = {}

	# Waiting state and notification if a `new usb` has been connected
	def usb_monitor(self):
		# A continuous process (this is only for testing)
		while (True):
			# Get known_devices, connected_devices and new_devices
			self.get_known_devices()
			self.get_connected_devices()
			self.get_new_devices()
			if (len(self.new_devices) != 0):
				# For every new device ask the user if he wants to trust that device
				for dev in self.new_devices.keys():	
					print "A new device detected:"
					print "ID: " + dev
					print "Location: " + self.new_devices[dev]['device']
					print "Name: " + self.new_devices[dev]['name']	
					
					input = raw_input("Do you want to add it to the known devices list?(Y/N):")
					while (input != "Y" and input != "N"):
						input = raw_input("Please write Y or N:")

					# If the answer is Y than we can trust that device
					if (input == "Y"):
						all_devices = self.known_devices
						with open('known_devices', 'wt') as f_out:
							all_devices[dev] = self.connected_devices[dev]
							json.dump(all_devices, f_out, indent = 4)
			# Reset all devices and get them again
			self.reset()

					
			
	
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
			print "ID: " + dev
			print "Location: " + self.know_devices[dev]['device']
			print "Name: " + self.know_devices[dev]['name']
			print "-------------------"



	# Show all devices (connected + known_devices)	
	def show_new_devices(self):		
		for dev in self.new_devices:
			print "ID: " + dev
			print "Location: " + self.new_devices[dev]['device']
			print "Name: " + self.new_devices[dev]['name']
			print "-------------------"


	# Write connected devices to a `knowned_device` file, also check if they appear more times
	def write_new_devices(self):
		# If `new devices` have no key
		if (len(self.new_devices) == 0):
			self.get_new_devices()

		# All devices = known devices + connected devices
		all_devices = self.known_devices
		with open('known_devices', 'wt') as f_out:
			for dev in self.new_devices.keys():
			
				# Add him to `not_know_devices` dictionary
				all_devices[dev] = self.connected_devices[dev]

			json.dump(all_devices, f_out, indent = 4)



if __name__ == "__main__":
	
	a = USB_ports()
	'''
	a.get_connected_devices()
	a.show_connected_devices()
	print "\n\n"
	a.get_new_devices()
	a.show_new_devices()
	a.write_new_devices()
	'''

	# Monitor will continuously check the usb to see if any new device is connected.
	# If a new device is connected it will ask if you want or not to be added to a known_host file
	# (this devices can be trusted). If you ask 'Y' the device will be added and will way for another
	# device and if you ask 'N' that device may ask you once again if you can or not trust him
	# (it will ask you until you remove it)
	a.usb_monitor()
