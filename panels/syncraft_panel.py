import logging

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
            'UPDATE': self._gtk.Button("syncraftupdate", _("Update via Internet"), "color1"),
            'FIX': self._gtk.Button("compass", _("Quick System Fixes"), "color1"),
            'UPDATE_USB': self._gtk.Button("usb", _("Update via USB"), "color1"),
        }
        self.buttons['UPDATE'].connect("clicked", self.menu_item_clicked, "update", {
            "name": _("Update"),
            "panel": "update"
        })
        self.buttons['FIX'].connect("clicked", self.menu_item_clicked, "fix", {
            "name": _("Quick System Fixes"),
            "panel": "fix"
        })
        self.buttons['UPDATE_USB'].connect("clicked", self.nothing)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['UPDATE'], 0, 0, 1, 2)
        grid.attach(self.buttons['FIX'], 1, 0, 1, 2)
        # grid.attach(self.buttons['UPDATE_USB'], 2, 0, 1, 2)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def nothing (self):
        pass