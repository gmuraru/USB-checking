#! /usr/bin/env python

#                                                                               
#    Copyright 2015 George-Cristian Muraru <murarugeorgec@gmail.com>            
#    Copyright 2015 Tobias Mueller <muelli@cryptobitch.de>                      
#                                                                               
#    This file is part of USB Inhibitor.                                        
#                                                                               
#    USB Inhibitor is free software: you can redistribute it and/or modify      
#    it under the terms of the GNU General Public License as published by       
#    the Free Software Foundation, either version 3 of the License, or          
#    (at your option) any later version.                                        
#                                                                               
#    USB Inhibitor and the afferent extension is distributed in the hope that it
#    will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              
#    GNU General Public License for more details.                               
#                                                                               
#    You should have received a copy of the GNU General Public License          
#    along with USB Inhibitor.  If not, see <http://www.gnu.org/licenses/>.     
#  


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

    device_class_nonblock = [0x09] # Allow USB hubs to connect


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
                    self.device_class_nonblock = [int(x, 0) for x in sys.argv[index+1:][1:]]

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
		self.add_connected_device(bus_id, dev_name, key)	            

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

        if self.observer != None:
    	    self.observer.stop()
	
	# For the dbus part we have to clear all the dict content
	self.known_devices.clear()
	self.connected_devices.clear()
	self.busID_key_map.clear()


    # Start the usb-inhibit program 
    def start(self):
        self.observer = MonitorObserver(self.monitor, callback = self.start_monitor,
		                                      name='monitor-usb-inhibitor') 

	# For the lock screen (the usb inhibit will continue to run until
	# a signal is received -- that would tell the screen unlocked)

	# Form the dict with the known devices
	if self.flag_known_devices:
    	    self.get_known_devices()

	# Initial devices not formed - currently not used
        #self.form_initial_devices()

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
	    self.observer.daemon = False
	    self.observer.start()
	    print("Runs in continuous mode")

    def add_nonblock_device(self, class_dev):
        self.device_class_non_block.append(class_dev)


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
                
	    elif read_device.find_device(dev, list(usb.core.find(find_all=True, custom_match = 
                                            read_device.custom_search(self.device_class_nonblock)))):
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

    # Bind the driver of a device
    def bind_driver(self, bus_id, dev_id):
        if self.connected_devices[bus_id][1] == dev_id:
            usb_on.usb_enable(bus_id)
            return True

        return False
	


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
