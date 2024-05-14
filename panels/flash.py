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
    return ReflashPanel(*args)

class ReflashPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['reflash_design']

        event_box = Gtk.EventBox()
        image = self._gtk.Image("eletro-warning", self._gtk.content_width * 3, self._gtk.content_height * .5, universal=True)
        event_box.add(image)
        event_box.connect("button-press-event", self.on_image_clicked)

        self.content.add(event_box)

        self.text = f"""
        {_("This procedure will flash the controller board.")}
        {_("After this quick procedure, the machine will restart.")}
        {_("Do not proceed if you are not sure what you are doing.")}
        """

        self.labels['text'] = Gtk.Label(self.text)
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        
        self.content.add(self.labels['text'])

        timer = threading.Timer(8.0, self.allow_reflash)
        timer.start()
        self.clicks: int = 0

        self.buttons = {
            'FLASH': self._gtk.Button(None, _("First Flash (Jumper required)"), "color1"),
            'REFLASH': self._gtk.Button(None, _("Re-flash (Jumper not required)"), "color2"),
        }

        self.buttons['FLASH'].connect("clicked", self.flash)
        self.buttons['REFLASH'].connect("clicked", self.reflash)

        self.buttons['FLASH'].set_sensitive(False)
        self.buttons['REFLASH'].set_sensitive(False)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FLASH'], 1, 0, 1, 1)
        grid.attach(self.buttons['REFLASH'], 2, 0, 1, 1)

        self.labels['reflash_design'] = self._gtk.HomogeneousGrid()
        self.labels['reflash_design'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['reflash_design'])

    def on_image_clicked(self, widget, event):
        if self.clicks >= 10:
            self.allow_first_flash()
        else:
            self.clicks += 1

    def flash(self, button):
        script_path = '/home/pi/KlipperScreen/scripts/fix/flash.sh'
        subprocess.call(['bash', script_path])

    def reflash(self, button):
        script_path = '/home/pi/KlipperScreen/scripts/fix/reflash.sh'
        subprocess.call(['bash', script_path])

    def allow_first_flash(self):
        self.buttons['FLASH'].set_sensitive(True)

    def allow_reflash(self):
        self.buttons['REFLASH'].set_sensitive(True)