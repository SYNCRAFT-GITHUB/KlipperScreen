import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel

SPEED = 23_350
EXTRUDER = 1
BED = 2
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

def create_panel(*args):
    return MovePanel(*args)

class MovePanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['move']

        grid = self._gtk.HomogeneousGrid()

        self.buttons = {
            "extruder": self._gtk.Button("extruder-square", None, None),
            "bed": self._gtk.Button("bed-square", None, None),
            "up": self._gtk.Button("key-up", None, "color3"),
            "down": self._gtk.Button("key-down", None, "color2"),
            "left": self._gtk.Button("key-left", None, "color1"),
            "right": self._gtk.Button("key-right", None, "color1"),
            "home": self._gtk.Button("home", _("Home All"), None),
            "off": self._gtk.Button("motor-off", _("Disable Motors"), None),
            "gear": self._gtk.Button("settings", None, None)
        }

        grid.attach(self.buttons["extruder"], 0, 2, 1, 1)
        grid.attach(self.buttons["bed"], 1, 2, 1, 1)

        grid.attach(self.buttons["up"], 1, 0, 1, 1)
        grid.attach(self.buttons["down"], 1, 1, 1, 1)
        grid.attach(self.buttons["left"], 0, 1, 1, 1)
        grid.attach(self.buttons["right"], 2, 1, 1, 1)

        grid.attach(self.buttons["home"], 0, 0, 1, 1)
        grid.attach(self.buttons["off"], 2, 0, 1, 1)
        grid.attach(self.buttons["gear"], 2, 2, 1, 1)

        self.buttons["home"].connect("clicked", self.home_all)
        self.buttons["gear"].connect("clicked", self.menu_item_clicked, "move_gear", {
                "name": _("Move"),
                "panel": "move_gear"
            })

        self.buttons["extruder"].connect("clicked", self.orientation, EXTRUDER)
        self.buttons["bed"].connect("clicked", self.orientation, BED)

        self.buttons["up"].connect("clicked", self.move, UP)
        self.buttons["down"].connect("clicked", self.move, DOWN)
        self.buttons["left"].connect("clicked", self.move, LEFT)
        self.buttons["right"].connect("clicked", self.move, RIGHT)
        self.buttons["off"].connect("clicked", self._screen._confirm_send_action,
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
        self.buttons["left"].set_sensitive(True)
        self.buttons["right"].set_sensitive(True)
        self.buttons["extruder"].set_property("opacity", 0.3)
        self.buttons["bed"].set_property("opacity", 0.3)

        if self.active == EXTRUDER:
            self.buttons["extruder"].set_property("opacity", 1.0)
        if self.active == BED:
            self.buttons["bed"].set_property("opacity", 1.0)
            self.buttons["left"].set_sensitive((False))
            self.buttons["right"].set_sensitive((False))

    def move(self, button, direction):

        if direction == UP:
            if self.active == EXTRUDER:
                self._screen._ws.klippy.gcode_script(f"G1 Y300 F{SPEED}")
                logging.debug("Moving Extruder Up")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 Z0 F{SPEED}")
                logging.debug("Moving Bed Up")
        elif direction == DOWN:
            if self.active == EXTRUDER:
                self._screen._ws.klippy.gcode_script(f"G1 Y0 F{SPEED}")
                logging.debug("Moving Extruder Down")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 Z340 F{SPEED}")
                logging.debug("Moving Bed Down")
        elif direction == LEFT:
            self._screen._ws.klippy.gcode_script(f"G1 X0 F{SPEED}")
            logging.debug("Moving Extruder to the Left")
        elif direction == RIGHT:
            self._screen._ws.klippy.gcode_script(f"G1 X320 F{SPEED}")
            logging.debug("Moving Extruder to the Right")
        else:
            print("unknown direction")

    def process_busy(self, busy):
        for button in self.buttons:
            if button == "gear":
                continue
            else:
                self.buttons[button].set_sensitive(not busy)

    def process_update(self, action, data):
            if action == "notify_busy":
                self.process_busy(data)
                return