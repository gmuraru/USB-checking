#! /usr/bin/python3

from USB_DBus import usb_on
from USB_DBus import usb_off
import json
import sys
import subprocess
import pyudev


# USB-inhibit runs in 2 mods:
# * If it runs and someone connects a USB device then his driver would not be
# loaded even is a known device
#
# * If it runs and someone connects a USB device than that device would be
# allowed to connect if it is an already known device
# The known devices files would be loaded from the directory USB_devices
class USB_inhibit:
	
	# Create context
	context = pyudev.Context()
	monitor = pyudev.Monitor.from_netlink(context)
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

	# Class initializer
	def __init__(self, known_devices):

		# Device list with already connected devices
		self.already_connected = {}

		# Device list with not connected devices
		self.not_connected = {}

		# Known devices
		self.known_devices = {}

		# And their bus_id port if they are connected
		self.busID_key_map = {}
	
		# If the devices must remain unseen after the usb-inhibit stops
		self.flag_remain_unseen = True

		self.known_devices = False

		# For the lock screen (the usb inhibit will continue to run until
		# a signal is received -- that would tell the screen unlocked)
		self.running_mode_cont = True

		self.known_devices = known_devices
		
		if not check_args():
			self.usage()


	# Validate the command
	def check_args(self):
		
		call_with_parameters = sys.argv.split('--')[0]
		
		parameters = call_with_parameters.split()[1:]

		if '-help' in parameters:
			self.usage()
			return True

		if '-u' in parameters:
			self.flag_remain_unseen = True


		if len(sys.argv.split('--') >= 1):
			self.process = sys.argv.split('--')[1:]
			self.runing_mode_cont = False

		else:

			return False

		return True


	# The proper way to use the usb-inhibit
	def usage(self):
		print ("Bad program call"
				"\nCall:"
				"\n\t Method1: ./usb-inhibit.py -- process_with_arguments"
				"\n\t Method2: python usb-inhibi.py -- process_with_arguments"
				"\nOptions:"
				"\n\t -u -- unseen, after the program finishes running leave "
				"the USB devices drivers (that were connected during"
				"\n\t\tthe program execution) unloaded")


	# Look for already connected devices and take their bus_id
	def form_initial_devices(self):

		for device in self.context.list_devices(subsystem='usb',                
                                                        DEVTYPE='usb_device'):  
                                                                                
            bus_id = device.sys_name                                            
                                                                                
            if  device.find_parent(subsystem='usb',                             
                                            device_type='usb_device') != None:  
                print bus_id                                                    
                                                                                
                (dev_name, key) = self.extract_information(device)              
                                                                                
                self.add_connected_device(key, dev_name, bus_id)                


	def add_connected_device(self, key, dev_name, bus_id):                      
        self.connected_devices[key] = dev_name                                  
        self.busID_key_map[bus_id] = key                                        
                                                                                

    def remove_connected_device(self, bus_id):                                  
        key = self.busID_key_map.pop(bus_id)                                    
        self.connected_devices.pop(key)                                         
        return key                                                              
                                                                                

    def add_to_known_device(self, key, dev_name):                               
        self.known_devices[key] = dev_name                                                                                 


	# Get the known devices
	def get_known_devices(self)
		if os.path.isfile('../USB_devices/known_devices'):                                                               
			with open('../USB_devices/known_devices', 'rt') as f_in:
				try:                                                                                      
                    self.known_devices = json.load(f_in)                                                  
                                                                                                          
                except ValueError:                                                                        
                    self.known_devices = {}  		
	


	def start_process(self):

		try:
			pid = subprocess.Popen(self.process)

		except OSError:
			pid = None

		return pid


	def rebind_devices(self):

		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("1")
	
		if not self.flag_remain_unseen:
			for dev in not_connected:
				usb_on.usb_enable(dev.sys_name)

	def inhibit_USB(self):

		with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
			f_out.write("0")

        self.monitor.start()                                                    
                                                                                
        for action, device in self.monitor:                                     
            dev = device.sys_name.split(':')[0]                                 
            (dev_name, key) = self.extract_information(device)                  
                                                                                
                                                                                
            if action == 'add':                                                 
                self.add_connected_device(key, dev_name, dev)                   
                                                                                
            if action == 'remove':                                              
                self.remove_connected_device(dev)

def main():
	else:
		pid = start_process(process_with_args)

		if pid == None:
			print ("Enter a valid command!")

		else:		

			already_connected = form_initial_devices()

			try:
				inhibit_USB(pid)
				rebind_devices()

			except IOError:
				print ("You do not have enough permissions to create the file")

			except KeyboardInterrupt:
				rebind_devices()


if __name__ == "__main__":
	main()
