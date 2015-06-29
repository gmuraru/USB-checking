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
* Add more device descriptors

---
## USB_modify folder
### USB_DBus folder

USB turn on

```python usb_on.py bus_id (bus_id the given parameter)```

**USB turn off**

```python usb_off.py bus_id (bus_id the given parameter)```

**USB DBus**

Firstly, the ```usb_dbus.py``` must be run with sudo privileges to have the
right to write the ```auto_probe``` file.

Before using the dbus service there must first exist a service file
in the ```/usr/share/dbus-1/services/``` directory.

You can call this file how you would like, but must have the folllowing content:

'''
[D-BUS Service]

Name=org.me.usb

Exec=*Location_of_dbus_script/usb_dbus.py*
'''


USB-inhibit

```python usb-inhibit -- application_name```

While the *application_name* is running let no USB devices
connect to your PC.

Still working on improvements regarding the interface.

## Requiremets
* pyudev --> ```pip install pyudev```
