import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from ks_includes.screen_panel import ScreenPanel
import subprocess

def create_panel(*args):
    return CustomTimezone(*args)

class CustomTimezone(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)

        pl = self._gtk.Label(f"{_('Insert your timezone')}: ({_('Example')}: 'america new york')")
        pl.set_hexpand(False)
        self.labels['timezone_name'] = Gtk.Entry()
        self.labels['timezone_name'].set_text('')
        self.labels['timezone_name'].set_hexpand(True)
        self.labels['timezone_name'].connect("activate", self.apply_timezone_by_text)
        self.labels['timezone_name'].connect("focus-in-event", self._screen.show_keyboard)

        save = self._gtk.Button(None, _("Save Config"), "color3")
        save.set_hexpand(False)
        save.connect("clicked", self.apply_timezone_by_text)

        box = Gtk.Box()
        box.pack_start(self.labels['timezone_name'], True, True, 5)
        box.pack_start(save, False, False, 5)

        self.labels['insert_timezone'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.labels['insert_timezone'].set_valign(Gtk.Align.CENTER)
        self.labels['insert_timezone'].set_hexpand(True)
        self.labels['insert_timezone'].set_vexpand(True)
        self.labels['insert_timezone'].pack_start(pl, True, True, 5)
        self.labels['insert_timezone'].pack_start(box, True, True, 5)

        self.content.add(self.labels['insert_timezone'])
        self.labels['timezone_name'].grab_focus_without_selecting()
        
    def apply_timezone_by_text(self, widget):

        code = self.labels['timezone_name'].get_text()

        magic_words = ['welcome', 'newlogo', 'regress', 'help', 'kill', 'restart']
        if code in magic_words:
            self.magic(code=code)
            return

        code = code.title()
        code = code.replace(" ", "/", 1)
        code = code.replace(" ", "_")
        command = f"sudo timedatectl set-timezone {code}"
        subprocess.call(command, shell=True)
        self._screen.restart_ks()

    def magic(self, code):

        if code == 'welcome':
            self.set_bool_config_option(section="hidden", option="welcome", boolean=True)
            self._screen.reload_panels()

        if code == 'newlogo':
            self.set_bool_config_option(section="hidden", option="new_logo", boolean=True)
            self._screen.reload_panels()

        if code == 'regress':
            self.set_bool_config_option(section="hidden", option="new_logo", boolean=False)
            self._screen.reload_panels()

        if code == 'help':
            message: str = _("Let me guess... Someone stole your Sweetroll")
            self._screen.show_popup_message(message, level=1)
            self._screen.remove_keyboard()

        if code == 'kill':
            kill_command = "sudo service KlipperScreen stop"
            subprocess.call(kill_command, shell=True)

        if code == 'restart':
            kill_command = "sudo service KlipperScreen restart"
            subprocess.call(kill_command, shell=True)