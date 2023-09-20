import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return UpdateFromUsbPanel(*args)

class UpdateFromUsbPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['update_from_usb']

        self.buttons = {
            'DEFAULT': self._gtk.Button("usb", _("Regular Update"), "color1"),
            'RECOVER': self._gtk.Button("refresh", _("Recover Backup"), "color2"),
        }
        self.buttons['DEFAULT'].connect("clicked", self.set_fix_option_to, "USB_DEFAULT")
        self.buttons['DEFAULT'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("Regular Update"),
            "panel": "script"
        })
        self.buttons['RECOVER'].connect("clicked", self.set_fix_option_to, "USB_RECOVER")
        self.buttons['RECOVER'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("Recover Backup"),
            "panel": "script"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['DEFAULT'], 0, 0, 1, 2)
        grid.attach(self.buttons['RECOVER'], 1, 0, 1, 2)

        self.labels['update_from_usb'] = self._gtk.HomogeneousGrid()
        self.labels['update_from_usb'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['update_from_usb'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)