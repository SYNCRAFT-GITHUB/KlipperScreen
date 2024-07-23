import subprocess
import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return FixPanel(*args)

class FixPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['fix_panel']

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.buttons = {
            'FIX_FILES_AUTO': self._gtk.Button("file_branch", f'{_("Essential Files")} ({_("Automatic Detection")})', self.color()),
            'FIX_FILES_MANUAL': self._gtk.Button("file_config", _("Manually select configuration files"), self.color()),
            'CLEAN_GCODE': self._gtk.Button("clean", _("Clear GCodes Folder"), self.color()),
            'FIX_CAMERA': self._gtk.Button("camera", _("Camera Driver"), self.color()),
            'FIX_KLIPPERSCREEN': self._gtk.Button("screen", _("KlipperScreen"), self.color()),
            'FIX_MAINSAIL': self._gtk.Button("monitor", _("Mainsail"), self.color()),
            'FIX_LED': self._gtk.Button("light", _("LED Light Driver"), self.color()),
            'FIX_MOONRAKER': self._gtk.Button("moonraker", _("Moonraker"), self.color()),
            'EXPORT_LOGS_USB': self._gtk.Button("usb-save", _("Export Logs to USB"), self.color()),
            'FLASH': self._gtk.Button("board-circuit", _("Flash Controller Board"), self.color()),
        }

        self.buttons['CLEAN_GCODE'].connect("clicked", self.set_fix_option_to, "CLEANGCODEFILES")
        self.buttons['CLEAN_GCODE'].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
        })

        self.buttons['FIX_FILES_AUTO'].connect("clicked", self.auto_detect_fix_option_and_set)
        self.buttons['FIX_FILES_AUTO'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_FILES_MANUAL'].connect("clicked", self.menu_item_clicked, "branch_select", {
            "name": _("Fix"),
            "panel": "branch_select"
        })

        self.buttons['FIX_CAMERA'].connect("clicked", self.set_fix_option_to, "CAMERA")
        self.buttons['FIX_CAMERA'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.set_fix_option_to, "KLIPPERSCREEN")
        self.buttons['FIX_KLIPPERSCREEN'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        self.buttons['FIX_MAINSAIL'].connect("clicked", self.set_fix_option_to, "MAINSAIL")
        self.buttons['FIX_MAINSAIL'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        
        self.buttons['FIX_LED'].connect("clicked", self.set_fix_option_to, "LIGHT")
        self.buttons['FIX_LED'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.set_fix_option_to, "MOONRAKER")
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['EXPORT_LOGS_USB'].connect("clicked", self.set_fix_option_to, "EXPORTLOGSTOUSB")
        self.buttons['EXPORT_LOGS_USB'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Fix"),
            "panel": "script"
        })

        self.buttons['FLASH'].connect("clicked", self.menu_item_clicked, "fix_steps", {
            "name": _("Flash Controller Board"),
            "panel": "flash"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX_FILES_AUTO'], 0, 0, 4, 1)
        grid.attach(self.buttons['FIX_FILES_MANUAL'], 0, 1, 4, 1)
        grid.attach(self.buttons['FIX_CAMERA'], 0, 5, 1, 1)
        grid.attach(self.buttons['FIX_KLIPPERSCREEN'], 2, 5, 1, 1)
        grid.attach(self.buttons['FIX_MAINSAIL'], 3, 5, 1, 1)
        grid.attach(self.buttons['FIX_LED'], 1, 5, 1, 1)
        grid.attach(self.buttons['FIX_MOONRAKER'], 0, 4, 2, 1)
        grid.attach(self.buttons['FLASH'], 2, 4, 2, 1)

        scroll.add(grid)
        self.content.add(scroll)

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def auto_detect_fix_option_and_set(self, button):
        repo_path = "/home/pi/printerdataconfig"
        if not os.path.exists(repo_path):
            repo_path = "/home/pi/printer_data/config"
            if not os.path.exists(repo_path):
                self._config.replace_fix_option(newvalue="DETECT_ERROR")
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            branch_name = result.stdout.strip()
            equivalent = {
                "syncraftx1-arc-stable": "FILES_BOWDEN",
                "x1-feeder": "FILES_FEEDER",
                "metal": "FILES_METAL",
                "v3": "FILES_V3"
            }
            try:
                new_fix_option = equivalent[branch_name]
            except:
                new_fix_option = "DETECT_ERROR"
            self._config.replace_fix_option(newvalue=new_fix_option)
            msg = f"{_('File branch detected:')} {branch_name}"
            return self._screen.show_popup_message(msg, level=2)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr}")
            message: str = _("Unable to auto-detect")
            self._screen.show_popup_message(message, level=3)
            return

    def color(self) -> str:
        return f"color{random.randint(1, 4)}"