USB-checking

Check if a connected devices was already seen by the computer.
If the device was not seen, it will ask for your permission to add it
to a trusted file ('known_host' in our case)

How to run!

-For the command line--
python usb_checking.py

-For the Gtk+ interface--
python usb_listing.py

Still working on improvements regarding the interface.

Added
USB turn on
	python usb_on.py bus_id (bus_id the given parameter)

USB turn off
	python usb_off.py bus_id (bus_id the given parameter)

USB-inhibit
	python usb-inhibit -- application_name

While the "application_name" is running let no USB devices
connect to your PC.
