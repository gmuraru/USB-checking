#! /usr/bin/python3

# Add the service file in the specific directory

import os

def create_service():
	dbus_file = os.path.dirname(os.path.abspath(__file__)) + "/usb_dbus.py"
	with open('/usr/share/dbus-1/services/usb_monitor.service', 'wt') as f_out:
		f_out.write("[D-BUS Service]"
					"\nName=org.me.usb"
					"\nExec=%s" % dbus_file)
	print ("Service file succesfully created!")

if __name__ == "__main__":
	try:
		create_service()
	except IOError:
		print ("You do not have enough permissions to create the file")
