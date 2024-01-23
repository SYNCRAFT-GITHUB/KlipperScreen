import logging
import gi
import subprocess
import os
import socket
import shutil
import datetime

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ExecuteScript(*args)

class ExecuteScript(ScreenPanel):

    def __init__(self, screen, title):
        
        self.fix_option: str = self._config.get_fix_option()

        super().__init__(screen, title)
        self.menu = ['execute_script_panel']

        self.buttons = {
            'EXECUTE': self._gtk.Button("resume", None, None),
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

    def execute(self, button):

        fix_option = self._config.get_fix_option()
        offline_scripts = ["UPDATEVIAUSB", "CLEANGCODEFILES", "EXPORTLOGSTOUSB"]

        if not self._config.internet_connection() and fix_option not in offline_scripts:
            message: str = _("This procedure requires internet connection")
            self._screen.show_popup_message(message, level=2)
            return None

        if (fix_option == "FILES"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/files.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "FILES_BOWDEN"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/files_bowden.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "FILES_FEEDER"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/files_feeder.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "KLIPPERSCREEN"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/klipperscreen.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "MAINSAIL"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/mainsail.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "CAMERA"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/camera.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "LIGHT"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/light.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "CLEANGCODEFILES"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/cleangcodefiles.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "MOONRAKER"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/moonraker.sh'
            subprocess.call(['bash', script_path])

        if (fix_option == "EXPORTLOGSTOUSB"):

            usb_path: str = "/home/pi/printer_data/gcodes/USB"
            if os.path.exists(usb_path):
                if len(os.listdir(usb_path)) == 0:
                    message: str = _("USB not inserted into Printer")
                    self._screen.show_popup_message(message, level=2)
                else:
                    script_path = '/home/pi/KlipperScreen/scripts/fix/exportlogstousb.sh'
                    subprocess.call(['bash', script_path])
                    self._screen.reload_panels()
            else:
                message: str = _("Error")
                self._screen.show_popup_message(message, level=2)

        if (fix_option == "UPDATEVIAUSB"):

            path: str = '/home/pi/printer_data/gcodes/USB/SYNCRAFT/update.sh'

            if not os.path.exists(path):
                message: str = _("Update File not found")
                self._screen.show_popup_message(message, level=2)

            elif os.path.exists(path):
                script_path = path
                subprocess.call(['bash', script_path])
