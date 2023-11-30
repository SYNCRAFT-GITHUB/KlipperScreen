import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return BusterSyncraftPanel(*args)

class BusterSyncraftPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['syncraft_panel']

        class SyncraftPanelButton:
            def __init__(self, button: str, title: str, icon: str, panel='', show: bool = True):
                self.button = button
                self.icon = icon
                self.title = title
                self.show = show
                self.panel = panel

        
        if self._config.linux('buster'):
            self.config_buttons = [
                SyncraftPanelButton(button='UPDATE', panel='update', title=_("Update via Internet"), icon='update'),
                SyncraftPanelButton(button='UPDATEVIAUSB', panel='script', title=_("Update via USB"), icon='usb'),
                SyncraftPanelButton(button='FIX', panel='fix', title=_("Quick System Fixes"), icon='compass'),
                SyncraftPanelButton(button='EXPORTLOGSTOUSB', panel='script', title=_("Export Logs to USB"), icon='usb-save'),
            ]
        else:
            self.config_buttons = [
                SyncraftPanelButton(button='UPDATE', panel='update', title=_("Update via Internet"), icon='update'),
                SyncraftPanelButton(button='USB_ACTIONS', panel='usb_actions', title=_("USB Device"), icon='usb'),
            ]

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        columns = 2

        for i, btn in enumerate(self.config_buttons):

            self.button = self._gtk.Button(btn.icon, btn.title, f"color{random.randint(1, 4)}")
            
            self.button.connect("clicked", self.menu_item_clicked, btn.panel, {
                "name": btn.title,
                "panel": btn.panel
            })

            if btn.panel == 'script':
                self.button.connect("clicked", self.set_fix_option_to, btn.button)

            if self._screen.vertical_mode:
                row = i % columns
                col = int(i / columns)
            else:
                col = i % columns
                row = int(i / columns)
            grid.attach(self.button, col, row, 1, 1)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)