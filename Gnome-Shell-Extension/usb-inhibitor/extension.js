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
  <interface name="org.gnome.USBBlocker.inhibit">\
    <method name="get_status">\
		<arg type="b" direction="out" />\
	</method>\
    <method name="start_monitor">\
    </method>\
    <method name="stop_monitor">\
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
        
        this.actor.connect('button-press-event', Lang.bind(this, function() { this.toggleState("HAND"); } ));
        this.actor.add_actor(this._icon);
        this.actor.add_style_class_name('panel-status-button');

       
        this._usbBlocker = new DBusUSBBlockerProxy(Gio.DBus.system,
                                                          'org.gnome.USBBlocker',
                                                          '/org/gnome/USBBlocker');
        this._usbBlocker.get_statusRemote(Lang.bind(this, function(dbus_status) {
            this._byHand = this._state = (dbus_status == "true");
            if (this._state) {
                this._icon.icon_name = EnabledIcon;
            } else this._icon.icon_name = DisabledIcon;
        }));


        this._lockOrig = ScreenShield.ScreenShield.prototype.lock;
        this._fromLock = false;
        this._state = false;
        this._byHand = false;
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

            if (who === "HAND")
                this._byHand = false;

			this._usbBlocker.stop_monitorRemote();
			this._icon.icon_name = DisabledIcon;
            this._state = false;
            if (this._settings.get_boolean(SHOW_NOTIFICATIONS))
			    Main.notify(_("USB blocking disabled"));     

        }
        else {

            if (who === "HAND")
                this._byHand = true;

			this._usbBlocker.start_monitorRemote();
			this._icon.icon_name = EnabledIcon;
			this._state = true;
            
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
