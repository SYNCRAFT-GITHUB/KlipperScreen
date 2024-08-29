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

FILE_FIX_SCRIPT_PATHS = {
    "FILES_V3": "/home/pi/KlipperScreen/scripts/fix/files_v3.sh",
    "FILES_BOWDEN": "/home/pi/KlipperScreen/scripts/fix/files_bowden.sh",
    "FILES_FEEDER": "/home/pi/KlipperScreen/scripts/fix/files_feeder.sh",
    "FILES_METAL": "/home/pi/KlipperScreen/scripts/fix/files_metal.sh",
    "KLIPPERSCREEN": "/home/pi/KlipperScreen/scripts/fix/klipperscreen.sh",
    "MAINSAIL": "/home/pi/KlipperScreen/scripts/fix/mainsail.sh",
    "CAMERA": "/home/pi/KlipperScreen/scripts/fix/camera.sh",
    "LIGHT": "/home/pi/KlipperScreen/scripts/fix/light.sh",
    "CLEANGCODEFILES": "/home/pi/KlipperScreen/scripts/fix/cleangcodefiles.sh",
    "MOONRAKER": "/home/pi/KlipperScreen/scripts/fix/moonraker.sh"
}

def create_panel(*args):
    return ExecuteScript(*args)

class ExecuteScript(ScreenPanel):

    def __init__(self, screen, title):
        
        self.fix_option: str = self._config.get_fix_option()

        super().__init__(screen, title)
        self.menu = ['execute_script_panel']

        self.buttons = {
            'CONFIRM': self._gtk.Button("complete", _("Confirm"), "color1"),
            'EXECUTE': self._gtk.Button("resume", "...", "color2"),
        }
        self.buttons['CONFIRM'].connect("clicked", self.confirm)
        self.buttons['EXECUTE'].connect("clicked", self.execute)

        grid = self._gtk.HomogeneousGrid()

        text = Gtk.Label()
        text.set_markup(f"<b>{_('Please confirm before proceeding')}</b>\n")
        text.set_hexpand(True)
        text.set_halign(Gtk.Align.CENTER)
        text.set_vexpand(True)
        text.set_valign(Gtk.Align.CENTER)
        text.set_line_wrap(True)
        text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        self.buttons['EXECUTE'].set_sensitive(False)

        grid.attach(text, 0, 0, 3, 1)
        grid.attach(self.buttons['CONFIRM'], 0, 1, 1, 3)
        grid.attach(self.buttons['EXECUTE'], 1, 1, 2, 3)

        self.labels['execute_script_panel'] = self._gtk.HomogeneousGrid()
        self.labels['execute_script_panel'].attach(grid, 0, 0, 1, 2)
        self.content.add(self.labels['execute_script_panel'])

    def confirm(self, button):
        self.buttons['EXECUTE'].set_sensitive(True)
        self.buttons['CONFIRM'].set_sensitive(False)
        self.buttons['CONFIRM'].set_label(_("Confirmed"))
        self.buttons['EXECUTE'].set_label(_("Start"))

    def execute(self, button):
        self.buttons['EXECUTE'].set_sensitive(False)
        self.buttons['CONFIRM'].set_sensitive(True)
        self.buttons['CONFIRM'].set_label(_("Confirm"))
        self.buttons['EXECUTE'].set_label("...")

        fix_option = self._config.get_fix_option()
        offline_scripts = ["DETECT_ERROR", "UPDATEVIAUSB", "CLEANGCODEFILES", "EXPORTLOGSTOUSB"]

        if not self._config.internet_connection() and fix_option not in offline_scripts:
            message: str = _("This procedure requires internet connection")
            self._screen.show_popup_message(message, level=2)
            return None

        if (fix_option == "DETECT_ERROR"):
            message: str = _("Unable to auto-detect")
            self._screen.show_popup_message(message, level=2)
            return None

        if (fix_option in FILE_FIX_SCRIPT_PATHS):
            script_path = FILE_FIX_SCRIPT_PATHS.get(fix_option)
            script_exit_code = subprocess.call(["bash", script_path])
            if (script_exit_code != 0):
                # FIXME: String literal porque editar a tradução .po não funciona 
                self._screen.show_popup_message(
                    "A correção de arquivos falhou, verifique sua conexão com a internet",
                    level=3 # message_popup_error
                )

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
