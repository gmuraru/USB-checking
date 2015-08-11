/*
const St = imports.gi.St;                                                       
const PanelMenu = imports.ui.panelMenu;                                         
const Lang = imports.lang;
const Main = imports.ui.main;
const Atk = imports.gi.Atk;
const Gio = imports.gi.Gio;
*/

const ScreenShield = imports.ui.screenShield;
const Lang = imports.lang;                                                      
const St = imports.gi.St;                                                       
const GLib = imports.gi.GLib;                                                   
const Gio = imports.gi.Gio;                                                     
const Main = imports.ui.main;                                                   
const Mainloop = imports.mainloop;                                              
const PanelMenu = imports.ui.panelMenu;                                         
const Shell = imports.gi.Shell;                                                 
const MessageTray = imports.ui.messageTray;                                     
const Atk = imports.gi.Atk;                                                     
const Config = imports.misc.config;



const DisabledIcon = 'usb-unlock-new';
const EnabledIcon = 'usb-lock-new';

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


const Extension = new Lang.Class({
    Name: 'Extension',
    Extends: PanelMenu.Button,

    _init: function() {
        /*
        theme = imports.gi.Gtk.IconTheme.get_default();
        theme.append_search_path(extensionMeta.path + ".");
        */

        this.parent(null, 'Extension');
        this.actor.accessible_role = Atk.Role.TOGGLE_BUTTON;

        this._lockOrig = ScreenShield.ScreenShield.prototype.lock;
        this._fromLock = false;

        this._state = false;


		this._icon = new St.Icon({
       	    style_class: 'system-status-icon',
       	});
        
        this.actor.add_actor(this._icon);
        this.actor.add_style_class_name('panel-status-button');
        this.actor.connect('button-press-event', Lang.bind(this, this.toggleState));

       
        this._usbBlocker = new DBusUSBBlockerProxy(Gio.DBus.system,
                                                          'org.gnome.USBBlocker',
                                                          '/org/gnome/USBBlocker');


        this._usbBlocker.get_statusRemote(Lang.bind(this, function(dbus_status) {
            this._state = (dbus_status == "true");

            if (this._state) {
                this._icon.icon_name = EnabledIcon;
            } else this._icon.icon_name = DisabledIcon;
        }));
     
        Main.panel.addToStatusArea('Extension', this);               

    },

    enable: function() {
        this.actor.show();

        if (this._fromLock)
            this.toggleState();

        ScreenShield.ScreenShield.prototype.lock = Lang.bind(this,
            function(animate) {
                this._fromLock = true;

                this._lockOrig.call(Main.screenShield, animate);
            });


        this._fromLock = false;
    },

    toggleState: function() {
        if (this._state === true) {
			this._usbBlocker.stop_monitorRemote();
			this._icon.icon_name = DisabledIcon;
			Main.notify(_("USB blocking disabled"));     
			this._state = false;

        }
        else {
			this._usbBlocker.start_monitorRemote();
			this._icon.icon_name = EnabledIcon;
			Main.notify(_("USB blocking enabled"));
			this._state = true;
        }
    },


    disable: function() {
        
      //  this.actor.hide();
        if (!this._state) {
            Main.notify(_("Was not blocked"));
            this.toggleState();
        }

        ScreenShield.ScreenShield.prototype.lock = this._lockOrig;
    }
});

function init(extensionMeta) {
    theme = imports.gi.Gtk.IconTheme.get_default();                         
    theme.append_search_path(extensionMeta.path + "/icons"); 
    return new Extension();
}
