import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return FixPanel(*args)

class FixPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['fix_panel']

        self.buttons = {
            'FIX_FILES': self._gtk.Button("file", _("Essential Files"), "color1"),
            'FIX_CAMERA': self._gtk.Button("camera", _("Camera Driver"), "color2"),
            'FIX_KLIPPERSCREEN': self._gtk.Button("screen", _("Interface"), "color3"),
            'FIX_MAINSAIL': self._gtk.Button("monitor", _("Web Interface"), "color3"),
            'FIX_LED': self._gtk.Button("light", _("LED Light Driver"), "color4"),
        }

        self.buttons['FIX_FILES'].connect("clicked", self.set_fix_option_to, "FILES")
        self.buttons['FIX_FILES'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Essential Files"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_CAMERA'].connect("clicked", self.set_fix_option_to, "CAMERA")
        self.buttons['FIX_CAMERA'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Camera Driver"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.set_fix_option_to, "KLIPPERSCREEN")
        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Interface"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_MAINSAIL'].connect("clicked", self.set_fix_option_to, "MAINSAIL")
        self.buttons['FIX_MAINSAIL'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Web Interface"),
            "panel": "fix_steps"
        })
        
        self.buttons['FIX_LED'].connect("clicked", self.set_fix_option_to, "LIGHT")
        self.buttons['FIX_LED'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("LED Light Driver"),
            "panel": "fix_steps"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX_FILES'], 0, 0, 2, 1)
        grid.attach(self.buttons['FIX_CAMERA'], 0, 2, 1, 1)
        grid.attach(self.buttons['FIX_KLIPPERSCREEN'], 0, 1, 1, 1)
        grid.attach(self.buttons['FIX_MAINSAIL'], 1, 1, 1, 1)
        grid.attach(self.buttons['FIX_LED'], 1, 2, 1, 1)

        self.labels['fix_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_panel'].attach(grid, 0, 0, 2, 2)

        self.content.add(self.labels['fix_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def nothing (self):
        pass