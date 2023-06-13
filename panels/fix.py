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
            'FIX_LED': self._gtk.Button("light", _("LED Light Driver"), "color3"),
        }

        self.buttons['FIX_FILES'].connect("clicked", self.set_fix_option_to, "FILES")
        self.buttons['FIX_FILES'].connect("clicked", self.menu_item_clicked, "step_one_warning", {
            "name": _("Essential Files"),
            "panel": "step_one_warning"
        })

        self.buttons['FIX_CAMERA'].connect("clicked", self.set_fix_option_to, "CAMERA")
        self.buttons['FIX_CAMERA'].connect("clicked", self.menu_item_clicked, "step_one_warning", {
            "name": _("Camera Driver"),
            "panel": "step_one_warning"
        })
        
        self.buttons['FIX_LED'].connect("clicked", self.set_fix_option_to, "LIGHT")
        self.buttons['FIX_LED'].connect("clicked", self.menu_item_clicked, "step_one_warning", {
            "name": _("LED Light Driver"),
            "panel": "step_one_warning"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX_FILES'], 0, 0, 1, 2)
        grid.attach(self.buttons['FIX_CAMERA'], 1, 0, 1, 2)
        grid.attach(self.buttons['FIX_LED'], 2, 0, 1, 2)

        self.labels['fix_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['fix_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def nothing (self):
        pass