import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel

SPEED = 23_300
EXTRUDER = 1
BED = 2
MOVE_UP = 1
MOVE_DOWN = 2
MOVE_LEFT = 3
MOVE_RIGHT = 4

def create_panel(*args):
    return NewConfigurations(*args)

class NewConfigurations(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['move']

        grid = self._gtk.HomogeneousGrid()

        self.extruder = self._gtk.Button("extruder-square", None, None)
        self.bed = self._gtk.Button("bed-square", None, None)

        self.up = self._gtk.Button("key-up", None, "color2")
        self.down = self._gtk.Button("key-down", None, "color2")
        self.right = self._gtk.Button("key-right", None, "color2")
        self.left = self._gtk.Button("key-left", None, "color2")

        self.home = self._gtk.Button("home", "Home All", None)
        self.off = self._gtk.Button("motor-off", "Disable Motors", None)
        self.gear = self._gtk.Button("settings", None, None)

        grid.attach(self.extruder, 0, 2, 1, 1)
        grid.attach(self.bed, 1, 2, 1, 1)

        grid.attach(self.up, 1, 0, 1, 1)
        grid.attach(self.down, 1, 1, 1, 1)
        grid.attach(self.left, 0, 1, 1, 1)
        grid.attach(self.right, 2, 1, 1, 1)

        grid.attach(self.home, 0, 0, 1, 1)
        grid.attach(self.off, 2, 0, 1, 1)
        grid.attach(self.gear, 2, 2, 1, 1)

        self.home.connect("clicked", self.home_all)
        self.gear.connect("clicked", self.menu_item_clicked, "move_gear", {
                "name": _("Move"),
                "panel": "move_gear"
            })

        self.extruder.connect("clicked", self.orientation, EXTRUDER)
        self.bed.connect("clicked", self.orientation, BED)

        self.up.connect("clicked", self.move, MOVE_UP)
        self.down.connect("clicked", self.move, MOVE_DOWN)
        self.left.connect("clicked", self.move, MOVE_LEFT)
        self.right.connect("clicked", self.move, MOVE_RIGHT)
        self.off.connect("clicked", self._screen._confirm_send_action,
                                           _("Are you sure you wish to disable motors?"),
                                           "printer.gcode.script", {"script": "M18"})

        self.labels['move'] = self._gtk.HomogeneousGrid()
        self.labels['move'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['move'])
        self.orientation("", EXTRUDER)

    def home_all(self, button):
        self._screen._ws.klippy.gcode_script("G28")

    def orientation(self, button, value):
        self.active = value
        self.left.set_sensitive(True)
        self.right.set_sensitive(True)
        self.extruder.set_property("opacity", 0.3)
        self.bed.set_property("opacity", 0.3)

        if self.active == EXTRUDER:
            self.extruder.set_property("opacity", 1.0)
        if self.active == BED:
            self.bed.set_property("opacity", 1.0)
            self.left.set_sensitive((False))
            self.right.set_sensitive((False))

    def move(self, button, direction):

        if direction == MOVE_UP:
            if self.active == EXTRUDER:
                self._screen._ws.klippy.gcode_script(f"G1 Y300 F{SPEED}")
                logging.debug(f"Moving Extruder Up")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 Z0 F{SPEED}")
                logging.debug(f"Moving Bed Up")
        elif direction == MOVE_DOWN:
            if self.active == EXTRUDER:
                self._screen._ws.klippy.gcode_script(f"G1 Y0 F{SPEED}")
                logging.debug(f"Moving Extruder Down")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 Z340 F{SPEED}")
                logging.debug(f"Moving Bed Down")
        elif direction == MOVE_LEFT:
            self._screen._ws.klippy.gcode_script(f"G1 X0 F{SPEED}")
            logging.debug(f"Moving Extruder to the Left")
        elif direction == MOVE_RIGHT:
            self._screen._ws.klippy.gcode_script(f"G1 X320 F{SPEED}")
            logging.debug(f"Moving Extruder to the Right")
        else:
            print("unknown direction")