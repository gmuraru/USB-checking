#! /usr/bin/env python3

import re


## Needed information when getting attributes
device_descriptor = ["bLength", 
			 "bDescriptorType",
			 "bcdUSB",
			 "bDeviceClass", 
			 "bDeviceSubClass",
			 "bDeviceProtocol",
			 "bMaxPacketSize0",
			 "idVendor",
			 "idProduct",
			 "bcdDevice",
			 "iManufacturer",
			 "iProduct",
			 "iSerialNumber", 
			 "bNumConfigurations"]


configuration_descriptor = ["bLength",
				"bDescriptorType",
				"wTotalLength",
				"bNumInterfaces",
				"bConfigurationValue",
				"iConfiguration",
				"bmAttributes",
				"bMaxPower"]

interface_descriptor = ["bLength",
			"bDescriptorType",
			"bInterfaceNumber",
			"bAlternateSetting",
			"bNumEndpoints",
			"bInterfaceClass",
			"bInterfaceSubClass",
			"bInterfaceProtocol",
			"iInterface"]

endpoint_descriptor = ["bLength",
			   "bDescriptorType",
			   "bEndpointAddress",
			   "bmAttributes",
			   "wMaxPacketSize",
			   "bInterval"]

separator = ":"
name_device = ["Manufacturer", "Product"]

def get_descriptors(device):
	information = ""
	for dev_descriptor in device_descriptor:
		information += str(device.__getattribute__(dev_descriptor)) + separator

	for configuration in device.configurations():
		for dev_config in configuration_descriptor:
			information += str(configuration.__getattribute__(dev_config)) + separator

	for interface in configuration.interfaces():
		for dev_interf in interface_descriptor:
			information += str(interface.__getattribute__(dev_interf)) + separator

		for endpoint in interface.endpoints():
			for dev_endpoint in endpoint_descriptor:
				information += str(endpoint.__getattribute__(dev_endpoint)) + separator

	return information[:-1]


def extract_information(device):
	information = {}
	key = ""

	attributes = device.attributes

	for info in self.looked_information:

		if info in attributes:
			key += attributes.get(info).decode('utf-8')

		if info == "idProduct":
			dev_idProduct = attributes.get(info).decode('utf-8')

		elif info == "idVendor":
			dev_idVendor = attributes.get(info).decode('utf-8')

		key += self.separator


	# Eliminate the last ":"
	key = key[:-1]


	# The break occured and we can not get a piece of information
	# about the usb device

	#print("This is the key {}".format(key))
	
	dev_name = self.get_device_name(attributes)
	return (dev_name, key)


# Place the device name in the third and forth column
def get_device_name(attributes):
	# Device product and vendor
	
	prod_vendor = { "Manufacturer": "",
			"Product": ""}
	
	vendorFound = False
	productFound = False

	# Check if Product and Vendor are in the device attributes
	if name_device[0].lower() in attributes:
		prod_vendor[name_device[0]] = attributes.get("manufacturer")#.decode('ascii')
		vendorFound = True
		
	if name_device[1].lower() in attributes:
		prod_vendor[name_device[1]] = attributes.get("product")#.decode('ascii')
		productFound = True
	
	if vendorFound and productFound:
		return prod_vendor


	idVendor = attributes.get("idVendor").decode('ascii')
	idProduct = attributes.get("idProduct").decode("ascii")


	if idProduct == None or idVendor == None:
		return prod_vendor

	# If they are not in the attributes check a file (lsusb uses this file
	# for naming connected devices)
	regex_idVendor = re.compile('^{}  .*'.format(idVendor))
	regex_idProduct = re.compile('\t{}  .*'.format(idProduct))

	# The file has the format utf-8
	try:	
		f_in = open('/var/lib/usbutils/usb.ids', 'rt', encoding='utf-8',
			errors='replace')

	except TypeError:
		import codecs
		f_in = codecs.open('/var/lib/usbutils/usb.ids', 'rt', encoding='utf-8',
			errors='replace')


	for line_vendor in f_in:
		res = regex_idVendor.match(line_vendor)

		if res:
			if not prod_vendor["Manufacturer"]:
				prod_vendor["Manufacturer"] = (res.group(0)).split("  ")[1]

			for line_product in f_in:
				res = regex_idProduct.match(line_product)

				if res:
					if not prod_vendor["Product"]:
						prod_vendor["Product"] = (res.group(0)).split("  ")[1]
			
						return prod_vendor
	
	f_in.close()

	return prod_vendor
