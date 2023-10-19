import logging
import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel

def create_panel(*args):
    return FilamentPanel(*args)


class FilamentPanel(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.menu = ['add_filament_menu']
        grid = self._gtk.HomogeneousGrid()

        self.bools = {
            'ST025': False,
            'ST04': False,
            'ST08': False,
            'METAL04': False,
            'FIBER06': False,
        }

        dev = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2) # 5
        dev.get_style_context().add_class("frame-item")
        dev.set_hexpand(True)
        dev.set_vexpand(False)
        dev.set_valign(Gtk.Align.CENTER)

        for key, value in bools.items():

            name = Gtk.Label()
            name.set_markup(f"<big><b>{key}</b></big>")
            name.set_hexpand(True)
            name.set_vexpand(True)
            name.set_halign(Gtk.Align.START)
            name.set_valign(Gtk.Align.CENTER)
            name.set_line_wrap(True)
            name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

            labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            labels.add(name)

            switch = Gtk.Switch()
            switch.set_active(self.bools['ST025'])
            switch.connect("notify::active", self.test)
            dev.add(switch)
            self.content.add(dev)
            self.content.add(dev)
            self.content.add(dev)

        self.labels['text'] = Gtk.Label(f"Mamma Mia! :D")

        #grid.attach(self.buttons['ST025'], 0, 0, 1, 1)
        #grid.attach(self.buttons['ST04'], 1, 0, 1, 1)
        #grid.attach(self.buttons['ST08'], 2, 0, 1, 1)
        #grid.attach(self.buttons['FIBER06'], 3, 0, 1, 1)
        #grid.attach(self.buttons['METAL04'], 4, 0, 1, 1)

        self.labels['add_filament_menu'] = self._gtk.HomogeneousGrid()
        self.labels['add_filament_menu'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['text'])
        self.content.add(self.labels['add_filament_menu'])

        pl = self._gtk.Label(_('INSERT FILAMENT NAME'))
        pl.set_hexpand(False)
        self.labels['filament_name'] = Gtk.Entry()
        self.labels['filament_name'].set_text('')
        self.labels['filament_name'].set_hexpand(True)
        self.labels['filament_name'].connect("activate", self.apply_custom_filament)
        self.labels['filament_name'].connect("focus-in-event", self._screen.show_keyboard)

        save = self._gtk.Button("complete", _("Save"), "color3")
        save.set_hexpand(False)
        save.connect("clicked", self.apply_custom_filament)

        box = Gtk.Box()
        box.pack_start(self.labels['filament_name'], True, True, 5)
        box.pack_start(save, False, False, 5)

        self.labels['insert_name'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.labels['insert_name'].set_valign(Gtk.Align.CENTER)
        self.labels['insert_name'].set_hexpand(True)
        self.labels['insert_name'].set_vexpand(True)
        self.labels['insert_name'].pack_start(pl, True, True, 5)
        self.labels['insert_name'].pack_start(box, True, True, 5)

        self.content.add(self.labels['insert_name'])
        self.labels['filament_name'].grab_focus_without_selecting()

    def apply_custom_filament(self, widget):

        code = self.labels['filament_name'].get_text()

    def test(self, widget, text):
        if self.bools["ST025"]:
            self.bools["ST025"] = False
        else:
            self.bools["ST025"] = True
        print(f'TEST FUNCTION: {self.bools["ST025"]}')