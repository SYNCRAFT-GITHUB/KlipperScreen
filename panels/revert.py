import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return RevertToStock(*args)


class RevertToStock(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)

        class SystemAction:
            def __init__ (self, name: str, code: str, icon: str):
                self.name = name
                self.code = code
                self.icon = icon

        self.actions = [
            SystemAction(f"{_('Essential Files')}",      code='REVERT_PDC',          icon='file'),
            SystemAction(f"{_('KlipperScreen')}",        code='REVERT_KS',           icon='screen'),
            SystemAction(f"{_('Mainsail')}",             code='REVERT_MAINSAIL',     icon='monitor'),
            SystemAction(f"{_('Moonraker')}",            code='REVERT_MOONRAKER',    icon='moonraker'),
            SystemAction(f"{_('LED Light Driver')}",     code='REVERT_KLE',          icon='light'),
        ]

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        columns = 2

        for i, action in enumerate(self.actions):
            name: str = action.name
            self.labels[name] = self._gtk.Button(action.icon, f"{name}", None)
            self.labels[name].connect("clicked", self.set_fix_option_to, action.code)
            self.labels[name].connect("clicked", self.menu_item_clicked, "script", {
            "name": _("System"),
            "panel": "script"
        })
            if self._screen.vertical_mode:
                row = i % columns
                col = int(i / columns)
            else:
                col = i % columns
                row = int(i / columns)
            grid.attach(self.labels[name], col, row, 1, 1)

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)
