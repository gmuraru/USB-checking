#! /usr/bin/python3

import usb_on
import usb_off
import glob
import sys
import subprocess

files_to_look = "/sys/bus/usb/drivers/usb/[1-9]*"
already_connected = []
not_connected = []

def usage():
	print "Bad program call"
	print "Call:"
	print "\t Method1: ./usb-inhibit.py -- process_with_arguments"
	print "\t Method2: python usb-inhibi.py -- process_with_argument"

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
	for dev in not_connected:
		usb_on.usb_enable(dev)

def inhibit_USB(pid):
	while pid.wait():
		for full_dev in glob.glob(files_to_look):
			dev = full_dev.split("/")[-1]
			if dev not in not_connected and dev not in already_connected:
				print "Blocked %s" %dev
				not_connected.append(dev)
				usb_off.usb_disable(dev)
	

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

