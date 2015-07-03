### D-Bus turn USB on and off

Currently the bus service would be a SystemBus() because the state of the usb
devices must be global. It is not a session (for a user app) because if one of the
users block a device than all the users would have that device blocked.

-------
#### How to run
1. First there must be a service file in the **/etc/services/dbus-1/system.d**
with the following content (the content is very simplified but it would be
updated the following days):

```
<!DOCTYPE busconfig PUBLIC                                                      
 "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"                          
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">                 
<busconfig>                                                                     
        <policy user="root">                                                    
                <allow own="*"/>                                                
        </policy>                                                               
                                                                                
    <policy context="default">                                                  
        <allow send_interface="org.me.ub"/>                                     
        <allow send_destination="org.me.usb"/>                                  
    </policy>                                                                   
</busconfig>
```

2. Run from one terminal the dbus server:
```python test_dbus.py or ./test_dbus.py```

3. Run from another terminal the *listener* that would check when the GNOME
screensaver is active (while it's active the usb_inhibit will kick in and
when the screen is not blocked it would *bind* the new connecte devices)
```python monitor_lockscreen.py```
