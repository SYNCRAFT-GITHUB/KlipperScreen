import logging
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

        self.image = self._gtk.Image("eletro-warning", self._gtk.content_width * 4, self._gtk.content_height * .6, universal=True)

        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.content.add(self.info)

        self.text = f"""
        {_("This procedure will re-flash the controller board.")}
        {_("After this quick procedure, the machine will restart.")}
        {_("Do not proceed if you are not sure what you are doing.")}
        """

        self.labels['text'] = Gtk.Label(self.text)
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        
        self.content.add(self.labels['text'])

        self.buttons = {
            'OK': self._gtk.Button(None, _("Start"), "color1"),
        }
        self.buttons['OK'].connect("clicked", self.confirm)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['OK'], 1, 0, 1, 1)

        self.labels['reflash_design'] = self._gtk.HomogeneousGrid()
        self.labels['reflash_design'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['reflash_design'])

    def confirm(self, button):
        script_path = '/home/pi/KlipperScreen/scripts/fix/reflash.sh'
        subprocess.call(['bash', script_path])