#! /usr/bin/python3

import usb_on
import usb_off
import glob
import sys
import subprocess
import pyudev

already_connected = []
not_connected = []

# Create context
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

FLAG_REMAIN_UNSEEN = False


# The proper way to use the usb-inhibit
def usage():
	print ("Bad program call"
			"\nCall:"
			"\n\t Method1: ./usb-inhibit.py -- process_with_arguments"
	        "\n\t Method2: python usb-inhibi.py -- process_with_arguments"
			"\nOptions:"
			"\n\t -u -- unseen, after the program finishes running leave"
			"the USB devices drivers (that were connected during"
			"\n\t\tthe program execution) unloaded")


# Look for already connected devices and take their bus_id
def form_initial_devices():

	for device in context.list_devices(subsystem='usb'):

		if device.device_type == 'usb_device' and \
			device.find_parent(subsystem='usb', device_type='usb_device') != None:

			already_connected.append(device.sys_name.split('/')[-1])


	return already_connected

def start_process(process_with_args):

	try:
		pid = subprocess.Popen(process_with_args)
	except OSError:
		pid = None

	return pid

def rebind_devices():
	
	with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
		f_out.write("1")

	if not FLAG_REMAIN_UNSEEN:
		for dev in not_connected:
			usb_on.usb_enable(dev.split('/')[-1])

def inhibit_USB(pid):

	monitor.start()
	with open('/sys/bus/usb/drivers_autoprobe', 'wt') as f_out:
		f_out.write("0")

	for action, device in monitor:
		dev = device.sys_name.split(':')[0]
		print(dev)
		if action == 'add':
			not_connected.append(dev)

		if action == 'remove' and dev in not_connected:
			not_connected.remove(dev)

if __name__ == "__main__":

	process_with_args = sys.argv[2:]
	
	if not process_with_args:
		usage()

	else:
		pid = start_process(process_with_args)
		
		if pid == None:
			print ("Enter a valid command!")

		else:		
		
			already_connected = form_initial_devices()

			try:
				inhibit_USB(pid)
				rebind_devices()
			except KeyboardInterrupt:
				rebind_devices()

