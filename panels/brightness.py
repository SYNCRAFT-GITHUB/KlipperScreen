import logging
import subprocess
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ScreenBrightness(*args)

class ScreenBrightness(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['screen_bright']

        self.image = self._gtk.Image(f"screen", self._gtk.content_width * 4, self._gtk.content_height * .6)

        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        #self.content.add(self.info)

        self.buttons = {
            'LOW': self._gtk.Button("brightness-low", None, None),
            'NORMAL': self._gtk.Button("brightness-normal", None, None),
            'HIGH': self._gtk.Button("brightness-high", None, None),
        }
        self.buttons['LOW'].connect("clicked", self.set_brightness, 25)
        self.buttons['NORMAL'].connect("clicked", self.set_brightness, 100)
        self.buttons['HIGH'].connect("clicked", self.set_brightness, 255)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['HIGH'], 1, 0, 1, 1)
        grid.attach(self.buttons['LOW'], 1, 2, 1, 1)
        grid.attach(self.buttons['NORMAL'], 1, 1, 1, 1)

        self.labels['screen_bright'] = self._gtk.HomogeneousGrid()
        self.labels['screen_bright'].attach(grid, 0, 0, 3, 3)
        self.content.add(self.labels['screen_bright'])

    def set_brightness (self, button, value):
        bash_command = f"echo {value} | sudo tee /sys/class/backlight/*/brightness"
        try:
            subprocess.run(bash_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")