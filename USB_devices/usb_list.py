#! /usr/bin/python

from gi.repository import Gtk
import usb_checking


#list of tuples for each software, containing the software name, initial release, and main programming languages used
software_list = [("Firefox", 2002,  "C++"),
                 ("Eclipse", 2004, "Java" ),
                 ("Pitivi", 2004, "Python"),
                 ("Netbeans", 1996, "Java"),
                 ("Chrome", 2008, "C++"),
                 ("Filezilla", 2001, "C++"),
                 ("Bazaar", 2005, "Python"),
                 ("Git", 2005, "C"),
                 ("Linux Kernel", 1991, "C"),
                 ("GCC", 1987, "C"),
                 ("Frostwire", 2004, "Java")]

class USB_ViewFilterWindow(Gtk.Window):

    def __init__(self):
      	Gtk.Window.__init__(self, title="Treeview Filter Demo")
        Device = usb_checking.USB_ports()
        
        Device.get_known_devices()
        Device.get_connected_devices()
        Device.get_new_devices()

        devices = []
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.usb_list = Gtk.ListStore(bool, bool, str, str, str)
       
        for dev in Device.known_devices.keys():
            vendor = ""
            product = ""
            if "Vendor" in Device.known_devices[dev].keys():
                vendor = Device.known_devices[dev]["Vendor"]	
            if "Product" in Device.known_devices[dev].keys():
                product = Device.known_devices[dev]["Product"]
            self.usb_list.append((True, True, dev, vendor, product))


        self.current_filter_usb = None
        #Creating the filter, feeding it with the liststore model
        self.usb_filter = self.usb_list.filter_new()
        #setting the filter function, note that we're not using the
        self.usb_filter.set_visible_func(self.usb_filter_func)

        self.treeview = Gtk.TreeView.new_with_model(self.usb_filter)
        for i, column_title in enumerate(["Known Device", "Connected", "ID", "Vendor", "Product"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        #creating buttons to filter by programming language, and setting up their events
        self.buttons = list()
        for prog_language in ["Connected Devices", "Known Devices", "Unknown Devices"]:
            button = Gtk.Button(prog_language)
            self.buttons.append(button)
            button.connect("clicked", self.on_selection_button_clicked)

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def usb_filter_func(self, model, iter, data):
        """Tests if the language in the row is the one in the filter"""
        if self.current_filter_usb is None or self.current_filter_usb == "None":
            return True
        elif self.current_filter_usb == "Known Device":
            	return model[iter][0] == self.current_filter_usb
        else:
				return model[iter][1] == self.current_filter_usb

    def on_selection_button_clicked(self, widget):
        """Called on any of the button clicks"""
        self.current_filter_usb = widget.get_label()
        print("%s usb selected!" % self.current_filter_usb)
        self.usb_filter.refilter()


win = USB_ViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
