#! /usr/bin/python

from gi.repository import Gtk
import usb_checking
import gobject

# Modified tutorial http://python-gtk-3-tutorial.readthedocs.org/en/latest/treeview.html
class USB_ViewFilterWindow(Gtk.Window):

    def __init__(self):
        self.val = 0
        print "hi"
      	Gtk.Window.__init__(self, title = "Treeview Filter Demo")
        Device = usb_checking.USB_ports()
        
        Device.get_known_devices()
        Device.get_connected_devices()

        devices = []
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.usb_list = Gtk.ListStore(bool, bool, str, str, str)
       
        for dev in Device.connected_devices.keys():
            vendor = ""
            product = ""
            if "Vendor" in Device.connected_devices[dev].keys():
                vendor = Device.connected_devices[dev]["Vendor"]	
            if "Product" in Device.connected_devices[dev].keys():
                product = Device.connected_devices[dev]["Product"]

            if dev in Device.known_devices.keys():
            	self.usb_list.append((True, True, dev, vendor, product))
            else:
                self.usb_list.append((False, True, dev, vendor, product))
		
        for dev in Device.known_devices.keys():
            if dev in Device.connected_devices.keys():
                continue

            vendor = ""
            product = ""
            if "Vendor" in Device.known_devices[dev].keys():
                vendor = Device.known_devices[dev]["Vendor"]	
            if "Product" in Device.known_devices[dev].keys():
                product = Device.known_devices[dev]["Product"]
            if dev in Device.connected_devices.keys():
                continue
		   
            self.usb_list.append((True, False, dev, vendor, product))

        self.current_filter_usb = None
        #Creating the filter, feeding it with the usb_list model
        self.usb_filter = self.usb_list.filter_new()
        #setting the filter function
        self.usb_filter.set_visible_func(self.usb_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.usb_filter)
        for i, column_title in enumerate(["Known Device", "Connected", "ID", "Vendor", "Product"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        #creating buttons to filter by device state, and setting up their events
        self.buttons = list()
        for usb_type in ["Connected Devices", "Known Devices", "Unknown Devices"]:
            button = Gtk.Button(usb_type)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
 
        button = Gtk.Button("Refresh")
        self.buttons.append(button)
        button.connect("clicked", self.refresh)
    
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

	
   
        self.show_all()

    def refresh(self):
        Device.get_known_devices()
        Device.get_connected_devices()
        Device.get_new_devices()


    def usb_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_usb is None or self.current_filter_usb == "None":
            return True
        elif self.current_filter_usb == "Known Devices":
            	return model[iter][0] == True
        elif self.current_filter_usb == "Unknown Devices":
                 return model[iter][1] == False
        else:
                return model[iter][1] == True

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        self.current_filter_usb = widget.get_label()
        print("%s usb selected!" % self.current_filter_usb)
        self.usb_filter.refilter()


win = USB_ViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
