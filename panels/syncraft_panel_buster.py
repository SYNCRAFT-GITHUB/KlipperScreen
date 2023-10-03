import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return SyncraftPanelBuster(*args)

class SyncraftPanelBuster(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['syncraft_panel']

        self.buttons = {
            'UPDATE': self._gtk.Button("update", _("Update via Internet"), "color1"),
            'FIX': self._gtk.Button("compass", _("Quick System Fixes"), "color1"),
            'UPDATE_USB': self._gtk.Button("usb", _("Update via USB"), "color1"),
            'EXPORT_LOG': self._gtk.Button("usb-save", _("Export Logs to USB"), "color1"),
        }
        self.buttons['UPDATE'].connect("clicked", self.menu_item_clicked, "update", {
            "name": _("Update"),
            "panel": "update"
        })
        self.buttons['FIX'].connect("clicked", self.menu_item_clicked, "fix", {
            "name": _("Quick System Fixes"),
            "panel": "fix"
        })
        self.buttons['UPDATE_USB'].connect("clicked", self.set_fix_option_to, "UPDATEVIAUSB")
        self.buttons['UPDATE_USB'].connect("clicked", self.menu_item_clicked, "update_usb", {
            "name": _("System"),
            "panel": "script"
        })
        self.buttons['EXPORT_LOG'].connect("clicked", self.set_fix_option_to, "EXPORTLOGSTOUSB")
        self.buttons['EXPORT_LOG'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("Export Logs to USB"),
            "panel": "script"
        })
        

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX'], 0, 1, 1, 1)
        grid.attach(self.buttons['UPDATE'], 0, 0, 1, 1)
        grid.attach(self.buttons['UPDATE_USB'], 1, 0, 1, 1)
        grid.attach(self.buttons['EXPORT_LOG'], 1, 1, 1, 1)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)