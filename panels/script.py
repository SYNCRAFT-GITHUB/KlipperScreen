import logging

import gi
import subprocess
import os
import socket

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ExecuteScript(*args)

class ExecuteScript(ScreenPanel):

    def __init__(self, screen, title):
        
        self.fix_option: str = self._config.get_fix_option()
        # NONE, FILES, CAMERA, LIGHT, KLIPPERSCREEN, MAINSAIL, KLIPPER, USB_DEFAULT, USB_RECOVER

        super().__init__(screen, title)
        self.menu = ['execute_script_panel']

        self.buttons = {
            'EXECUTE': self._gtk.Button("resume", _("Start"), None),
        }
        self.buttons['EXECUTE'].connect("clicked", self.execute)

        grid = self._gtk.HomogeneousGrid()

        self.image = self._gtk.Image("gear", self._gtk.content_width * .4, self._gtk.content_height * .4)
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        grid.attach(self.buttons['EXECUTE'], 0, 0, 1, 1)

        self.labels['execute_script_panel'] = self._gtk.HomogeneousGrid()
        self.labels['execute_script_panel'].attach(grid, 0, 0, 1, 2)
        self.content.add(self.labels['execute_script_panel'])

    # NONE, FILES, CAMERA, LIGHT, KLIPPERSCREEN, KLIPPER
    def execute (self, button):

        if not self.internet_connection():
            message: str = _("This procedure requires internet connection")
            self._screen._ws.klippy.gcode_script(f"M118 {message}")
            return None

        if (self._config.get_fix_option() == "FILES"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/files.sh'
            subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "KLIPPERSCREEN"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/klipperscreen.sh'
            subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "MAINSAIL"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/mainsail.sh'
            subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "CAMERA"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/camera.sh'
            subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "LIGHT"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/light.sh'
            subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "USB_DEFAULT"):

            path: str = '/home/pi/printer_data/gcodes/USB/SYNCRAFT/update.sh'

            if not os.path.exists(path):
                message: str = _("Update File not found")
                self._screen._ws.klippy.gcode_script(f"M118 {message}")

            elif os.path.exists(path):
                script_path = path
                subprocess.call(['bash', script_path])

        if (self._config.get_fix_option() == "USB_RECOVER"):

            path: str = '/home/pi/printer_data/gcodes/USB/SYNCRAFT/RECOVER/update.sh'

            if not os.path.exists(path):
                message: str = _("Backup File not found")
                self._screen._ws.klippy.gcode_script(f"M118 {message}")

            elif os.path.exists(path):
                script_path = path
                subprocess.call(['bash', script_path])
            
    def internet_connection(self):
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            pass
        return False