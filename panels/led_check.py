import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return LedCheckPanel(*args)

class LedCheckPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)

        grid = self._gtk.HomogeneousGrid()

        self.labels['text'] = Gtk.Label(f"\n")
        self.content.add(self.labels['text'])
        
        self.above = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.below = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.spacer.set_vexpand(True)
        self.spacer.set_hexpand(False)
        self.spacer.set_halign(Gtk.Align.CENTER) 

        self.create_image_button("led_print_success", self.above, "print_success")
        self.create_image_button("led_status_cancel", self.above, "status_cancel")
        self.create_image_button("led_status_pause", self.above, "status_pause")
        self.create_image_button("led_status_heating_front_leds", self.below, "status_heating_front_leds")
        self.create_image_button("led_progress_bar_idle", self.below, "progress_bar_idle")

        self.content.add(self.above)
        self.content.add(self.below)
        
    def create_image_button(self, image_path, box, macro):
        event_box = Gtk.EventBox()
        image = self._gtk.Image(image_path, self._gtk.content_width * 4, self._gtk.content_height * .4, universal=True)
        event_box.add(image)
        event_box.connect("button-press-event", self.on_image_clicked, macro)
        box.pack_start(event_box, True, True, 8)

    def on_image_clicked(self, widget, event, macro):
        self.execute_macro(widget, macro)

    def execute_macro(self, widget, macro: str):
        self._screen._ws.klippy.gcode_script(macro)