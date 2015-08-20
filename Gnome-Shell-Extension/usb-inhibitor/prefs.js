// -*- mode: js2; indent-tabs-mode: nil; js2-basic-offset: 4 -*-
// Adapted from auto-move-windows@gnome-shell-extensions.gcampax.github.com
// A lot of simplifications

const Gio = imports.gi.Gio;
const Gtk = imports.gi.Gtk;
const Lang = imports.lang;
const GObject = imports.gi.GObject;
const Config = imports.misc.config;

const Gettext = imports.gettext.domain('gnome-shell-extension-usbinhibitor');
const _ = Gettext.gettext;

const ExtensionUtils = imports.misc.extensionUtils;
const Me = ExtensionUtils.getCurrentExtension();
const Convenience = Me.imports.convenience;

const SHOW_NOTIFICATIONS = 'show-notifications';

const USBinhibitorWidget = new Lang.Class({
    Name: 'USBinhibitorWidget',
    Extends: Gtk.Box,

    _init: function(params) {
        this._settings = Convenience.getSettings();
        this._changedPermitted = false;

        this.parent({orientation: Gtk.Orientation.HORIZONTAL,
                                margin: 7});
        let label = new Gtk.Label({label: _("Enable notifications"),
                                   xalign: 0});

        let show = new Gtk.Switch({active: this._settings.get_boolean(SHOW_NOTIFICATIONS)});
        show.connect('notify::active', Lang.bind(this, function(button) {
            this._settings.set_boolean(SHOW_NOTIFICATIONS, button.active);
        }));

        this.pack_start(label, true, true, 0);
        this.add(show);
    },

});

// Need to add translations
function init() {
//    Convenience.initTranslations();
}

function buildPrefsWidget() {
    let widget = new USBinhibitorWidget();
    widget.show_all();

    return widget;
}
