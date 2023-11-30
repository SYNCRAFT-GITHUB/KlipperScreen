import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return Configurations(*args)

class Configurations(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['configurations']

        self.buttons = {
            'DEFAULT_UNLOAD': self._gtk.Button("arrow-down", "default unload", "color1"),
            'HOT_UNLOAD': self._gtk.Button("brightness", "hot unload", "color2"),
        }

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['DEFAULT_UNLOAD'], 0, 0, 1, 1)
        grid.attach(self.buttons['HOT_UNLOAD'], 0, 1, 1, 1)

        self.content.add(grid)

        self.labels['configurations'] = self._gtk.HomogeneousGrid()
        self.labels['configurations'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['configurations'])