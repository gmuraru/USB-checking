#! /usr/bin/python3

import threading
from gi.repository import Gtk, GObject, GLib
import usb_checking
import time
import gobject

# Modified tutorial http://python-gtk-3-tutorial.readthedocs.org/en/latest/treeview.html
class USB_ViewFilterWindow(Gtk.Window):

    Device = usb_checking.USB_ports()
    
    def __init__(self):
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
 	
	# Refresh button
        button = Gtk.Button("Refresh")
        self.buttons.append(button)
        button.connect("clicked", self.refresh)
	    
	# Write to know devices
        button = Gtk.Button("Write selected")
        self.buttons.append(button)
        button.connect("clicked", self.write)
        
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)


        self.show_all()	
	        
	GObject.timeout_add(200, self.refresh)	


    # Write selected device to file
    def write(self, button):
        treeselection = self.treeview.get_selection()
    	model, treeiter = treeselection.get_selected()
        device = {}
        complete_dev = {}
        print treeiter
        if treeiter != None:
             if model[treeiter][0] == True:
       	          return
             if model[treeiter][3] != '':
                  device['Vendor'] = model[treeiter][2]
             if model[treeiter][4] != '':
                  device['Product'] = model[treeiter][3]
 
             complete_dev[model[treeiter][2]] = device
             self.Device.write_device(complete_dev)
        else:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, "A USB device must be selected!")
            dialog.format_secondary_text("The selected USB device will be written to a 'know_hosts' file")
            dialog.run()



    # Check new devices
    def refresh(self):
        treeselection = self.treeview.get_selection()
        model, treeiter = treeselection.get_selected()    
        if treeiter != None:
            index = (model.get_path(treeiter)).get_indices()[0]

        self.Device.reset()	
        self.usb_list.clear()
        self.Device.get_known_devices()
        self.Device.get_connected_devices()
        self.Device.get_new_devices()
            
        for dev in self.Device.connected_devices.keys():
            vendor = ""
            product = ""
            if "Vendor" in self.Device.connected_devices[dev].keys():
                vendor = self.Device.connected_devices[dev]["Vendor"]	
            if "Product" in self.Device.connected_devices[dev].keys():
                product = self.Device.connected_devices[dev]["Product"]

            if dev in self.Device.known_devices.keys():
      	        self.usb_list.append((True, True, dev, vendor, product))
            else:
                self.usb_list.append((False, True, dev, vendor, product))
		
        for dev in self.Device.known_devices.keys():
             if dev in self.Device.connected_devices.keys():
                continue

             vendor = ""
             product = ""
               
             if "Vendor" in self.Device.known_devices[dev].keys():
                 vendor = self.Device.known_devices[dev]["Vendor"]	
             if "Product" in self.Device.known_devices[dev].keys():
                 product = self.Device.known_devices[dev]["Product"]
             if dev in self.Device.connected_devices.keys():
                 continue
		   
             self.usb_list.append((True, False, dev, vendor, product))

        if treeiter != None:
              self.treeview.set_cursor(index)
        
        return True
  
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


if __name__ == "__main__":
        GObject.threads_init()
	win = USB_ViewFilterWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
