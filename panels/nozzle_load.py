import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ChNozzleLoadPanel(*args)

class ChNozzleLoadPanel(ScreenPanel):

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

        self.create_image_button("nozzle-ST025", self.above, "Standard 0.25mm")
        self.create_image_button("nozzle-ST04", self.above, "Standard 0.4mm")
        self.create_image_button("nozzle-ST08", self.above, "Standard 0.8mm")
        self.create_image_button("nozzle-METAL04", self.below, "Metal 0.4mm")
        self.create_image_button("nozzle-FIBER06", self.below, "Fiber 0.6mm")

        self.content.add(self.above)
        self.content.add(self.below)
        
    def create_image_button(self, image_path, box, nozzle):
        event_box = Gtk.EventBox()
        image = self._gtk.Image(image_path, self._gtk.content_width * 4, self._gtk.content_height * .4)
        event_box.add(image)
        event_box.connect("button-press-event", self.on_image_clicked, nozzle)
        box.pack_start(event_box, True, True, 8)

    def on_image_clicked(self, widget, event, nozzle):
        try:
            del self._screen.panels['material_load']
        except:
            pass
        self.nozzlegcodescript(widget, nozzle)

    def nozzlegcodescript(self, widget, nozzle: str):
        self._config.replace_nozzle(newvalue=nozzle)
        self.menu_item_clicked(widget=widget, panel="material_load", item={
            "name": _("Select the Material"),
            "panel": "material_load"
        })
