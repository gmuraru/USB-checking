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
/*
const HIDDevice = 
const MASSStorageDevice = 
const AudioDevice = 
const VideoDevice = 
*/

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

const IndicatorName = "USBInhibitor";

let USBBlocker;

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
        this.actor.connect('button-press-event', Lang.bind(this, function() { this.toggleState("HAND"); } ));

       
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
        Main.notify(_("First disable " + this._fromLock));
        if (!this._state && this._fromLock) {
            this.toggleState("LOCKSCREEN");
        }
         
        if (!this._fromLock) {
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
