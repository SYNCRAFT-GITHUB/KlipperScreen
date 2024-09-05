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
            Timezone(region='America', location='Araguaina'),
            Timezone(region='America', location='Bahia'),
            Timezone(region='America', location='Belem'),
            Timezone(region='America', location='Boa_Vista'),
            Timezone(region='America', location='Campo_Grande'),
            Timezone(region='America', location='Paramaribo'),
            Timezone(region='America', location='Porto_Velho'),
            Timezone(region='America', location='Rio_Branco'),
            Timezone(region='America', location='Santarem'),
            Timezone(region='America', location='Buenos_Aires'),
            Timezone(region='America', location='Catamarca'),
            Timezone(region='America', location='Cordoba'),
            Timezone(region='America', location='La_Rioja'),
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
        self.labels[name] = self._gtk.Button("timezone-error", f'  {_("My timezone is not on the list")}', "color1", .94, Gtk.PositionType.LEFT, 1)
        self.labels[name].connect("clicked", self.menu_item_clicked, "v3_password_panel", {
            # FIXME: Not using _() translation strings
            "name": "Custom timezone",
            "panel": "custom_timezone"
        })
        if self._screen.vertical_mode:
            row = i % columns
            col = int(i / columns)
        else:
            col = i % columns
            row = int(i / columns)
        grid.attach(self.labels[name], 0, row+1, columns, 1)

    def apply_timezone(self, widget, code):
        command = f"sudo timedatectl set-timezone {code}"
        subprocess.call(command, shell=True)
        self._screen.restart_ks()