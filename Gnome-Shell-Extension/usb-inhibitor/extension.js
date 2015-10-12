/**
*    Copyright 2015 George-Cristian Muraru <murarugeorgec@gmail.com>
*    Copyright 2015 Tobias Mueller <muelli@cryptobitch.de>
*
*    This file is part of USB Inhibitor.
*
*    USB Inhibitor is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    USB Inhibitor and the afferent extension is distributed in the hope that it
*    will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with USB Inhibitor.  If not, see <http://www.gnu.org/licenses/>.
**/


const ScreenShield = imports.ui.screenShield;
const Lang = imports.lang;                                                      
const St = imports.gi.St;                                                       
const GLib = imports.gi.GLib;                                                   
const Gio = imports.gi.Gio;                                                     
const Main = imports.ui.main;                                                   
const Mainloop = imports.mainloop;                                              
const PanelMenu = imports.ui.panelMenu;                                         
const PopupMenu = imports.ui.popupMenu;
const Shell = imports.gi.Shell;                                                 
const MessageTray = imports.ui.messageTray;                                     
const Atk = imports.gi.Atk;                                                     
const Config = imports.misc.config;


const Me = imports.misc.extensionUtils.getCurrentExtension();                   
const Convenience = Me.imports.convenience; 

const DisabledIcon = 'usb-unlock-new';
const EnabledIcon = 'usb-lock-new';

const SHOW_NOTIFICATIONS="show-notifications";

const IndicatorName = "USBInhibitor";

const DBusUSBBlockerIface = '<node>\
  <interface name="org.gnome.USBInhibit">\
    <method name="get_status">\
	<arg type="b" direction="out" />\
    </method>\
    <method name="start_inhibit">\
    </method>\
    <method name="stop_inhibit">\
    </method>\
    <method name="add_nonblock_device">\
	<arg type="n" direction="in" />\
    </method>\
    <method name="remove_nonblock_device">\
	<arg type="n" direction="in"/>\
    </method>\
  </interface>\
</node>';

const DBusUSBBlockerProxy = Gio.DBusProxy.makeProxyWrapper(DBusUSBBlockerIface);


let USBBlocker;

// Adapted from https://github.com/eonpatapon/gnome-shell-extension-caffeine     
const Extension = new Lang.Class({
    Name: IndicatorName,
    Extends: PanelMenu.Button,

    _init: function() {

        this.parent(null, IndicatorName);
        this._settings = Convenience.getSettings();

	this._icon = new St.Icon({
		style_class: 'system-status-icon',
       	});
        
        this.actor.add_actor(this._icon);
        this.actor.add_style_class_name('panel-status-button');

	       
        this._usbBlocker = new DBusUSBBlockerProxy(Gio.DBus.session,
                                                         'org.gnome.USBInhibit',
                                                         '/org/gnome/USBInhibit');

	
	subMenu = new PopupMenu.PopupSubMenuMenuItem(_("Allow devices"));


	// Some USB Classes (bDeviceClass)
	Audio = new PopupMenu.PopupSwitchMenuItem(_("Audio"));
	HID = new PopupMenu.PopupSwitchMenuItem(_("HID"));
	Printer = new PopupMenu.PopupSwitchMenuItem(_("Printer"));
	MassStorage = new PopupMenu.PopupSwitchMenuItem(_("Mass Storage"));
	Video = new PopupMenu.PopupSwitchMenuItem(_("Video"));


	HID.connect('activate', Lang.bind(this, function() { this.switchAction(3, HID); }));
	Printer.connect('activate', Lang.bind(this, function() { this.switchAction(7, Printer); }));
	MassStorage.connect('activate', Lang.bind(this, function() { this.switchAction(8, MassStorage); }));
	Video.connect('activate', Lang.bind(this, function() { this.switchAction(14, Video); }));
	Audio.connect('activate', Lang.bind(this, function() { this.switchAction(1, Audio); }));


	subMenu.menu.addMenuItem(HID);
	subMenu.menu.addMenuItem(Printer);
	subMenu.menu.addMenuItem(MassStorage);
	subMenu.menu.addMenuItem(Video);
	subMenu.menu.addMenuItem(Audio);

	this.menu.addMenuItem(subMenu);
	this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this._usbBlocker.get_statusRemote(Lang.bind(this, function(dbus_status) {
            this._byHand = this._state = (dbus_status == "true");
	    let label_name; 

	    if (this._state) {
                this._icon.icon_name = EnabledIcon;
		label = new PopupMenu.PopupMenuItem(_("Deactivate"));
		label.connect('activate', Lang.bind(this, function() { this.toggleState("USER"); }));
		this.menu.addMenuItem(label);
            } else {
		this._icon.icon_name = DisabledIcon;
		label = new PopupMenu.PopupMenuItem(_("Activate"));
		label.connect('activate', Lang.bind(this, function() { this.toggleState("USER"); }));
		this.menu.addMenuItem(label);
	    }
	
	}));

        this._lockOrig = ScreenShield.ScreenShield.prototype.lock;
        this._fromLock = false;
        this._byHand = false;
    },



    switchAction: function(code, caller) {
	if (caller._switch.state)
		this._addBDeviceClass(code);
	else this._removeBDeviceClass(code, "USER");
    },


    _addBDeviceClass: function(code) {
	this._usbBlocker.add_nonblock_deviceRemote(code);
    },


    _removeBDeviceClass: function(code, who) {
	this._usbBlocker.remove_nonblock_deviceRemote(code);	

    },


    enable: function() {
        this.actor.show();

        if (this._fromLock)
            if (!this._byHand)
                this.toggleState("LOCKSCREEN");

        ScreenShield.ScreenShield.prototype.lock = Lang.bind(this,
            function(animate) {
                this._fromLock = true;

                this._lockOrig.call(Main.screenShield, animate);
            });


        this._fromLock = false;
    },


    toggleState: function(who) {
	
        if (this._state === true) {

		if (who === "USER")
			this._byHand = false;

		this._usbBlocker.stop_inhibitRemote();
		this._icon.icon_name = DisabledIcon;
		this._state = false;
		this.menu._getMenuItems()[2].label.set_text("Activate");
            
		if (this._settings.get_boolean(SHOW_NOTIFICATIONS))
			Main.notify(_("USB blocking disabled"));     

        }
        else {

		if (who === "USER")
			this._byHand = true;

		this._usbBlocker.start_inhibitRemote();
		this._icon.icon_name = EnabledIcon;
		this._state = true;
		this.menu._getMenuItems()[2].label.set_text("Deactivate");
            
		if (this._settings.get_boolean(SHOW_NOTIFICATIONS))
			Main.notify(_("USB blocking enabled"));
        }
    },


    // Currently the user can change the state even when the screen is locked
    disable: function() {
        if (this._fromLock) {
            if (!this._state)
                this.toggleState("LOCKSCREEN");
            this.actor.hide();
        }

        else if (!this._fromLock) {
            if (this._state)
                this.toggleState("LOCKSCREEN");
            return true;
       }
    
        ScreenShield.ScreenShield.prototype.lock = this._lockOrig;
        return false;
    }
});


function init(extensionMeta) {
    theme = imports.gi.Gtk.IconTheme.get_default();                         
    theme.append_search_path(extensionMeta.path + "/icons"); 
}


function enable() {
    if (USBBlocker == null) {
        USBBlocker = new Extension();
        Main.panel.addToStatusArea(IndicatorName, USBBlocker);               
    }

    return USBBlocker.enable();
}


function disable() {
    if (USBBlocker.disable()) {
        USBBlocker.destroy();
        USBBlocker = null;
    }
}
