import subprocess
import gi
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
            def __init__ (self, name: str, code: str, icon: str, repo_name: str):
                self.repo_name = repo_name
                self.name = name
                self.code = code
                self.icon = icon

        softwares_path = os.path.join('/home', 'pi', 'SyncraftCore', 'softwares')
        self.need_update: bool = False

        self.actions = [
            SystemAction(f"{_('Essential Files')}",   code='UPDATE_PDC',          icon='file',      repo_name='printerdataconfig'),
            SystemAction(f"{_('KlipperScreen')}",     code='UPDATE_KS',           icon='screen',    repo_name='KlipperScreen'),
            SystemAction(f"{_('Mainsail')}",          code='UPDATE_MAINSAIL',     icon='monitor',   repo_name='mainsail'),
            SystemAction(f"{_('Moonraker')}",         code='UPDATE_MOONRAKER',    icon='moonraker', repo_name='moonraker'),
            SystemAction(f"{_('LED Light Driver')}",  code='UPDATE_KLE',          icon='light',     repo_name='klipper-led_effect'),
        ]

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)


        self.update_all_btn = self._gtk.Button('arrow-up', _('Full Update'), "color1")

        self.update_all_btn.connect("clicked", self.update_all_action)

        self.update_all_btn_space = 2
        self.update_all_btn.get_style_context().add_class('update')
        grid.attach(self.update_all_btn, 0, 0, 1, self.update_all_btn_space)

        columns = 1

        for i, action in enumerate(self.actions):

            name: str = action.name
            style_context = 'updated'
            check_script_path = os.path.join('/home', 'pi', 'SyncraftCore', 'scripts', 'check', 'repo', 'apply.py')

            command = f"python3 {check_script_path} --software {action.repo_name}"
            repo_status: str = ''

            try:
                repo_status = subprocess.check_output(command, shell=True, text=True)
            except:
                pass

            self.able_to_update: bool = False

            if 'up-to-date' in repo_status:
                name = f'{_("This software is already updated")}'
                style_context = 'updated'
            if 'outdated' in repo_status:
                name = f'{_("Update required").upper()}: {action.name}'
                style_context = 'invalid'
                self.need_update = True
                self.able_to_update = True
            if 'error' in repo_status:
                name = f'{_("Error")}: {action.name}'.upper()
                style_context = 'problem'

            self.labels[action.code] = self._gtk.Button(action.icon, f"{name}", f"color{1 + i % 4}")
            self.labels[action.code].get_style_context().add_class(style_context)

            if self.able_to_update:
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

            grid.attach(self.labels[action.code], col, row+self.update_all_btn_space, 1, 1)


    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def update_all_action(self, button):
        if self.need_update:
            self._config.replace_fix_option(newvalue='UPDATE_ALL')
            self.menu_item_clicked(widget=None, panel="script", item={
            "name": _("System"),
            "panel": "script"
            })
        else:
            message: str = _("This software is already updated")
            self._screen.show_popup_message(message, level=2)