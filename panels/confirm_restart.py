import logging
import time
import threading

import os
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ConfirmRestartPanel(*args)

class ConfirmRestartPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['reflash_design']

        event_box = Gtk.EventBox()
        image = self._gtk.Image("restart-warning", self._gtk.content_width * 3, self._gtk.content_height * .5, universal=True)
        event_box.add(image)

        self.content.add(event_box)

        self.labels['text'] = Gtk.Label(f'\n{_("Are you sure you wish to reboot the system?")}\n')
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        
        self.content.add(self.labels['text'])

        timer = threading.Timer(1.8, self.allow_restart)
        timer.start()

        self.buttons = {
            'GO_BACK': self._gtk.Button("arrow-left", _("Go Back"), "color2"),
            'RESTART': self._gtk.Button("refresh", _("Restart"), "color1"),
        }

        self.buttons['GO_BACK'].connect("clicked", self.go_back)
        self.buttons['RESTART'].connect("clicked", self.restart_system)

        self.buttons['RESTART'].set_sensitive(False)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['GO_BACK'], 0, 0, 1, 1)
        grid.attach(self.buttons['RESTART'], 1, 0, 1, 1)

        self.labels['reflash_design'] = self._gtk.HomogeneousGrid()
        self.labels['reflash_design'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['reflash_design'])

    def allow_restart(self):
        self.buttons['RESTART'].set_sensitive(True)

    def go_back(self, button):
        self._screen._menu_go_back()

    def restart_system(self, button):
        logging.info("OS Reboot")
        os.system("systemctl reboot")