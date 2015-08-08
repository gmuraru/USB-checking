#USB-checking

##USB_device folder
Check if a connected devices was already seen by the computer.
If the device was not seen, it will ask for your permission to add it
to a trusted file (*known_host* in our case)

###For the command line

```python usb_checking.py```

###For the Gtk+ interface

```python usb_listing.py```


###Updates
* Add pyudev library to check for new added devices (no more expensive loop)
* Add pyusb library to get the device descriptors, custom search and device binding

---
## USB_modify folder

** USB inhibit **
This script could run in 2 modes (the complete description could be find in the
script):

1. *continuous mode* --> block all the new connected devices until you decide
to kill the process:
```python usb_inhibit.py```

2. *a command mode* --> block all the new connected devices until a command
is finished:
```python usb_inhibit.py -- sleep 10m```

### USB_DBus folder

USB turn on

```python usb_on.py bus_id (bus_id the given parameter)```

**USB turn off**

```python usb_off.py bus_id (bus_id the given parameter)```

**USB DBus**

For this part is used a listener (to check when the screensaver is activated)
and a dbus service to start/stop the monitorisation.

Still working on improvements regarding the interface.

## Extension
* Could be used with pytho2.x and python3
* For python3.4 there was a problem with the gi.repository module (further looking)

## Requiremets
* pyudev --> ```pip install pyudev```


