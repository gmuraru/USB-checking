#! /usr/bin/env python3

from USB_DBus import usb_on
from USB_DBus import usb_off
import json
import sys
import os
import re
import subprocess

try:
	from pyudev import Context, Monitor, MonitorObserver
except ImportError: 
	sys.exit("Check if you have installed the module pyudev:\n "\
			"Installation: pip install pyudev")
	

# USB-inhibit runs in 2 mods:
# * If it runs and someone connects a USB device then his driver would not be
# loaded even is a known device
#
# * If it runs and someone connects a USB device than that device would be
# allowed to connect if it is an already known device
# The known devices files would be loaded from the directory USB_devices
class USB_inhibit:
	
	# Create context
	context = Context()

	# Create monitor
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

	# Class initializer
	def __init__(self, flag_known_devices):
		self.observer = MonitorObserver(self.monitor, callback = self.start_monitor,
				                                      name='monitor-observer') 


		# Devices that where connected when the usb_inhibit started
		# -- used for the option when the known_devices flag is False
		self.connected_devices = {}

		# Device that are connected after the usb_inhibit started
		# -- used for the option when the known_devices flag is either False or
		# True
		self.after_connect = {}

		# Known devices -- loaded from file
		self.known_devices = {}

		# And their bus_id port if they are connected
		self.busID_key_map = {}
	
		# If the devices must remain unseen after the usb-inhibit stops
		self.flag_remain_seen = False

		self.flag_known_devices = flag_known_devices
		
		self.check_args()

		# For the lock screen (the usb inhibit will continue to run until
		# a signal is received -- that would tell the screen unlocked)

		# Form the dict with the known devices
		if flag_known_devices:
			self.get_known_devices()

		self.form_initial_devices()	

	# Validate the command
	def check_args(self):
		
		self.running_mode_cont = False
		self.process = None

		# Eg. usb-inhibit -u -- sleep 10
		try:
			index = sys.argv.index('--') # --> 2

			# The process
			self.process = sys.argv[index+1:] # --> sleep 10

			# The usb-inhibit parameters
			parameters = sys.argv[1:index] # --> -u

		except ValueError:
			self.running_mode_cont = True
			parameters = sys.argv[1:]

		
		if '-help' in parameters:
			self.usage()
			return

		if '-u' in parameters:
			self.flag_remain_seen = True


	# The proper way to use the usb-inhibit
	def usage(self):
		print ("Bad program call\n"
				"Call:\n"
				"\t Method1: ./usb-inhibit.py -- process_with_arguments\n"
				"\t Method2: python usb-inhibi.py -- process_with_arguments\n"
				"Options:\n"
				"\t -u -- unseen, after the program finishes running leave "
				"the USB devices drivers (that were connected during\n"
				"\t\tthe program execution) unloaded")


	# Look for already connected devices and take their bus_id
	def form_initial_devices(self):

		for device in self.context.list_devices(subsystem='usb',
							DEVTYPE='usb_device'):  
		                                                                        
			bus_id = device.sys_name		                                    
		                                                                        
			if  device.find_parent(subsystem='usb',
										device_type='usb_device') != None:  
				print(bus_id)
		                                                                        
				(dev_name, key) = self.extract_information(device)              
		                                                                        
				#self.add_connected_device(key, dev_name, bus_id)	            
				self.connected_devices[key] = dev_name

	# Add a new connected device
	def add_connected_device(self, key, dev_name, bus_id):                      
		self.connected_devices[key] = dev_name
		self.busID_key_map[bus_id] = key
     

	# Remove a connected device using the bus_id
	def remove_connected_device(self, bus_id):                                  
		key = self.busID_key_map.pop(bus_id)                                    
		self.connected_devices.pop(key)                                         
		return key                                                              
                                                                                

	# Form the known devices dictionary
	def get_known_devices(self):

		if os.path.isfile('../USB_devices/known_devices'):	                                                           
			with open('../USB_devices/known_devices', 'rt') as f_in:
				try:	                                                                                  
					self.known_devices = json.load(f_in)

				except ValueError:                                                                        
					self.known_devices = {}  		
	

	# Start a process
	def start_process(self):

		try:
			pid = subprocess.Popen(self.process)

		except OSError:
			pid = None

		return pid


	# Rebind the devices that were disconnected (called when the inhibit is
	# stopped)
	def rebind_devices(self):

		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("1")
	
		# If the flag_remain_seen is set then rebind all the still connected
		# devices that were connected during the usb-inhibit process
		if not self.flag_remain_seen:
			for dev in self.busID_key_map.keys():
				print (dev)
				usb_on.usb_enable(dev)


	# Stop the usb-inhibit program
	def stop(self):
		print("Exiting...")
		self.rebind_devices()
		self.observer.stop()


	# Extract information from a device
	def extract_information(self, device):
		information = {}
		key = ""

		attributes = device.attributes

		for info in self.looked_information:
			if info in attributes:
				key += str(attributes.get(info))

			if info == "idProduct":
				dev_idProduct = str(attributes.get(info))

			elif info == "idVendor":
				dev_idVendor = str(attributes.get(info))

			key += self.separator


		# Eliminate the last ":"
		key = key[:-1]


		dev_name = self.get_device_name(attributes)
		return (dev_name, key)


	# Look for device name using the attributes
	def get_device_name(self, attributes):

		# Device product and vendor
		prod_vendor = {	
						"Vendor": "",
						"Product": ""}
	
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

		print(str(productFound) + "  " + str(vendorFound))

		idVendor = attributes.get("idVendor").decode('utf-8')
		idProduct = attributes.get("idProduct").decode('utf-8')
		print(type(idProduct))


		if idProduct == None or idVendor == None:
			return prod_vendor

		regex_idVendor = re.compile('^{}  .*'.format(idVendor))
		regex_idProduct = re.compile('\t{}  .*'.format(idProduct))

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
				if "Vendor" not in prod_vendor.keys():
					prod_vendor["Vendor"] = (res.group(0)).split("  ")[1]
					print (prod_vendor["Vendor"])

				for line_product in f_in:
					res = regex_idProduct.match(line_product)

					if res:
						if "Product" not in prod_vendor.keys():

							prod_vendor["Product"] = (res.group(0)).split("  ")[1]
							print (prod_vendor["Product"])
							
						return prod_vendor
		f_in.close()

		return prod_vendor


	# Start the usb-inhibit program 
	def start(self):

		print ("Start monitoring!")

		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("0")
		
			
		if not self.running_mode_cont:	
			proc = self.start_process()
			print ("Runs with a given command mode")

			self.observer.start()
			while proc.poll() is None:
				continue
		
		# For continuous mode must be called manually the stop command
		else:
			self.observer.daemon = False
			self.observer.start()
			print ("Runs in continuous mode")


	# Start monitoring
	def start_monitor(self, device):

		dev = device.sys_name
		action = device.action                                                                           

		# If a new device is added:
		# * add it to the connected device dict
		# * check if the flag for known_devices is on and the devic
		# is in the known devices dict
		if action == 'add':
			(dev_name, key) = self.extract_information(device)                  
			self.add_connected_device(key, dev_name, dev)

			print ("Device added!")
			print ("Device name {}, bus_id %s and key {}".format(dev_name, dev, key))
			if self.flag_known_devices and key in self.known_devices.keys():
				print ("Device in known list!")
				usb_on.usb_enable(dev)
			else:
				print ("Unkown device! Better block it!")
       
		# If a device is removed, simply remove it from the
		# connected device dict
		if action == 'remove':
			print ("Device removed!")
			print ("Device bus_id {}".format(dev))
			if dev in self.busID_key_map:
				self.remove_connected_device(dev)
	
def main():

	usb_inhibit = USB_inhibit(True)

	try:
		usb_inhibit.start()

	except KeyboardInterrupt:
		print ("\nYou killed me with CTRL+C")
		usb_inhibit.stop()
	
	except IOError:
		print ("You do not have enough permissions!")

if __name__ == "__main__":
	main()
