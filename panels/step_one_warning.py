import logging

import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return StepOneWarning(*args)

class StepOneWarning(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['step_one_warning']

        self.image = self._gtk.Image("warning", self._gtk.content_width * .7, self._gtk.content_height * .7)
        
        self.labels['text'] = Gtk.Label(_("Please follow the tutorial to ensure everything performs correctly."))
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)

        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.content.add(self.info)
        
        self.content.add(self.labels['text'])

        self.buttons = {
            'CONTINUE': self._gtk.Button("arrow-right", None, "color1"),
        }
        self.buttons['CONTINUE'].connect("clicked", self.menu_item_clicked, "step_two_warning", {
            "name": _("Fix"),
            "panel": "step_two_warning"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['CONTINUE'], 0, 1, 1, 1)

        self.labels['fix_specific_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_specific_panel'].attach(grid, 0, 0, 1, 3)
        self.content.add(self.labels['fix_specific_panel'])