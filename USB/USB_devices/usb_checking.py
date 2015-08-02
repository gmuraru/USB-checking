#! /usr/bin/env python3

import json
import sys
import os
import read_device
import usb
from pyudev import Context, Monitor

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



	def __init__(self, running_mode):
		try:
			with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
				f_out.write("0")

		except IOError:
			print("You do not have enough permissions!")
			sys.exit(1)

		self.running_mode = running_mode
		self.get_known_devices()
		self.get_connected_devices()



	def get_connected_devices(self):

		print("Connected-devices that are new")
		for device in self.context.list_devices(subsystem='usb',
														DEVTYPE='usb_device'):

			if	device.find_parent(subsystem='usb', 
											device_type='usb_device') != None:
				'''	
				print(bus_id)
				print("-------------------------------------------")
				'''
				bus_id = device.sys_name
			
				devnum = int(device.attributes.get("devnum"))
				busnum = int(device.attributes.get("busnum"))


				dev = usb.core.find(address=devnum, bus=busnum)

				dev_id = read_device.get_descriptors(dev)
				dev_name = read_device.get_device_name(device.attributes)

				
				self.add_connected_device(bus_id, dev_id, dev_name, dev)


				if self.running_mode == RunningMode.CLI:
					if dev_id not in self.known_devices.keys():
						self.ask_user(dev, dev_name, bus_id, dev_id)

	


	
	# The bus_id may change for a device if it is connected on a different port
	def ask_user(self, dev, dev_name, bus_id, dev_id):

		print("A new device attached")
		print("Device Product: " + dev_name["Product"]) 
		print("Device Manufacturer: " + dev_name["Manufacturer"])
	
		print(dev)
		
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
			self.add_to_known_device(dev_id, dev_name, dev)
			
			print("The new `known_device list is` {}".format(self.known_devices))

		else:
			print("The device was not added")				

	
	# Form the known devices dictionary
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


	# Add a device to the connected devices dictionary (also retain his bus_id)
	def add_connected_device(self, bus_id, dev_id, dev_name, dev_descriptors):
		self.connected_devices[dev_id] = [dev_name, str(dev_descriptors)]
		self.busID_key_map[bus_id] = dev_id

	# Remove device from the connected devices dictionary
	def remove_connected_device(self, bus_id):
		key = None
		
		if bus_id in self.connected_devices.keys():
			key = self.busID_key_map(bus_id)
			self.connected_devices.pop(key)

		else:
			print("No prompt message - the device was connected while you were " \
				"answering for another device")

		return key


	# Add the device to the known list
	def add_to_known_device(self, dev_id, dev_name, dev_descriptors):
		self.known_devices[dev_id] = [dev_name, str(dev_descriptors)]


	# Waiting state and notification if a `new usb` has been connected
	def usb_monitor_start(self):

		self.monitor.start()

		for action, device in self.monitor:
			bus_id = device.sys_name
			
			# Device has been added
			if action == 'add':

				devnum = int(device.attributess.get("devnum"))
				busnum = int(device.attributes.get("busnum"))

				dev = usb.core.find(address=devnum, bus=busnum)

				print("A device has been added bus_id {}".format(bus_id))

				dev_id = read_device.get_descriptors(dev)
				dev_name = read_device.get_device_name(device.attributes)

				self.add_connected_device(bus_id, dev_id, dev_name, dev)

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
