#! /usr/bin/python3

import threading
from gi.repository import Gtk, GObject, GLib
from usb_checking import RunningMode, USB_ports
from pyudev import MonitorObserver
import time
import gobject

# Modified tutorial http://python-gtk-3-tutorial.readthedocs.org/en/latest/treeview.html
class USB_ViewFilterWindow(Gtk.Window):

    def __init__(self):
        self.device_monitor = USB_ports(RunningMode.GTK)
        self.observer = MonitorObserver(self.device_monitor.monitor, callback =	self.refresh,
                                      name='monitor-observer')

        Gtk.Window.__init__(self, title = "USBGnomento")
 
        self.set_resizable(True)
        self.set_border_width(10)

        # Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # Creating the ListStore model
        self.usb_list = Gtk.ListStore(bool, bool, str, str, str)
       
        self.current_filter_usb = None
        # Creating the filter, feeding it with the usb_list model
        self.usb_filter = self.usb_list.filter_new()
        # Setting the filter function
        self.usb_filter.set_visible_func(self.usb_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.usb_filter)

        for i, column_title in enumerate(["Known Device", "Connected", "Id", "Vendor", "Product"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property('cell-background', 'grey')
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        # Creating buttons to filter by device state, and setting up their events
        self.buttons = list()
        for usb_type in ["Connected Devices", "Known Devices", "Unknown Devices"]:
            button = Gtk.Button(usb_type)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
 	
        # Write to know devices
        button = Gtk.Button("Write selected")
        self.buttons.append(button)
        button.connect("clicked", self.write_to_known_devices)
        
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        
        self.scrollable_treelist.add(self.treeview)


        self.first_populate_table()
        self.show_all()	
        self.observer.start()
	   # GObject.timeout_add(200, self.refresh)	


    def first_populate_table(self):
        self.device_monitor.get_known_devices()
        self.device_monitor.get_connected_devices()

        for device in self.device_monitor.known_devices.keys():

            if device in self.device_monitor.connected_devices.keys():
                self.usb_list.append([True, True, device,
                            self.device_monitor.known_devices[device]['Vendor'],
                            self.device_monitor.known_devices[device]['Product']])

            else:
                self.usb_list.appned([True, False, device,
							self.device_monitor.known_devices[device]['Vendor'],
							self.device_monitor.known_devices[device]['Product']])
				

        for device in self.device_monitor.connected_devices.keys():
			
            if device not in self.device_monitor.known_devices.keys():
                self.usb_list.append([False, True, device,
                             self.device_monitor.connected_devices[device]['Vendor'],
                             self.device_monitor.connected_devices[device]['Product']])
                

    # Write selected device to file
	# The device would be kept in a buffer until the program exits
    def write_to_known_devices(self, button):
        treeselection = self.treeview.get_selection()
    	model, treeiter = treeselection.get_selected()
        device = {}
        complete_dev = {}

        if treeiter != None:

             if model[treeiter][0] == True:
       	          return

             if model[treeiter][3] != '':
                  device['Vendor'] = model[treeiter][2]

             if model[treeiter][4] != '':
                  device['Product'] = model[treeiter][3]
 
             key = model[treeiter][2]
             self.device_monitor.add_to_known_device(key, device)
             model.set_value(treeiter, 0, True)

        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "A USB device must be selected!")
            dialog.format_secondary_text("The selected USB device will be written to a 'know_hosts' file")
            dialog.run()



    # Check new devices
    def refresh(self, device):
        treeselection = self.treeview.get_selection()
        model, treeiter = treeselection.get_selected()    


        if treeiter != None:
            index = (model.get_path(treeiter)).get_indices()[0]
       	
        action = device.action
        dev = device.sys_name.split(':')[0]
        (dev_name, key) = self.device_monitor.extract_information(device)

        if action == 'add':
            self.device_monitor.busID_key_map[dev] = key
            self.device_monitor.add_connected_device(key, dev_name, dev)

            if key not in self.device_monitor.known_devices.keys():
                self.usb_list.append([False, True, key, dev_name['Vendor'],
															dev_name['Product']])
				
            else:
                self.usb_list.append([True, True, key, dev_name['Vendor'],
														   dev_name['Product']])

        if action == 'remove':
            to_delete_key = self.device_monitor.remove_connected_device(dev)
            self.remove_from_usb_list(to_delete_key)
			
        if treeiter != None:
              self.treeview.set_cursor(index)
	

        return True
  
    # Remove one entry from the usb_list (to remove from the gtk tree)
    def remove_from_usb_list(self, key):
		for entry in self.usb_list:
			if entry[2] == key:
				entry.model.remove(entry.iter)
				break


    def usb_filter_func(self, model, iter, data):
        """Tests if the usb is connected, known device or unknown"""
        if self.current_filter_usb is None or self.current_filter_usb == "None":
            return True

        elif self.current_filter_usb == "Known Devices":
            	return model[iter][0] == True

        elif self.current_filter_usb == "Unknown Devices":
                return model[iter][0] == False

        else:
                return model[iter][1] == True


    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        self.current_filter_usb = widget.get_label()
        print("%s usb selected!" % self.current_filter_usb)
        self.usb_filter.refilter()

    def quit_monitor(self):
        self.device_monitor.usb_monitor_stop()
        print self.device_monitor.known_devices


if __name__ == "__main__":
    GObject.threads_init()
    win = USB_ViewFilterWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    win.quit_monitor()
