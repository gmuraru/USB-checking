#! /usr/bin/python3

import os.path
import json
from pyudev import Context, Monitor
import re

class USB_ports:	
	
	# Start with no device
	new_devices = {}
	connected_devices = {}
	known_devices = {}
	
	# Pyudev monitor
	context = Context()
	monitor = Monitor.from_netlink(context)

	monitor.filter_by(subsystem='usb')

	# Separator for key
	separator = ":"
	
	# Information to look up
	looked_information = ["bNumConfigurations",
						"iSerialNumber",
						"iProduct",
						"iManufacturer",
						"bcdDevice",
						"idProduct",
						"idVendor",
						"bMaxPacketSize",
						"bDeviceProtocol",
						"bDeviceSubClass",
						"bDeviceClass",
						"bcdUSB",
						"bDescriptorType",
						"bLength"]
	
	# The unique identifier (indexes of the looked_information)
	# Currently all the information is used for unique identification
	unique_identifier = range(len(looked_information));

	def get_connected_devices(self):
		devices_info = {}
		

		for dev in self.context.list_devices(subsystem='usb'):#, DEVTYPE='usb_device'):
			information = {}
			key = ""
		
			attributes = dev.attributes

			for info in self.looked_information:
				if info in attributes:
					key += attributes.get(info)
					key += ":"

					if info == "idProduct":
						dev_idProduct = attributes.get(info)
					elif info == "idVendor":
						dev_idVendor = attributes.get(info)


			# Eliminate the last ":"
			key = key[:-1]

			
			# The break occured and we can not get a piece of information
			# about the usb device
			if len(key.split(":")) <= 0.3 * len(self.looked_information):
				continue
		
			device = self.get_device_information(dev_idProduct, dev_idVendor)
			self.connected_devices[key] = device
	

	def get_device_information(self, idProduct, idVendor):
		# Device product and vendor
		product_vendor = {}
		regex_idVendor = re.compile('^%s  .*' %(str(idVendor)))
		regex_idProduct = re.compile('\t%s  .*' %(str(idProduct)))
		with open("/var/lib/usbutils/usb.ids") as f_in:
			for line_vendor in f_in:
				result = regex_idVendor.match(line_vendor)
				if result:
					product_vendor["Vendor"] = (result.group(0)).split("  ")[1]
					for line_product in f_in:
						result = regex_idProduct.match(line_product)
						if result:
							product_vendor["Product"] = (result.group(0)).split("  ")[1]
							return product_vendor
			
		return product_vendor
						

	def get_known_devices(self):
		if (not os.path.isfile('known_devices')):
			return
		
		with open('known_devices', 'rt') as f_in:
			self.known_devices = json.load(f_in)		



	def __init__(self):
		self.get_known_devices()		

	# Printing info about the device
	def information_print(self, requests, information):
		for name in requests:
			if name in information.keys():
				print name + ": " + information[name]
		

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
					self.information_print(["Product", "Vendor"], self.connected_devices[dev])
					
					input = raw_input("Do you want to add it to the known devices list?(Y/N):")
					while (input != "Y" and input != "N"):
						input = raw_input("Please write Y or N:")

					# If the answer is Y than we can trust that device
					if (input.upper() == "Y"):
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
			self.information_print(["Product", "Vendor"], self.connected_devices[dev])
			print "-------------------"



	# Show all known devices
	def show_known_devices(self):
		for dev in self.connected_devices:
			print "ID: " + dev
			self.information_print(["Product", "Vendor"], self.connected_devices[dev])
			print "-------------------"



	# Show all devices (connected + known_devices)	
	def show_new_devices(self):		
		for dev in self.new_devices:
			print "ID: " + dev
			self.information_print(["Product", "Vendor"], self.connected_devices[dev])
			print "-------------------"


	def write_device(self, device):
		all_devices = self.known_devices
		
		with open('known_devices', 'wt') as f_out:
			# Add him to `not_know_devices` dictionary
			all_devices[device.keys()[0]] = device[device.keys()[0]]

			json.dump(all_devices, f_out, indent = 4)


	# Write connected devices to a `knowned_device` file, also check if they appear more times
	def write_new_devices(self):
		# If `new devices` have no key
		if (len(self.new_devices) == 0):
			self.get_new_devices()

		# All devices = known devices + connected devices
		all_devices = self.known_devices
		with open('known_devices', 'wt') as f_out:
			for dev in self.new_devices.keys():
			
				all_devices[dev] = self.connected_devices[dev]

			json.dump(all_devices, f_out, indent = 4)



if __name__ == "__main__":
	
	a = USB_ports()
	
	a.get_connected_devices()
	print a.connected_devices
	'''
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
	#a.usb_monitor()
