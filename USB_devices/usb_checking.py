#! /usr/bin/env python3

import json
import sys
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
	monitor.filter_by(subsystem='usb', device_type='usb_device')

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
		try:
			with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
				f_out.write("0")

		except IOError:
			print("You do not have enough permission!")
			sys.exit(1)

		self.running_mode = running_mode
		self.get_known_devices()
		self.get_connected_devices()



	def get_connected_devices(self):

		print("Connected-devices that are new")
		for device in self.context.list_devices(subsystem='usb',
														DEVTYPE='usb_device'):

			bus_id = device.sys_name
			
			
			if	device.find_parent(subsystem='usb', 
											device_type='usb_device') != None:

				print(bus_id)
				print("-------------------------------------------")

				(dev_name, key) = self.extract_information(device)
				
				self.add_connected_device(key, dev_name, bus_id)

				if self.running_mode == RunningMode.CLI:
					if key not in self.known_devices.keys():
						self.ask_user(dev_name, key, bus_id)

	
	def extract_information(self, device):
		information = {}
		key = ""

		attributes = device.attributes

		for info in self.looked_information:

			if info in attributes:
				key += attributes.get(info).decode('utf-8')

			if info == "idProduct":
				dev_idProduct = attributes.get(info).decode('utf-8')

			elif info == "idVendor":
				dev_idVendor = attributes.get(info).decode('utf-8')

			key += self.separator


		# Eliminate the last ":"
		key = key[:-1]


		# The break occured and we can not get a piece of information
		# about the usb device

		#print("This is the key {}".format(key))
		
		dev_name = self.get_device_name(attributes)
		return (dev_name, key)


	def get_device_name(self, attributes):
		# Device product and vendor
		prod_vendor = { "Vendor": "",
						"Product": ""}
	
		vendorFound = False
		productFound = False

		# Check if Product and Vendor are in the device attributes
		if self.looked_vendor_product[0] in attributes:
			prod_vendor["Product"] = attributes.get('product').decode('ascii')
			productFound = True
			
		if self.looked_vendor_product[1] in attributes:
			prod_vendor['Vendor'] = attributes.get('vendor').decode('ascii')
			vendorFound = True
	
		if vendorFound and productFound:
			return prod_vendor


		idVendor = attributes.get("idVendor").decode('ascii')
		idProduct = attributes.get("idProduct").decode("ascii")


		if idProduct == None or idVendor == None:
			return prod_vendor

		# If they are not in the attributes check a file (lsusb uses this file
		# for naming connected devices)
		regex_idVendor = re.compile('^{}  .*'.format(idVendor))
		regex_idProduct = re.compile('\t{}  .*'.format(idProduct))

		# The file has the format utf-8
		try:	
			f_in = open('/var/lib/usbutils/usb.ids', 'rt', encoding='utf-8',
					errors='replace')

		except TypeError:
			import codecs
			f_in = codecs.open('/var/lib/usbutils/usb.ids', 'rt', encoding='utf-8',
					errors='replace')


		for line_vendor in f_in:
			res = regex_idVendor.match(line_vendor)

			if res:
				if not prod_vendor["Vendor"]:
					prod_vendor["Vendor"] = (res.group(0)).split("  ")[1]

				for line_product in f_in:
					res = regex_idProduct.match(line_product)

					if res:
						if not prod_vendor["Product"]:

							prod_vendor["Product"] = (res.group(0)).split("  ")[1]
						
						return prod_vendor
		
		f_in.close()

		return prod_vendor
	

	
	# The bus_id may change for a device if it is connected on a different port
	def ask_user(self, dev_name, key, bus_id):

		print("A new device attached")
		print("Bus_ID: " + bus_id) 
	
		self.information_print(dev_name, key)
		
		question = "Do you want to add it to the known devices list? (Y/N): "
		user_input = None

		try:
			if sys.version_info >= (3, 0):	
				user_input = input(question)
			else:
				user_input = raw_input(question)

		except EOFError:
			print("\n")

		except KeyboardInterrupt:
			print("\nRebinding the devices...")
			self.usb_monitor_stop()

		while not user_input or user_input.upper() not in ["Y", "N"]:
			try:
				if sys.version_info >= (3,0):
					user_input = input("Please write Y or N: ")
				else:
					user_input = raw_input("Please write Y or N: ")

			except EOFError:
				pass

			except KeyboardInterrupt:
				print("\nRebinding the devices...")
				self.usb_monitor_stop()


			

		# If the answer is Y than we can trust that device
		if user_input.upper() == 'Y':
			print("Added")
			self.known_devices[key] = dev_name
			
			print("The new `known_device list is` {}".format(self.known_devices))

		else:
			print("The device was not added")
			
	
					

	def get_known_devices(self):
		if os.path.isfile('known_devices'):

			with open('known_devices', 'rt') as f_in:

				try:
					self.known_devices = json.load(f_in)
				
				except ValueError:
					self.known_devices = {}	
				
				except TypeError:
					self.known_devices = {}
		print("Known devices {}".format(self.known_devices))

	# Printing informations about the device
	def information_print(self, dev_name, dev_information):
		print("Vendor: {}".format(dev_name["Vendor"])) 
		print("Product: {}".format(dev_name["Product"]))
		dev_info_split = dev_information.split(self.separator)

		for info_index in range(len(self.looked_information)):
			print("{}:{}".format(self.looked_information[info_index],
								dev_info_split[info_index]))
		
		print("-----------------------------------\n")


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
			dev = device.sys_name
			
			# Device has been added
			if action == 'add':
				print("A device has been added bus_id {}".format(dev))
				(dev_name, key) = self.extract_information(device)
				self.add_connected_device(key, dev_name, dev)

				if key not in self.known_devices.keys():
					self.ask_user(dev_name, key, dev)
				else:
					print("It is a trusted device")

			# Device has been removed
			if action == 'remove':
				print("A device has been removed from the bus_id {}".format(dev))
				self.remove_connected_device(dev)
		

	def usb_monitor_stop(self):
		self.reload_on()
		with open('known_devices', 'wt') as f_out:
			json.dump(self.known_devices, f_out, indent = 4)

		sys.exit(0)
			

	def reload_on(self):
		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("1")

def main():
	usb_guard = USB_ports(RunningMode.CLI)
	
	# Monitor will continuously check the usb to see if any new device is
	# connected. If a new device is connected it will ask if you want or not
	# to be added to a known_host file (this devices can be trusted). If you as
	# 'Y' the device will be added and will way for another device and if you
	# ask 'N' that device may ask you once again if you can or not trust him
	# (it will ask you until you remove it)

	try:
		usb_guard.usb_monitor_start()
	
	except KeyboardInterrupt:
		print ("\nYou pressed CTRL+C! Rebinding the devices...")
		usb_guard.usb_monitor_stop()

if __name__ == "__main__":
	main()
