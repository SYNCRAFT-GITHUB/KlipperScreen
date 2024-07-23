import subprocess
import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return BranchSelectPanel(*args)

class BranchSelectPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['fix_panel']

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.buttons = {
            'FIX_FILES_V3': self._gtk.Button("file", "V3", self.color()),
            'FIX_FILES_BOWDEN': self._gtk.Button("file", _("Bowden"), self.color()),
            'FIX_FILES_FEEDER': self._gtk.Button("file", _("Feeder"), self.color()),
            'FIX_FILES_METAL': self._gtk.Button("file", _("Metal"), self.color()),
        }

        self.buttons['FIX_FILES_V3'].connect("clicked", self.set_fix_option_to, "FILES_V3")
        self.buttons['FIX_FILES_V3'].connect("clicked", self.menu_item_clicked, "fix_steps", {
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

        self.buttons['FIX_FILES_METAL'].connect("clicked", self.set_fix_option_to, "FILES_METAL")
        self.buttons['FIX_FILES_METAL'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX_FILES_V3'], 0, 0, 1, 1)
        grid.attach(self.buttons['FIX_FILES_BOWDEN'], 1, 0, 1, 1)
        grid.attach(self.buttons['FIX_FILES_FEEDER'], 1, 1, 1, 1)
        grid.attach(self.buttons['FIX_FILES_METAL'], 0, 1, 1, 1)

        scroll.add(grid)
        self.content.add(scroll)

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def color(self) -> str:
        return f"color{random.randint(1, 4)}"