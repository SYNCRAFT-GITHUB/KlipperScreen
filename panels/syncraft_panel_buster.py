import logging
import os
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
            'REVERT': self._gtk.Button (
                "compass" if self._config.linux('buster') else "stock",
                _("Quick System Fixes") if self._config.linux('buster') else _("Restore to Factory Default"),
                "color1"),
            'UPDATE_USB': self._gtk.Button("usb", _("Update via USB"), "color1"),
        }
        self.buttons['UPDATE'].connect("clicked", self.menu_item_clicked, "update", {
            "name": _("Update"),
            "panel": "moonraker_update" if self._config.linux('buster') else "core_update"
        })
        self.buttons['REVERT'].connect("clicked", self.menu_item_clicked, "fix", {
            "name": _("Quick System Fixes") if self._config.linux('buster') else _("Restore"),
            "panel": "fix" if self._config.linux('buster') else "revert"
        })
        self.buttons['UPDATE_USB'].connect("clicked",self.set_fix_option_to,"EXPORTLOGSTOUSB")
        self.buttons['UPDATE_USB'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['REVERT'], 0, 1, 1, 1)
        grid.attach(self.buttons['UPDATE'], 0, 0, 1, 1)
        grid.attach(self.buttons['UPDATE_USB'], 1, 0, 1, 1)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)