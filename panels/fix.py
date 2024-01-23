import logging
import random

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
            'FIX_FILES': self._gtk.Button("file", f'{_("Essential Files")} (LEGACY)', self.color()),
            'FIX_FILES_BOWDEN': self._gtk.Button("file", f'{_("Essential Files")} (BOWDEN)', self.color()),
            'FIX_FILES_FEEDER': self._gtk.Button("file", f'{_("Essential Files")} ({_("Feeder").upper()})', self.color()),
            'CLEAN_GCODE': self._gtk.Button("clean", _("Clear GCodes Folder"), self.color()),
            'FIX_CAMERA': self._gtk.Button("camera", _("Camera Driver"), self.color()),
            'FIX_KLIPPERSCREEN': self._gtk.Button("screen", _("KlipperScreen"), self.color()),
            'FIX_MAINSAIL': self._gtk.Button("monitor", _("Mainsail"), self.color()),
            'FIX_LED': self._gtk.Button("light", _("LED Light Driver"), self.color()),
            'FIX_MOONRAKER': self._gtk.Button("moonraker", _("Moonraker"), self.color()),
            'EXPORT_LOGS_USB': self._gtk.Button("usb-save", _("Export Logs to USB"), self.color()),
        }

        self.buttons['CLEAN_GCODE'].connect("clicked", self.set_fix_option_to, "CLEANGCODEFILES")
        self.buttons['CLEAN_GCODE'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
        })

        self.buttons['FIX_FILES'].connect("clicked", self.set_fix_option_to, "FILES")
        self.buttons['FIX_FILES'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_FILES_BOWDEN'].connect("clicked", self.set_fix_option_to, "FILES_BOWDEN")
        self.buttons['FIX_FILES_BOWDEN'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_FILES_FEEDER'].connect("clicked", self.set_fix_option_to, "FILES_FEEDER")
        self.buttons['FIX_FILES_FEEDER'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_CAMERA'].connect("clicked", self.set_fix_option_to, "CAMERA")
        self.buttons['FIX_CAMERA'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.set_fix_option_to, "KLIPPERSCREEN")
        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_MAINSAIL'].connect("clicked", self.set_fix_option_to, "MAINSAIL")
        self.buttons['FIX_MAINSAIL'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        
        self.buttons['FIX_LED'].connect("clicked", self.set_fix_option_to, "LIGHT")
        self.buttons['FIX_LED'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.set_fix_option_to, "MOONRAKER")
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['EXPORT_LOGS_USB'].connect("clicked", self.set_fix_option_to, "EXPORTLOGSTOUSB")
        self.buttons['EXPORT_LOGS_USB'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "script"
        })

        grid = self._gtk.HomogeneousGrid()

        # 0, 2, 2, 1

        grid.attach(self.buttons['FIX_FILES'], 0, 0, 2, 1)
        grid.attach(self.buttons['FIX_FILES_BOWDEN'], 2, 0, 2, 1)
        grid.attach(self.buttons['FIX_FILES_FEEDER'], 0, 2, 2, 1)
        grid.attach(self.buttons['FIX_CAMERA'], 0, 3, 1, 1)
        grid.attach(self.buttons['FIX_KLIPPERSCREEN'], 2, 3, 1, 1)
        grid.attach(self.buttons['FIX_MAINSAIL'], 3, 3, 1, 1)
        grid.attach(self.buttons['FIX_LED'], 1, 3, 1, 1)
        grid.attach(self.buttons['FIX_MOONRAKER'], 2, 2, 2, 1)

        self.labels['fix_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_panel'].attach(grid, 0, 0, 2, 2)

        self.content.add(self.labels['fix_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def color(self) -> str:
        return f"color{random.randint(1, 4)}"
