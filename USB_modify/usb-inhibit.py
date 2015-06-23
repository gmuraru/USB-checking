#! /usr/bin/python3

import usb_on
import usb_off
import glob
import sys
import subprocess
import pyudev

files_to_look = "/sys/bus/usb/drivers/usb/[1-9]*"
already_connected = []
not_connected = []

# Create context
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

FLAG_REMAIN_UNSEEN = False


def usage():
	print "Bad program call"
	print "Call:"
	print "\t Method1: ./usb-inhibit.py -- process_with_arguments"
	print "\t Method2: python usb-inhibi.py -- process_with_argument"
	print "Options:"
	print ("\t -ru -- remain unseen, after the program finishes running leave "
			"the USB devices drivers (that were connected durring"
			"\n\t\tthe program execution) unloaded")



def form_initial_devices():
	already_connected = []
	for full_dev in glob.glob(files_to_look):
		already_connected.append(full_dev.split("/")[-1])
	return already_connected

def start_process(process_with_args):
	#pid = subprocess.call(process_with_args)
	pid = subprocess.Popen(process_with_args)
	return pid

def rebind_devices():
	
	with open("/sys/bus/usb/drivers_autoprobe", "wt") as f_out:
		f_out.write("1")

	if not FLAG_REMAIN_UNSEEN:
		for dev in not_connected:
			usb_on.usb_enable(dev.split("/")[-1])

def inhibit_USB(pid):

	monitor.start()
	with open("/sys/bus/usb/drivers_autoprobe", "wt") as f_out:
		f_out.write("0")

	for action, device in monitor:
		dev = device.sys_name.split(":")[0]
		print dev
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

		already_connected = form_initial_devices()

		try:
			inhibit_USB(pid)
			rebind_devices()
		except KeyboardInterrupt:
			rebind_devices()

