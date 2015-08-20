#USB-checking

##USB folder
###USB_devices folder
Check if a connected devices was already seen by the computer.
If the device was not seen, it will ask for your permission to add it
to a trusted file (*known_host* in our case) - for the command line interface or
you could add them manually from the Gtk+ interface.

###For the command line

```python usb_checking.py```

###For the Gtk+ interface

```python usb_listing.py```


###Updates
* Add pyudev library to check for new added devices (no more expensive loop)
* Add pyusb library to get the device descriptors, custom search and device binding
* Made a gnome-shell-extension to block new USB connected devices when the screen
is locked or when the user wants

---
## USB_DBus folder

** USB inhibit **
This script could run in 3 modes (the complete description could be find in the
script):

1. *continuous mode* --> block all the new connected devices until you decide
to kill the process:
```python usb_inhibit.py```

2. *a command mode* --> block all the new connected devices until a command
is finished:
```python usb_inhibit.py -- sleep 10m```

3. *allow mode* --> allow a specific class of devices:
```python usb_inhibit.py -- allow 0x08 0x01```
This would allow only Audio and USB Mass Storage devices.

### USB_DBus folder

**USB turn on**

```python usb_on.py bus_id (bus_id the given parameter)```

**USB turn off**

```python usb_off.py bus_id (bus_id the given parameter)```

**USB DBus**

For this part is used a listener (to check when the screensaver is activated)
and a dbus system service to start/stop the blocking.

Also the dbus service is used in the gnome-shell-extension.

Still working on improvements regarding the interface.

## Requiremets
* pyudev --> ```pip install pyudev```
* pyusb --> ```pip install pyusb -pre```
