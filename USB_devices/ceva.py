import usb
for dev in usb.core.find(find_all=True):
	print dev
	import pdb; pdb.set_trace()
#	print "Manufacturer:", dev.manufacturer
#	print "Vendor:", dev.iProduct
	print "  idVendor: %d (%s)" % (dev.idVendor, hex(dev.idVendor))
	print "  idProduct: %d (%s)" % (dev.idProduct, hex(dev.idProduct))
