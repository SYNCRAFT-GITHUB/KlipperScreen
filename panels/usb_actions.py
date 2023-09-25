import logging
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return UsbActions(*args)

class UsbActions(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['usb_actions_panel']

        self.buttons = {
            'UPDATE': self._gtk.Button("usb-save", _("Update via USB"), "color1"),
            'LOGS': self._gtk.Button ("logs", _("Export Logs"), "color1"),
            'SLICER': self._gtk.Button("cura", _("Export Syncraft Packs"), "color1"),
        }
        self.buttons['UPDATE'].connect("clicked",self.set_fix_option_to,"UPDATE_USB")
        self.buttons['UPDATE'].connect("clicked", self.menu_item_clicked, "script", {
            "name":_("System"),
            "panel": "script"
        })
        self.buttons['LOGS'].connect("clicked",self.set_fix_option_to,"USB_LOGS")
        self.buttons['LOGS'].connect("clicked", self.menu_item_clicked, "script", {
            "name":_("System"),
            "panel": "script"
        })
        self.buttons['SLICER'].connect("clicked",self.set_fix_option_to,"USB_SLICER")
        self.buttons['SLICER'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['UPDATE'], 0, 1, 1, 1)
        grid.attach(self.buttons['LOGS'], 0, 0, 1, 1)
        grid.attach(self.buttons['SLICER'], 1, 0, 1, 1)

        self.labels['usb_actions_panel'] = self._gtk.HomogeneousGrid()
        self.labels['usb_actions_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['usb_actions_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)