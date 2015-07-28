/* -*- mode: js2 - indent-tabs-mode: nil - js2-basic-offset: 4 -*- */
/*jshint multistr:true */
/*jshint esnext:true */
/*global imports: true */
/*global global: true */
/*global log: true */
/*global logError: true */
/**
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
**/

'use strict';

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

const INHIBIT_APPS_KEY = 'inhibit-apps';
const SHOW_INDICATOR_KEY = 'show-indicator';
const SHOW_NOTIFICATIONS_KEY = 'show-notifications';
const USER_ENABLED_KEY = 'user-enabled';
const FULLSCREEN_KEY = 'enable-fullscreen';

const Gettext = imports.gettext.domain('gnome-shell-extension-caffeine');
const _ = Gettext.gettext;

const Me = imports.misc.extensionUtils.getCurrentExtension();
const Convenience = Me.imports.convenience;

const DBusUSBBlockerIface = '<node>\
  <interface name="org.gnome.USBBlocker.monitor">\
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

const DBusScreenSaverIface = '<node>\
	<interface name="org.gnome.ScreenSaver">\
	  <signal name="ActiveChanged">\
	    <arg type="b" direction="out" />\
	  </signal>\
	</interface>\
</node>';
  			  

const DBusScreenSaverProxy = Gio.DBusProxy.makeProxyWrapper(DBusScreenSaverIface);

const IndicatorName = "Caffeine";
const DisabledIcon = 'usb-unlock-new';
const EnabledIcon = 'usb-lock-new';

let CaffeineIndicator;
let ShellVersion = parseInt(Config.PACKAGE_VERSION.split(".")[1]);

const Caffeine = new Lang.Class({
    Name: IndicatorName,
    Extends: PanelMenu.Button,

    _init: function(metadata, params) {
        this.parent(null, IndicatorName);
        this.actor.accessible_role = Atk.Role.TOGGLE_BUTTON;

        this._settings = Convenience.getSettings();
        this._settings.connect("changed::" + SHOW_INDICATOR_KEY, Lang.bind(this, function() {
            if (this._settings.get_boolean(SHOW_INDICATOR_KEY))
                this.actor.show();
            else
                this.actor.hide();
        }));
        if (!this._settings.get_boolean(SHOW_INDICATOR_KEY))
            this.actor.hide();

        this._usbBlocker = new DBusUSBBlockerProxy(Gio.DBus.system,
                                                          'org.gnome.USBBlocker',
                                                          '/org/gnome/USBBlocker');
		this._screenSaver = new DBusScreenSaverProxy(Gio.DBus.session,
														  'org.gnome.ScreenSaver',
														  '/org/gnome/ScreenSaver');

		this._screenLockToggle = this._screenSaver.connectSignal('ActiveChanged',
														Lang.bind(this, this._screenChanged));

        // From auto-move-windows@gnome-shell-extensions.gcampax.github.com
        this._windowTracker = Shell.WindowTracker.get_default();
        let display = global.screen.get_display();
        let shellwm = global.window_manager;
	
		this._state = false;
		this._icon = new St.Icon({
       			style_class: 'system-status-icon'
       	});

		this._usbBlocker.get_statusRemote(Lang.bind(this, function(dbus_status) {
			this._state = (dbus_status == "true");
			if (this._state) {
				this._icon.icon_name = EnabledIcon;
				
			} else this._icon.icon_name = DisabledIcon;
			
		}));



        // who has requested the inhibition
		this._lockedBefore = false;
		this._screenLocked = false;
        this._last_app = "";
        this._last_cookie = "";
        this._handle_lid_fd = false;
        this._apps = [];
        this._cookies = [];
        this._objects = [];

        this.actor.add_actor(this._icon);
        this.actor.add_style_class_name('panel-status-button');
        this.actor.connect('button-press-event', Lang.bind(this, this.toggleState));

        // Restore user state -- if we have a system bus we would need to check
		// the status of the entire program
/*
		if (this._settings.get_boolean(USER_ENABLED_KEY)) {
          this.toggleState();
        }
*/
        // Enable caffeine when fullscreen app is running
/*        if (this._settings.get_boolean(FULLSCREEN_KEY)) {
            this._inFullscreenId = global.screen.connect('in-fullscreen-changed', Lang.bind(this, this.toggleFullscreen));
            this.toggleFullscreen();
        }
        // List current windows to check if we need to inhibit
        global.get_window_actors().map(Lang.bind(this, function(window) {
            this._mayInhibit(null, window.meta_window, null);
        }));
*/
    },

	_screenChanged: function(proxy, sender, [object]) {
		if (!this._screenLocked) {
			this._screenLocked = true;
			if (this._state)
				this._lockedBefore = true;
			else if (!this._state) {
				this._lockedBefore = false;
				this.toggleState();
			}
		} else if (!this._lockedBefore) {
				this._screenLocked = false;
				this.togglesstate();
		}
	

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

    destroy: function() {
		if (this._state)
			this.toggleState();

        if (this._windowDestroyedId) {
            global.window_manager.disconnect(this._windowDestroyedId);
            this._windowDestroyedId = 0;
        }

        this.parent();
    }
});

function init(extensionMeta) {
    Convenience.initTranslations();
    let theme = imports.gi.Gtk.IconTheme.get_default();
    theme.append_search_path(extensionMeta.path + "/icons");
}

function enable() {
    CaffeineIndicator = new Caffeine();
    Main.panel.addToStatusArea(IndicatorName, CaffeineIndicator);
}

function disable() {
    CaffeineIndicator.destroy();
    CaffeineIndicator = null;
}
