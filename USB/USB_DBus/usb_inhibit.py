#! /usr/bin/env python

import read_device
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

try:
	import usb.core
except ImportError:
    sys.exit("Check if you have installed the module pyusbhere:\n "\
			"Installation: pip install pyusb --pre")
	
import usb_on
import usb_off


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

    name_device = ["Manufacturer", "Product"]

    MASS_STORAGE = 0x8
    HID = 0x03
    AUDIO = 0x01
    VIDEO = 0x0E

    device_class_non_block = []


    # Class initializer
    def __init__(self, flag_known_devices):
	# Devices that where connected when the usb_inhibit started
	# -- used for the option when the known_devices flag is False
	self.connected_devices = {}
	self.busID_key_map = {}

	# Device that are connected after the usb_inhibit started
	# -- used for the option when the known_devices flag is either False or
	# True -- currently not used
	self.after_connect = {}

	# Known devices -- loaded from file
	self.known_devices = {}

	# If the devices must remain unseen after the usb-inhibit stops
	self.flag_remain_seen = False

	self.flag_known_devices = flag_known_devices
	
	self.check_args()



    # Validate the command
    def check_args(self):
		
	self.running_mode_cont = False
	self.process = None

      	# Eg. usb-inhibit -u -- sleep 10
	try:
            index = sys.argv.index('--') # --> 2

            # Check if block
            if sys.argv[index+1:][0] == "allow":
                try: 
                    self.device_class_non_block = [int(x, 0) for x in sys.argv[index+1:][1:]]
                    print (self.device_class_non_block)
                except ValueError:
                    sys.exit("Invalid arguments for allow - use only valid device classes")

                self.running_mode_cont = True
                return

            # The process
            self.process = sys.argv[index+1:] # --> sleep 10

            # The usb-inhibit parameters
	    parameters = sys.argv[1:index] # --> -u

	except ValueError:
	    self.running_mode_cont = True
            parameters = sys.argv[1:]

		 
        if '-help' in parameters:
	    self.usage()
	    sys.exit(0)

	if '-u' in parameters:
	    self.flag_remain_seen = True


		

	# The proper way to use the usb-inhibit
    def usage(self):
	print("USB-inhibit\n"
		"Call:\n"
                    "\t python usb-inhibit.py -- allow 0x1 0x8\n"
                    "\t python usb-inhibit.py -- process_with_arguments\n"
                    "\t python usb-inhibit.py (continuous inhibitor)\n"
		"Options:\n"
	    	    "\t -u -- unseen, after the program finishes running leave "
		    "the USB devices drivers (that were connected during\n"
		    "\t\tthe program execution) unloaded\n"
                    "\t -help -- how to use the python script")


    # Look for already connected devices and take their bus_id
    # !!! Not used !!!
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
    def add_connected_device(self, bus_id, dev_name, dev_id):
	self.connected_devices[bus_id] = [dev_name, dev_id]
     

    # Remove a connected device using the bus_id
    def remove_connected_device(self, bus_id):                                  
        key = ""
        if bus_id in self.busID_key_map.keys():
            key = self.busID_key_map.pop(bus_id)                                    
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
	        print("Rebind devie: {}".format(dev))
		usb_on.usb_enable(dev)


    # Stop the usb-inhibit program
    def stop(self):
	print("Stop monitoring...")

	self.rebind_devices()
	self.observer.stop()
	
	# For the dbus part we have to clear all the dict content
	self.known_devices.clear()
	self.connected_devices.clear()
	self.busID_key_map.clear()



	# Extract information from a device
	# !!! Not used !!!
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
				"Manufacturer": "",
        			"Product": ""}
	
		vendorFound = False
		productFound = False
 
		if self.name_device[0].lower() in attributes:
			prod_vendor[self.name_device[0]] = attributes.get(self.name_device[0].lower())
			vendorFound = True
			
		if self.name_device[1].lower() in attributes:
			prod_vendor[self.name_device[1]] = attributes.get(self.name_device[1].lower())
			productFound = True
	
		if vendorFound and productFound:
			return prod_vendor

		idVendor = attributes.get("idVendor").decode('utf-8')
		idProduct = attributes.get("idProduct").decode('utf-8')

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
				if not prod_vendor["Manufacturer"]:
					prod_vendor["Manufacturer"] = (res.group(0)).split("  ")[1]

				for line_product in f_in:
					res = regex_idProduct.match(line_product)

					if res:
						if not prod_vendor["Product"]:
							prod_vendor["Product"] = (res.group(0)).split("  ")[1]
							
						return prod_vendor
		f_in.close()

		return prod_vendor


    # Start the usb-inhibit program 
    def start(self):

        self.observer = MonitorObserver(self.monitor, callback = self.start_monitor,
		                                      name='monitor-observer') 

	# For the lock screen (the usb inhibit will continue to run until
	# a signal is received -- that would tell the screen unlocked)

	# Form the dict with the known devices
	if self.flag_known_devices:
    	    self.get_known_devices()

	# Initial devices not formed
#	self.form_initial_devices()

	with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
	    f_out.write("0")
		
	print("Start monitoring!")

	if not self.running_mode_cont:	
            proc = self.start_process()
	    print ("Runs with a given command mode")

	    self.observer.start()
	    while proc.poll() is None:
	        continue
		
	# For continuous mode must be called manually the stop command
	else:
            # For testing purposes one can let False and then run the inhibit
            # in continuous mode to see the output of it

	    #self.observer.daemon = False
	    self.observer.start()
	    print("Runs in continuous mode")

    def add_nonblock_device(self, class_dev):
        self.device_class_non_block.append(class_dev)

    def custom_search(self, dev):
	import usb.util
		
	for descriptor_value in self.device_class_non_block:

    	    if dev.bDeviceClass == descriptor_value:
		return True

	    for cfg in dev:
		if usb.util.find_descriptor(cfg, bInterfaceClass = descriptor_value) is not None:
	    	    return True

        return False

        
    def found(self, dev, list_devices):
        for maybe_device in list_devices:
            if dev.bus == maybe_device.bus and dev.address == maybe_device.address:
                return True

        return False

    # Start monitoring
    def start_monitor(self, device):

	bus_id = device.sys_name

	action = device.action                                                                          

	# If a new device is added:
	# * add it to the connected device dict
        # * check if the flag for known_devices is on and the devic
	# is in the known devices dict
	if action == 'add':

	    devnum = int(device.attributes.get("devnum"))
	    busnum = int(device.attributes.get("busnum"))
			
	    dev = usb.core.find(address=devnum, bus=busnum)
			
    	    dev_id = read_device.get_descriptors(dev)
	    dev_name = read_device.get_device_name(device.attributes)
	    self.add_connected_device(bus_id, dev_name, dev_id)

	    print("Device added!")
    	    print("Device name {}, dev_id {} and bus_id {}".format(dev_name, dev_id, bus_id))

	    if self.flag_known_devices and dev_id in self.known_devices.keys():
		print("Device in known list!")
		usb_on.usb_enable(bus_id)
                
	    elif self.found(dev, list(usb.core.find(find_all=True, custom_match = self.custom_search))):
		print("Device is on non-blocking list")
		usb_on.usb_enable(bus_id)
	    else:
		print("Unkown device! Better block it!")

       
	    # If a device is removed, simply remove it from the
	    # connected device dict
	    if action == 'remove':
		print("Device removed!")
		print("Device bus {}".format(bus_id))
		self.remove_connected_device(bus_id)
	
def main():

    usb_inhibit = USB_inhibit(True)

    try:
        #usb_inhibit.add_nonblock_device(USB_inhibit.AUDIO)
        #usb_inhibit.add_nonblock_device(USB_inhibit.MASS_STORAGE)
    	usb_inhibit.start()


    except KeyboardInterrupt:
    	print("\nYou killed me with CTRL+C")
    	usb_inhibit.stop()
	
    except IOError:
    	print("You do not have enough permissions!")

if __name__ == "__main__":
    main()
