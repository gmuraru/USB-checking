#! /usr/bin/env python3

import json
import os
from pyudev import Context, Monitor
import re

# Defining the 2 running modes
class RunningMode:
	CLI = 1
	GTK = 2


class USB_ports:	

	# Start with no device
	connected_devices = {}
	known_devices = {}
	busID_key_map = {}
	
	# Pyudev monitor
	context = Context()
	monitor = Monitor.from_netlink(context)

	monitor.filter_by(subsystem='usb')

	# Separator for key
	separator = ':'
	
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

	looked_vendor_product = ["product", "vendor"]

	# The unique identifier (indexes of the looked_information)
	# Currently all the information is used for unique identification
	unique_identifier = range(len(looked_information));



	def __init__(self, running_mode):

		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("0")

		self.running_mode = running_mode
		self.get_known_devices()
		self.get_connected_devices()



	def get_connected_devices(self):

		for device in self.context.list_devices(subsystem='usb',
														DEVTYPE='usb_device'):

			bus_id = device.sys_name

			if	device.find_parent(subsystem='usb', 
											device_type='usb_device') != None:
				print bus_id

				(dev_name, key) = self.extract_information(device)
				
				self.add_connected_device(key, dev_name, bus_id)

				if self.running_mode == RunningMode.CLI:
					if key not in self.known_devices.keys():
						self.ask_user(dev_name, key, bus_id)

	
	def get_busID(self):
		return busID_key_map


	def extract_information(self, device):
		information = {}
		key = ""

		attributes = device.attributes

		for info in self.looked_information:
			if info in attributes:
				key += attributes.get(info)

			if info == "idProduct":
				dev_idProduct = attributes.get(info)

			elif info == "idVendor":
				dev_idVendor = attributes.get(info)

			key += self.separator


		# Eliminate the last ":"
		key = key[:-1]


		# The break occured and we can not get a piece of information
		# about the usb device
		#if len(key.split(":")) <= 0.3 * len(self.looked_information):
		#	continue

		dev_name = self.get_device_name(attributes)
		return (dev_name, key)


	def get_device_name(self, attributes):
		# Device product and vendor
		prod_vendor = {}
	
		vendorFound = False
		productFound = False

		if self.looked_vendor_product[0] in attributes:
			prod_vendor["Product"] = attributes.get('product')
			productFound = True
			
		if self.looked_vendor_product[1] in attributes:
			prod_vendor['Vendor'] = attributes.get('vendor')
			vendorFound = True
	
		if vendorFound and productFound:
			return prod_vendor


		idVendor = attributes.get("idVendor")
		idProduct = attributes.get("idProduct")

		if idProduct == None or idVendor == None:
			return prod_vendor

		regex_idVendor = re.compile('^%s  .*' %(idVendor))
		regex_idProduct = re.compile('\t%s  .*' %(idProduct))


		with open("/var/lib/usbutils/usb.ids") as f_in:
			for line_vendor in f_in:
				res = regex_idVendor.match(line_vendor)

				if res:
					if 'Vendor' not in prod_vendor.keys():
						prod_vendor["Vendor"] = (res.group(0)).split("  ")[1]

					for line_product in f_in:
						res = regex_idProduct.match(line_product)

						if res:
							if 'Product' not in prod_vendor.keys():

								prod_vendor["Product"] = (res.group(0)).split("  ")[1]
							
							return prod_vendor
			
		return prod_vendor
	

	
	# The bus_id may change for a device if it is connected on a different port
	def ask_user(self, dev_name, key, bus_id):

		print ("A new device attached")
		print ("Bus_ID: " + bus_id) 
	
		self.information_print(dev_name, key)

		input = raw_input("Do you want to add it to the known devices list? (Y/N): ")

		while input != "Y" and input != "N":
			input = raw_input("Please write Y or N:")

		# If the answer is Y than we can trust that device
		if input.upper() == 'Y':
			print ("Added")
			self.known_devices[key] = dev_name
			print self.known_devices
	
					

	def get_known_devices(self):
		if os.path.isfile('known_devices'):

			with open('known_devices', 'rt') as f_in:

				try:
					self.known_devices = json.load(f_in)
				
				except ValueError:
					self.known_devices = {}	

	# Printing informations about the device
	def information_print(self, dev_name, dev_information):
		
		print ("Vendor: %s" %dev_name["Vendor"])
		print ("Product: %s" %dev_name["Product"])
		dev_info_split = dev_information.split(self.separator)

		for info_index in range(len(self.looked_information)):
			print (self.looked_information[info_index] + ": " 
												+ dev_info_split[info_index])
		
		print ("-----------------------------------\n")


	def add_connected_device(self, key, dev_name, bus_id):
		self.connected_devices[key] = dev_name
		self.busID_key_map[bus_id] = key

	def remove_connected_device(self, bus_id):
		key = self.busID_key_map.pop(bus_id)
		self.connected_devices.pop(key)
		return key

	def add_to_known_device(self, key, dev_name):
		self.known_devices[key] = dev_name


	# Waiting state and notification if a `new usb` has been connected
	def usb_monitor_start(self):

		self.monitor.start()

		for action, device in self.monitor:
			dev = device.sys_name.split(':')[0]
			(dev_name, key) = self.extract_information(device)
			

			if action == 'add':
				self.add_connected_device(key, dev_name, dev)

				if key not in self.known_devices.keys():
					self.ask_user(dev_name, key, dev)

			if action == 'remove':
				self.remove_connected_device(dev)
		

	def usb_monitor_stop(self):
		self.reload_on()
		with open('known_devices', 'wt') as f_out:
			json.dump(self.known_devices, f_out, indent = 4)
			

	def reload_on(self):
		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("1")

def main():
	try:
		usb_guard = USB_ports(RunningMode.CLI)
	
	except IOError:
		print ("You do not have enough permissions to create the file")
		return 1


	# Monitor will continuously check the usb to see if any new device is
	# connected. If a new device is connected it will ask if you want or not
	# to be added to a known_host file (this devices can be trusted). If you as
	# 'Y' the device will be added and will way for another device and if you
	# ask 'N' that device may ask you once again if you can or not trust him
	# (it will ask you until you remove it)

	try:
		usb_guard.usb_monitor_start()
	
	except KeyboardInterrupt:
		usb_guard.usb_monitor_stop()

if __name__ == "__main__":
	main()
