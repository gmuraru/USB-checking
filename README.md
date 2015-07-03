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

---
## USB_modify folder
### USB_DBus folder

USB turn on

```python usb_on.py bus_id (bus_id the given parameter)```

**USB turn off**

```python usb_off.py bus_id (bus_id the given parameter)```

**USB DBus**


USB-inhibit

```python usb-inhibit -- application_name```

While the *application_name* is running let no USB devices
connect to your PC.

Still working on improvements regarding the interface.

## Extension
* Could be used with pytho2.x and python3
* For python3.4 there was a problem with the gi.repository module (further looking)

## Requiremets
* pyudev --> ```pip install pyudev```


