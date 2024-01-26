import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return NewConfigurations(*args)

class NewConfigurations(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['move']

        grid = self._gtk.HomogeneousGrid()

        self.switch_x = self._gtk.Button("letter-x", None, None)
        self.switch_y = self._gtk.Button("letter-y", None, None)
        self.switch_z = self._gtk.Button("letter-z", None, None)

        self.up = self._gtk.Button("arrow-up", None, "color2")
        self.down = self._gtk.Button("arrow-down", None, "color2")
        self.right = self._gtk.Button("arrow-right", None, "color2")
        self.left = self._gtk.Button("arrow-left", None, "color2")

        self.home = self._gtk.Button("home", None, None)
        self.gear = self._gtk.Button("gear", None, None)

        grid.attach(self.switch_x, 0, 2, 1, 1)
        grid.attach(self.switch_y, 1, 2, 1, 1)
        grid.attach(self.switch_z, 2, 2, 1, 1)

        grid.attach(self.up, 1, 0, 1, 1)
        grid.attach(self.down, 1, 1, 1, 1)
        grid.attach(self.left, 0, 1, 1, 1)
        grid.attach(self.right, 2, 1, 1, 1)

        grid.attach(self.home, 0, 0, 1, 1)
        grid.attach(self.gear, 2, 0, 1, 1)

        self.home.connect("clicked", self.home)
        self.gear.connect("clicked", self.menu_item_clicked, "move_gear", {
                "name": _("Move"),
                "panel": "move"
            })

        self.switch_x.connect("clicked", self.orientation, "X")
        self.switch_y.connect("clicked", self.orientation, "Y")
        self.switch_z.connect("clicked", self.orientation, "Z")

        self.labels['move'] = self._gtk.HomogeneousGrid()
        self.labels['move'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['move'])
        self.orientation("", "Y")

    def home(self, button):
        self._screen._ws.klippy.gcode_script("G28")

    def orientation(self, button, value):
        self.active = value
        self.left.set_sensitive(True)
        self.right.set_sensitive(True)
        self.switch_x.set_property("opacity", 0.3)
        self.switch_y.set_property("opacity", 0.3)
        self.switch_z.set_property("opacity", 0.3)

        if self.active == "X":
            self.switch_x.set_property("opacity", 1.0)
        if self.active == "Y":
            self.switch_y.set_property("opacity", 1.0)
        if self.active == "Z":
            self.switch_z.set_property("opacity", 1.0)
            self.left.set_sensitive((False))
            self.right.set_sensitive((False))

        