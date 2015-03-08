#! /usr/bin/python

from gi.repository import Gtk
import usb_checking 





class USB_window(Gtk.Window):
	
	def __init__(self):
		renderer = Gtk.CellRendererText()
		model = Gtk.ListStore(str)
		model.append(["Benjamin"])
		model.append(["Charles"])
		model.append(["alfred"])
		model.append(["Alfred"])
		model.append(["David"])
		model.append(["charles"])
		model.append(["david"])
		model.append(["benjamin"])

		treeView = Gtk.TreeView(model)

		cellRenderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn("Title", renderer, text=0)



		usb = usb_checking.USB_ports()
		Gtk.Window.__init__(self, title = "USB detecting")
		
		self.box = Gtk.Box(spacing=6)
		self.add(self.box)
		# Button for printing all known devices
		self.button1 = Gtk.Button(label = "All known devices")
		self.button1.connect("clicked", self.list_known_devices)	
		self.box.pack_start(self.button1, True, True, 0)

		self.button2 = Gtk.Button(label = "All connected devices")
		self.button2.connect("clicked", self.list_connected_devices)
		self.box.pack_start(self.button2, True, True, 0)

		self.button3 = Gtk.Button(label = "Add connected devices to repository")
		self.button3.connect("clicked", self.add_connected_devices)
		self.box.pack_start(self.button3, True, True, 0)

		self.button4 = Gtk.Button(label = "Delete repository")
		self.button4.connect("clicked", self.delete_repository)
		self.box.pack_start(self.button4, True, True, 0)

	def list_known_devices():
		pass
	
	def list_connected_devices():
		pass

	def add_connected_devices():
		pass
	
	def delete_repository():
		pass	
		

win = USB_window()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
