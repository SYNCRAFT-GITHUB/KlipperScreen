import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return FixSpecificPanel(*args)

class FixSpecificPanel(ScreenPanel):

    def __init__(self, screen, title):

        self.fix_option: str = self._config.get_fix_option()

        self.page = {
            'CURRENT': 0,
            'PREVIOUS': 0,
            'MAX': 3
        }

        text_step_0: str = _("Please follow the tutorial to ensure everything performs correctly.")
        text_step_1: str = _("Do not turn off Syncraft during the procedure, and keep a stable internet connection.")
        text_step_2: str = _("Interrupting this procedure can result in problems for the internal system.")
        text_step_3: str = _("At the end, Syncraft will restart.")

        image_step_0 = self._gtk.Image("compass", self._gtk.content_width * .5, self._gtk.content_height * .5)
        image_step_1 = self._gtk.Image("square-warning-electricity", self._gtk.content_width * .6, self._gtk.content_height * .6)
        image_step_2 = self._gtk.Image("warning", self._gtk.content_width * .5, self._gtk.content_height * .5)
        image_step_3 = self._gtk.Image("refresh", self._gtk.content_width * .5, self._gtk.content_height * .5)

        self.texts = [text_step_0, text_step_1, text_step_2, text_step_3]
        self.images = [image_step_0, image_step_1, image_step_2, image_step_3]

        super().__init__(screen, title)
        self.menu = ['fix_specific_panel']

        self.buttons = {
            'NEXT_PAGE': self._gtk.Button("arrow-right", None, None),
            'PREVIOUS_PAGE': self._gtk.Button("arrow-left", None, None),
            'START': self._gtk.Button("resume", _("Start"), "color1"),
        }
        self.buttons['NEXT_PAGE'].connect("clicked", self.nextpage)
        self.buttons['PREVIOUS_PAGE'].connect("clicked", self.previouspage)
        self.buttons['START'].connect("clicked", self.nothing)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['NEXT_PAGE'], 1, 1, 1, 1)
        grid.attach(self.buttons['PREVIOUS_PAGE'], 0, 1, 1, 1)

        self.load_everything_on_screen(gridvariable=grid)

    def remove_all_from_screen(self):
        self.info.remove(self.images[self.page['PREVIOUS']])
        self.content.remove(self.labels['text'])
        self.content.remove(self.labels['fix_specific_panel'])

    def load_everything_on_screen(self, gridvariable):
        self.set_image()
        self.create_and_set_text()
        self.set_homogeneousgrid(gridvariable=gridvariable)

    def create_and_set_text(self):
        self.labels['text'] = Gtk.Label(self.texts[self.page['CURRENT']])
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        self.content.add(self.labels['text'])

    def set_image(self):
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.images[self.page['CURRENT']], True, True, 8)
        self.content.add(self.info)

    def set_homogeneousgrid(self, gridvariable):
        self.labels['fix_specific_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_specific_panel'].attach(gridvariable, 0, 0, 1, 2)
        self.content.add(self.labels['fix_specific_panel'])

    def nextpage (self, button):
        if not (self.page['CURRENT'] + 1 > self.page['MAX']):
            self.page['PREVIOUS'] = self.page['CURRENT']
            self.page['CURRENT'] += 1
            self.remove_all_from_screen()
            self.load_everything_on_screen()

    def previouspage (self, button):
        if not (self.page['CURRENT'] - 1 < 0):
            self.page['PREVIOUS'] = self.page['CURRENT']
            self.page['CURRENT'] -= 1
            self.remove_all_from_screen()
            self.load_everything_on_screen()


    def nothing (self, button):
        pass