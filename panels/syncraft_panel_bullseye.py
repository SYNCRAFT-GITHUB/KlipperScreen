import logging
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return SyncraftPanel(*args)

class SyncraftPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['syncraft_panel']

        self.buttons = {
            'UPDATE': self._gtk.Button("update", _("Update via Internet"), "color3"),
            'REVERT': self._gtk.Button ("stock", _("Factory Reset"), "color1"),
            'USB_ACTIONS': self._gtk.Button("usb", _("USB Device"), "color2"),
            'SYSTEM_INFO': self._gtk.Button("info", _("System Information"), "color1"),
        }
        self.buttons['UPDATE'].connect("clicked", self.menu_item_clicked, "update", {
            "name": _("Update"),
            "panel": "moonraker_update" #core_update
        })
        self.buttons['REVERT'].connect("clicked",self.set_fix_option_to,"REVERT_ALL")
        self.buttons['REVERT'].connect("clicked", self.menu_item_clicked, "script", {
            "name":_("System"),
            "panel": "script"
        })
        self.buttons['USB_ACTIONS'].connect("clicked", self.menu_item_clicked, "USB_ACTIONS", {
            "name": _("USB Device"),
            "panel": "usb_actions"
        })
        self.buttons['SYSTEM_INFO'].connect("clicked", self.menu_item_clicked, "system_info", {
            "name": _("Information"),
            "panel": "system_info"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['REVERT'], 0, 1, 1, 1)
        grid.attach(self.buttons['UPDATE'], 0, 0, 1, 1)
        grid.attach(self.buttons['USB_ACTIONS'], 1, 0, 1, 1)
        grid.attach(self.buttons['SYSTEM_INFO'], 1, 1, 1, 1)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)