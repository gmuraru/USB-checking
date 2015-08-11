#! /usr/bin/env python3

import threading
from gi.repository import Gtk, GObject, GLib
from usb_checking import RunningMode, USB_ports
from pyudev import MonitorObserver
import read_device
import usb.core
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
        self.usb_list = Gtk.ListStore(str, bool, str, str, str)
       
        self.current_filter_usb = None
        # Creating the filter, feeding it with the usb_list model
        self.usb_filter = self.usb_list.filter_new()
        # Setting the filter function
        self.usb_filter.set_visible_func(self.usb_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.usb_filter)

        col = Gtk.TreeViewColumn("Known Device", Gtk.CellRendererPixbuf(), stock_id = 0)
        self.treeview.append_column(col)

		#col.set_cell_data_func( cell, self._render_icon)
        for i, column_title in enumerate(["Connected", "DescriptorInfo", "Manufacturer", "Product"]):
            print (str(i) + "     " + column_title)
            i = i + 1
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

        # Remove trusted device
        button = Gtk.Button("Remove selected")
        self.buttons.append(button)
        button.connect("clicked", self.remove_from_known_devices)

        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)

        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        
        self.scrollable_treelist.add(self.treeview)


        self.first_populate_table()
        self.show_all()	
        self.observer.start()


    def first_populate_table(self):

        for device_id in self.device_monitor.known_devices.keys():

            if device_id in self.device_monitor.connected_devices.keys():
                self.usb_list.append([Gtk.STOCK_YES, True,
							self.device_monitor.known_devices[device_id][1],
                            self.device_monitor.known_devices[device_id][0]["Manufacturer"],
                            self.device_monitor.known_devices[device_id][0]["Product"]])

            else:
                self.usb_list.append([Gtk.STOCK_YES, False,
							self.device_monitor.known_devices[device_id][1],
							self.device_monitor.known_devices[device_id][0]["Manufacturer"],
							self.device_monitor.known_devices[device_id][0]["Product"]])
				

        for device_id in self.device_monitor.connected_devices.keys():
			
            if device_id not in self.device_monitor.known_devices.keys():
                print (self.device_monitor.connected_devices[device_id][1])
                self.usb_list.append([Gtk.STOCK_NO, True,
							 self.device_monitor.connected_devices[device_id][1],
                             self.device_monitor.connected_devices[device_id][0]["Manufacturer"],
                             self.device_monitor.connected_devices[device_id][0]["Product"]])
                

    # Write selected device to file
    # The device would be kept in a buffer until the program exits
    def write_to_known_devices(self, button):

        treeselection = self.treeview.get_selection()
        model, treeiter = treeselection.get_selected()
        device = {}

        print ("HERE it is ")
        if treeiter != None:

            if model[treeiter][0] == Gtk.STOCK_YES:
       	        return

            if model[treeiter][3]:
                device["Manufacturer"] = model[treeiter][3]

            if model[treeiter][4]:
                device["Product"] = model[treeiter][4]

            print("HEllo there !")
            print(device["Product"])
            print(device["Manufacturer"])
            
            busnum, devnum = model[treeiter][2].split("\n")[0].split("Bus")[1].split("Address")
            devnum = devnum.split()[0]

            dev = usb.core.find(address=int(devnum), bus=int(busnum))

            dev_id = read_device.get_descriptors(dev)

            self.device_monitor.add_to_known_device(dev_id, device, dev)
            model.set_value(treeiter, 0, Gtk.STOCK_YES)


        else:

            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "A USB device must be selected!")
            dialog.format_secondary_text("The selected USB device will be written to a 'know_hosts' file")
            dialog.run()
            
    # Remove selected device from file
    def remove_from_known_devices(self, button):

        treeselection = self.treeview.get_selection()
        model, treeiter = treeselection.get_selected()
        device = {}

        if treeiter != None:

             if model[treeiter][0] == Gtk.STOCK_NO:
       	          return

             if model[treeiter][3]:
                  device["Manufacturer"] = model[treeiter][2]

             if model[treeiter][4]:
                  device["Product"] = model[treeiter][3]
            
             busnum, devnum = model[treeiter][2].split("\n")[0].split("Bus")[1].split("Address")
             devnum = devnum.split()[0]

             dev = usb.core.find(address=int(devnum), bus=int(busnum))
             dev_id = read_device.get_descriptors(dev)

             self.device_monitor.known_devices.pop(dev_id)

             model.set_value(treeiter, 0, Gtk.STOCK_NO)


        else:

             dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
             Gtk.ButtonsType.CANCEL, "A USB device must be selected!")
            
             dialog.format_secondary_text("The selected USB device was removed")
             dialog.run()



    # Check new devices
    def refresh(self, device):
        treeselection = self.treeview.get_selection()
        model, treeiter = treeselection.get_selected()    


        if treeiter != None:
            index = (model.get_path(treeiter)).get_indices()[0]
       	
        action = device.action
        bus_id = device.sys_name


        if action == 'add':

            devnum = int(device.attributes.get("devnum"))
            busnum = int(device.attributes.get("busnum"))
			
            dev = usb.core.find(address=devnum, bus=busnum)

            dev_id = read_device.get_descriptors(dev)
            dev_name = read_device.get_device_name(device.attributes)

            self.device_monitor.add_connected_device(bus_id, dev_id, dev_name, dev)

            if dev_id not in self.device_monitor.known_devices.keys():
                self.usb_list.append([Gtk.STOCK_NO, True, str(dev), dev_name["Manufacturer"],
    				    dev_name["Product"]])
				
            else:
                self.usb_list.append([Gtk.STOCK_YES, True, str(dev), dev_name["Manufacturer"],
				    dev_name["Product"]])

        if action == 'remove':
            bus_id = self.device_monitor.remove_connected_device(dev)
            self.remove_from_usb_list(bus_id)
			
        if treeiter != None:
              self.treeview.set_cursor(index)
	
        return True
  
    # Remove one entry from the usb_list (to remove from the gtk tree)
    def remove_from_usb_list(self, bus_id):
        for entry in self.usb_list:
            if entry[2] == bus_id:
                entry.model.remove(entry.iter)
                break


	# Tests if the usb is connected, known device or unknown
    def usb_filter_func(self, model, iter, data):

        if self.current_filter_usb is None or self.current_filter_usb == "None":
            return True

        elif self.current_filter_usb == "Known Devices":
            return model[iter][0] == Gtk.STOCK_YES

        elif self.current_filter_usb == "Unknown Devices":
            return model[iter][0] == False

        else:
            return model[iter][1] == True


    # Called on any of the button clicks
    def on_selection_button_clicked(self, widget):
        self.current_filter_usb = widget.get_label()
        print("{} usb selected!".format(self.current_filter_usb))
        self.usb_filter.refilter()


    def quit_monitor(self):
        self.device_monitor.usb_monitor_stop()
        print("The know device list {}".format(self.device_monitor.known_devices))


if __name__ == "__main__":
    GObject.threads_init()
    win = USB_ViewFilterWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    win.quit_monitor()
