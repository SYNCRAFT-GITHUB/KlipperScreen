import gi
import subprocess
import git
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return UpdateWeb(*args)


class UpdateWeb(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)

        class SystemAction:
            def __init__ (self, name: str, code: str, icon: str, path: str):
                self.path = path
                self.name = name
                self.code = code
                self.icon = icon

        softwares_path = os.path.join('/home', 'pi', 'SyncraftCore', 'softwares')

        class DIR:
            LED = os.path.join(softwares_path, 'klipper-led_effect')
            PDC = os.path.join(softwares_path, 'printerdataconfig')
            KS = os.path.join(softwares_path, 'KlipperScreen')
            MAINSAIL = os.path.join(softwares_path, 'mainsail')
            MOONRAKER = os.path.join(softwares_path, 'moonraker')
            KLIPPER = os.path.join(softwares_path, 'klipper')

        self.actions = [
            SystemAction(f"{_('Essential Files')}",   code='UPDATE_PDC',          icon='file',      path=DIR.PDC),
            SystemAction(f"{_('KlipperScreen')}",     code='UPDATE_KS',           icon='screen',    path=DIR.KS),
            SystemAction(f"{_('Mainsail')}",          code='UPDATE_MAINSAIL',     icon='monitor',   path=DIR.MAINSAIL),
            SystemAction(f"{_('Moonraker')}",         code='UPDATE_MOONRAKER',    icon='moonraker', path=DIR.MOONRAKER),
            SystemAction(f"{_('LED Light Driver')}",  code='UPDATE_KLE',          icon='light',     path=DIR.LED),
        ]

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        columns = 1

        for i, action in enumerate(self.actions):

            name: str = action.name
            style_context = 'updated'

            repo_status = self._config.repo_status(action.path)

            if repo_status == 'up-to-date':
                name = f'{_("This software is already updated")}'
                style_context = 'updated'
            if repo_status == 'outdated':
                name = f'{_("Update required").upper()}: {action.name}'
                style_context = 'invalid'
            elif repo_status == 'error':
                name = f'{_("Error")}: {action.name}'.upper()
                style_context = 'problem'

            self.labels[action.code] = self._gtk.Button(action.icon, f"{name}", f"color{1 + i % 4}")
            self.labels[action.code].get_style_context().add_class(style_context)
            self.labels[action.code].connect("clicked", self.set_fix_option_to, action.code)
            self.labels[action.code].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
            })
            if self._screen.vertical_mode:
                row = i % columns
                col = int(i / columns)
            else:
                col = i % columns
                row = int(i / columns)
            grid.attach(self.labels[action.code], col, row, 1, 1)


    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)