import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return TimezoneSelect(*args)


class TimezoneSelect(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)

        class Timezone:
            def __init__ (self, region: str, location: str):
                self.region = region
                self.location = location
            def code (self):
                index: str = f"{self.region}/{self.location}"
                return index
            def name (self):
                index: str = f"{self.region[:2].upper()} {self.location}"
                return (index.replace("_", " ")).replace("/", " ")

        self.timezones = [
            Timezone(region='Africa', location='Algiers'),
            Timezone(region='Africa', location='Cairo'),
            Timezone(region='Africa', location='Casablanca'),
            Timezone(region='Africa', location='Cape_Town'),
            Timezone(region='Africa', location='Lagos'),
            Timezone(region='Africa', location='Nairobi'),
            Timezone(region='America', location='Chicago'),
            Timezone(region='America', location='Los_Angeles'),
            Timezone(region='America', location='Mexico_City'),
            Timezone(region='America', location='New_York'),
            Timezone(region='America', location='Sao_Paulo'),
            Timezone(region='America', location='Buenos_Aires'),
            Timezone(region='America', location='Lima'),
            Timezone(region='America', location='Toronto'),
            Timezone(region='America', location='Vancouver'),
            Timezone(region='Asia', location='Bangkok'),
            Timezone(region='Asia', location='Dubai'),
            Timezone(region='Asia', location='Hong_Kong'),
            Timezone(region='Asia', location='Kolkata'),
            Timezone(region='Asia', location='Tokyo'),
            Timezone(region='Asia', location='Beijing'),
            Timezone(region='Asia', location='Jakarta'),
            Timezone(region='Asia', location='Seoul'),
            Timezone(region='Asia', location='Taipei'),
            Timezone(region='Australia', location='Melbourne'),
            Timezone(region='Australia', location='Sydney'),
            Timezone(region='Australia', location='Brisbane'),
            Timezone(region='Australia', location='Perth'),
            Timezone(region='Europe', location='Amsterdam'),
            Timezone(region='Europe', location='Berlin'),
            Timezone(region='Europe', location='London'),
            Timezone(region='Europe', location='Moscow'),
            Timezone(region='Europe', location='Paris'),
            Timezone(region='Europe', location='Rome'),
            Timezone(region='Europe', location='Stockholm'),
            Timezone(region='Europe', location='Athens'),
            Timezone(region='Europe', location='Brussels'),
            Timezone(region='Europe', location='Budapest'),
            Timezone(region='Europe', location='Dublin'),
            Timezone(region='Europe', location='Istanbul'),
            Timezone(region='Europe', location='Vienna'),
            Timezone(region='Europe', location='Warsaw'),
            Timezone(region='Pacific', location='Fiji'),
            Timezone(region='Pacific', location='Auckland'),
            Timezone(region='Pacific', location='Honolulu'),
            Timezone(region='Pacific', location='Guam'),
            Timezone(region='Pacific', location='Majuro'),
            Timezone(region='Pacific', location='Papeete'),
            Timezone(region='Pacific', location='Guadalcanal'),
            Timezone(region='Pacific', location='Port_Moresby'),
            Timezone(region='Pacific', location='Suva'),
            Timezone(region='Pacific', location='Wake')
        ]

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        columns = 4

        for i, timezone in enumerate(self.timezones):
            name: str = timezone.name()
            name = f"{name[:13]}." if len(name) > 13 else name
            self.labels[name] = self._gtk.Button("timezone", f"{name}", f"color{1 + i % 4}")
            self.labels[name].connect("clicked", self.apply_timezone, timezone.code())
            if self._screen.vertical_mode:
                row = i % columns
                col = int(i / columns)
            else:
                col = i % columns
                row = int(i / columns)
            grid.attach(self.labels[name], col, row, 1, 1)

        name: str = timezone.name()
        self.labels[name] = self._gtk.Button(None, _("My timezone is not on the list"), None)
        self.labels[name].connect("clicked", self.show_insert_custom_timezone)
        if self._screen.vertical_mode:
            row = i % columns
            col = int(i / columns)
        else:
            col = i % columns
            row = int(i / columns)
        grid.attach(self.labels[name], 0, row+1, columns, 1)

    def show_insert_custom_timezone(self, widget):

        for child in self.content.get_children():
            self.content.remove(child)

        pl = self._gtk.Label(f"{_('Insert your timezone')}: ({_('Example')}: 'america new york')")
        pl.set_hexpand(False)
        self.labels['timezone_name'] = Gtk.Entry()
        self.labels['timezone_name'].set_text('')
        self.labels['timezone_name'].set_hexpand(True)
        self.labels['timezone_name'].connect("activate", self.apply_timezone_by_text)
        self.labels['timezone_name'].connect("focus-in-event", self._screen.show_keyboard)

        save = self._gtk.Button("complete", _("Save"), "color3")
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

    def apply_timezone(self, widget, code):
        command = f"sudo timedatectl set-timezone {code}"
        subprocess.call(command, shell=True)
        self._screen.restart_ks()

    def apply_timezone_by_text(self, widget):

        code = self.labels['timezone_name'].get_text()

        magic_words = ['welcome', 'help', 'kill', 'restart']
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