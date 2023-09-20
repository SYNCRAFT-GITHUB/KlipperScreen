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
        self.buttons['EXECUTE'].connect("clicked", self.execute_buster if self._config.linux('buster') else self.execute)

        grid = self._gtk.HomogeneousGrid()

        self.image = self._gtk.Image("gear", self._gtk.content_width * .4, self._gtk.content_height * .4)
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        grid.attach(self.buttons['EXECUTE'], 0, 0, 1, 1)

        self.labels['execute_script_panel'] = self._gtk.HomogeneousGrid()
        self.labels['execute_script_panel'].attach(grid, 0, 0, 1, 2)
        self.content.add(self.labels['execute_script_panel'])

    def execute_buster (self, button):

        fix_option = self._config.get_fix_option()
        offline_scripts = ["USB_DEFAULT", "USB_RECOVER", "CLEANGCODEFILES", "EXPORTLOGSTOUSB"]

        if not self._config.internet_connection() and fix_option not in offline_scripts:
            message: str = _("This procedure requires internet connection")
            self._screen.show_popup_message(message, level=2)
            return None

        if (fix_option == "FILES"):
            script_path = '/home/pi/KlipperScreen/scripts/fix/files.sh'
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
                    self._screen.restart_ks()
            else:
                message: str = _("Error")
                self._screen.show_popup_message(message, level=2)

        if (fix_option == "USB_DEFAULT"):

            path: str = '/home/pi/printer_data/gcodes/USB/SYNCRAFT/update.sh'

            if not os.path.exists(path):
                message: str = _("Update File not found")
                self._screen.show_popup_message(message, level=2)

            elif os.path.exists(path):
                script_path = path
                subprocess.call(['bash', script_path])

        if (fix_option == "USB_RECOVER"):

            path: str = '/home/pi/printer_data/gcodes/USB/SYNCRAFT/RECOVER/update.sh'

            if not os.path.exists(path):
                message: str = _("Backup File not found")
                self._screen.show_popup_message(message, level=2)

            elif os.path.exists(path):
                script_path = path
                subprocess.call(['bash', script_path])

    def execute(self, button):

        fix_option = self._config.get_fix_option()

        def core_script(core_script_dir: str, usb: bool = False, web=False):

            usb_machine_path: str = os.path.join('/home', 'pi', 'printer_data', 'gcodes', 'USB')
            if len(os.listdir(usb_machine_path)) == 0:
                message: str = _("USB not inserted into Printer")
                self._screen.show_popup_message(message, level=2)
                return None
            if not self._config.internet_connection() and web:
                message: str = _("This procedure requires internet connection")
                self._screen.show_popup_message(message, level=2)
                return None
            try:
                if '.sh' in core_script_dir:
                    subprocess.call(['bash', core_script_dir])

                if '.py' in core_script_dir:
                    subprocess.run(["python3", core_script_dir], check=True)
            except:
                message: str = _("Error")
                self._screen.show_popup_message(message, level=2)
                return None

        core = os.path.join('/home', 'pi', 'SyncraftCore')
        maintenance = os.path.join(core, 'scripts', 'maintenance')
        pdc_dir = os.path.join(core, 'scripts', 'pdc')
        update_dir = os.path.join(maintenance, 'update')
        revert_dir = os.path.join(maintenance, 'revert')
        
        class SCRIPT:
            class UPDATE:
                DOWNLOAD_ALL = os.path.join(core, 'scripts', 'core', 'update', 'apply.py')
                APPLY_ALL = os.path.join(update_dir, 'apply.sh')
                KLE = os.path.join(update_dir, 'kle', 'apply.sh')
                KS = os.path.join(update_dir, 'klipperscreen', 'apply.sh')
                MAINSAIL = os.path.join(update_dir, 'mainsail', 'apply.sh')
                MOONRAKER = os.path.join(update_dir, 'moonraker', 'apply.sh')
                PDC = os.path.join(pdc_dir, 'update', 'apply.py')
            class REVERT:
                APPLY_ALL = os.path.join(revert_dir, 'apply.sh')
                KLE = os.path.join(revert_dir, 'kle', 'apply.sh')
                KS = os.path.join(revert_dir, 'klipperscreen', 'apply.sh')
                MAINSAIL = os.path.join(revert_dir, 'mainsail', 'apply.sh')
                MOONRAKER = os.path.join(revert_dir, 'moonraker', 'apply.sh')
                PDC = os.path.join(pdc_dir, 'revert', 'apply.py')
            class USB:
                SLICER = os.path.join(core, 'slicer', 'apply.sh')
                LOGS = os.path.join(pdc_dir, 'logs', 'usb', 'apply.sh')

        if (fix_option == "UPDATE_ALL"):
            core_script(SCRIPT.UPDATE.DOWNLOAD_ALL)
            core_script(SCRIPT.UPDATE.APPLY_ALL)
            os.system('sudo reboot')

        if (fix_option == "REVERT_ALL"):
            core_script(SCRIPT.REVERT.APPLY_ALL)
            os.system('sudo reboot')

        if (fix_option == "UPDATE_KLE"):
            core_script(SCRIPT.UPDATE.KLE)
            self._screen.reload_panels()

        if (fix_option == "UPDATE_KS"):
            core_script(SCRIPT.UPDATE.KS)
            os.system('sudo reboot')

        if (fix_option == "UPDATE_MAINSAIL"):
            core_script(SCRIPT.UPDATE.MAINSAIL)
            os.system('sudo reboot')

        if (fix_option == "UPDATE_MOONRAKER"):
            core_script(SCRIPT.UPDATE.MOONRAKER)
            self._screen.reload_panels()

        if (fix_option == "UPDATE_PDC"):
            core_script(SCRIPT.UPDATE.PDC)
            os.system('sudo reboot')

        if (fix_option == "REVERT_KLE"):
            core_script(SCRIPT.REVERT.KLE)
            self._screen.reload_panels()

        if (fix_option == "REVERT_KS"):
            core_script(SCRIPT.REVERT.KS)
            self._screen.reload_panels()

        if (fix_option == "REVERT_MAINSAIL"):
            core_script(SCRIPT.REVERT.MAINSAIL)
            os.system('sudo reboot')

        if (fix_option == "REVERT_MOONRAKER"):
            core_script(SCRIPT.REVERT.MOONRAKER)
            self._screen.reload_panels()

        if (fix_option == "REVERT_PDC"):
            core_script(SCRIPT.REVERT.PDC)
            os.system('sudo reboot')

        if (fix_option == "USB_SLICER"):
            core_script(SCRIPT.USB.SLICER)
            self._screen.reload_panels()

        if (fix_option == "USB_LOGS"):
            core_script(SCRIPT.USB.LOGS)
            self._screen.reload_panels()
