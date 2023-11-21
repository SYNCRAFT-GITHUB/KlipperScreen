import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ScrewsAdjust(*args)

class ScrewsAdjust(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['screws-adjust']

        self.buttons = {
            'START': self._gtk.Button("resume", _("Start"), "color1"),
            'CANCEL': self._gtk.Button("cancel", _("Abort Screw Adjust"), "color2"),
            'APPLY': self._gtk.Button("arrow-right", _("This screw is now Adjusted"), "color4"),
            'CONTINUE': self._gtk.Button("arrow-right", _("This screw is already Adjusted"), "color4"),
        }
        self.buttons['START'].connect("clicked", self.screws_tilt_calculate)
        self.buttons['CANCEL'].connect("clicked", self.abort)
        self.buttons['APPLY'].connect("clicked", self.apply)
        self.buttons['CONTINUE'].connect("clicked", self.accept)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['START'], 0, 0, 1, 3)
        grid.attach(self.buttons['CANCEL'], 1, 2, 2, 1)
        grid.attach(self.buttons['APPLY'], 1, 0, 2, 1)
        grid.attach(self.buttons['CONTINUE'], 1, 1, 2, 1)

        self.labels['screws-adjust'] = self._gtk.HomogeneousGrid()
        self.labels['screws-adjust'].attach(grid, 0, 0, 1, 3)

        self.content.add(self.labels['screws-adjust'])

    def abort(self, widget):
        logging.info("Aborting screws adjust")
        self._screen._ws.klippy.gcode_script(KlippyGcodes.ABORT)
        self._screen._menu_go_back()

    def accept(self, widget):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.ACCEPT)

    def apply(self, widget):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.ADJUSTED)

    def home(self):
        if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
            self._screen._ws.klippy.gcode_script(KlippyGcodes.HOME)
        if self._printer.config_section_exists("z_tilt"):
            self._screen._ws.klippy.gcode_script(KlippyGcodes.Z_TILT)

    def screws_tilt_calculate(self, widget):
        self._screen._ws.klippy.gcode_script("BED_SCREWS_ADJUST")