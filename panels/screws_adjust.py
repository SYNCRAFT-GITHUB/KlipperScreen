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

        self.started: bool = False
        self.amount: int = 0

        self.buttons = {
            'START': self._gtk.Button("resume", _("Start"), "color1"),
            'CANCEL': self._gtk.Button("cancel", _("Abort"), "color2"),
            'NOW_ADJUSTED': self._gtk.Button("arrow-right", _("This screw is now Adjusted"), "color4"),
            'ALREADY_ADJUSTED': self._gtk.Button("arrow-right", _("This screw is already Adjusted"), "color4"),
            'FINISH': self._gtk.Button("complete", _("Finish"), "color2"),
        }
        self.buttons['START'].connect("clicked", self.screws_tilt_calculate)
        self.buttons['CANCEL'].connect("clicked", self.abort)
        self.buttons['NOW_ADJUSTED'].connect("clicked", self.apply)
        self.buttons['ALREADY_ADJUSTED'].connect("clicked", self.accept)
        self.buttons['FINISH'].connect("clicked", self.finish)

        self.off_state()

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['START'], 0, 0, 1, 3)
        grid.attach(self.buttons['CANCEL'], 1, 2, 1, 1)
        grid.attach(self.buttons['FINISH'], 2, 2, 1, 1)
        grid.attach(self.buttons['NOW_ADJUSTED'], 1, 0, 2, 1)
        grid.attach(self.buttons['ALREADY_ADJUSTED'], 1, 1, 2, 1)

        self.labels['screws-adjust'] = self._gtk.HomogeneousGrid()
        self.labels['screws-adjust'].attach(grid, 0, 0, 1, 3)

        self.content.add(self.labels['screws-adjust'])

    def abort(self, widget):
        self.off_state()
        logging.info("Aborting screws adjust")
        self._screen._ws.klippy.gcode_script(KlippyGcodes.ABORT)
        self._screen._menu_go_back()

    def off_state(self):
        self.started = False
        self.amount = 0
        self.buttons['FINISH'].set_sensitive(False)
        self.buttons['CANCEL'].set_sensitive(False)
        self.buttons['NOW_ADJUSTED'].set_sensitive(False)
        self.buttons['ALREADY_ADJUSTED'].set_sensitive(False)

    def check_finish(self):
        if self.started and self.amount >= 3:
            self.buttons['FINISH'].set_sensitive(True)

    def accept(self, widget):
        if self.started:
            self.amount += 1
            self._screen._ws.klippy.gcode_script(KlippyGcodes.ACCEPT)
            self.check_finish()

    def apply(self, widget):
        if self.started:
            self.amount += 1
            self._screen._ws.klippy.gcode_script(KlippyGcodes.ADJUSTED)
            self.check_finish()

    def home(self):
        if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
            self._screen._ws.klippy.gcode_script(KlippyGcodes.HOME)
        if self._printer.config_section_exists("z_tilt"):
            self._screen._ws.klippy.gcode_script(KlippyGcodes.Z_TILT)

    def screws_tilt_calculate(self, widget):
        self.started = True
        self.buttons['CANCEL'].set_sensitive(True)
        self.buttons['NOW_ADJUSTED'].set_sensitive(True)
        self.buttons['ALREADY_ADJUSTED'].set_sensitive(True)
        self._screen._ws.klippy.gcode_script("BED_SCREWS_ADJUST")

    def finish(self, button):
        self.off_state()
        self._screen._menu_go_back()