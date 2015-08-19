#! /usr/bin/env python3

import re

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
