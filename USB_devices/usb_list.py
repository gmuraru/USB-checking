#! /usr/bin/python


from gi.repository import Gtk
import usb_checking 





class USB_connected(Gtk.Window):
	
	def __init__(self):
		column = Gtk.TreeViewColumn("Connected USB device information")
		ID = Gtk.CellRendererText()
		Device = Gtk.CellRendererText()

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


