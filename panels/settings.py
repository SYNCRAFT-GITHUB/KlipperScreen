import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return SettingsPanel(*args)


class SettingsPanel(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.printers = self.settings = {}
        self.menu = ['settings_menu']
        options = self._config.get_configurable_options().copy()
        options.append({"change_system_timezone": {
            "name": _("Change Timezone"),
            "type": "panel",
            "panel": "timezone",
            "icon": "world-web"
        }})
        options.append({"system_info": {
            "name": _("System Information"),
            "type": "panel",
            "panel": "system_info",
            "icon": "info"
        }})
        options.append({"network": {
            "name": _("Connect to WiFi"),
            "type": "panel",
            "panel": "network",
            "icon": "network"
        }})
        options.append({"clear_gcodes": {
            "name": _("Clear GCodes Folder"),
            "type": "script",
            "script": "CLEANGCODEFILES" if self._config.linux('buster') else "CLEAR_GCODES",
            "icon": "custom-script"
        }})
        options.append({"add_material": {
            "name": _("Add Material"),
            "type": "panel",
            "panel": "add_material",
            "icon": "filament_plus"
        }})
        options.append({"console": {
            "name": _("Console"),
            "type": "panel",
            "panel": "console",
            "icon": "console"
        }})
        options.append({"sensors": {
            "name": _("Sensors"),
            "type": "panel",
            "panel": "sensors",
            "icon": "sensor"
        }})
        if not self._config.linux('buster'):
            options.append({"factory_reset": {
                "name": _("Factory Reset"),
                "type": "script",
                "script": "REVERT_ALL",
                "icon": "stock"
            }})

        self.labels['settings_menu'] = self._gtk.ScrolledWindow()
        self.labels['settings'] = Gtk.Grid()
        self.labels['settings_menu'].add(self.labels['settings'])
        for option in options:
            name = list(option)[0]
            self.add_option('settings', self.settings, name, option[name])

        self.content.add(self.labels['settings_menu'])

    def activate(self):
        while len(self.menu) > 1:
            self.unload_menu()

    def back(self):
        if len(self.menu) > 1:
            self.unload_menu()
            return True
        return False

    def add_option(self, boxname, opt_array, opt_name, option):

        try:
            if option['section'] == 'hidden':
                return
        except Exception as e:
            print (f'e: {e}')
            
        if option['type'] is None:
            return
        name = Gtk.Label()
        name.set_markup(f"<big><b>{option['name']}</b></big>")
        name.set_hexpand(True)
        name.set_vexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_valign(Gtk.Align.CENTER)
        name.set_line_wrap(True)
        name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        labels.add(name)

        dev = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        dev.get_style_context().add_class("frame-item")
        dev.set_hexpand(True)
        dev.set_vexpand(False)
        dev.set_valign(Gtk.Align.CENTER)

        dev.add(labels)
        if option['type'] == "binary":
            switch = Gtk.Switch()
            switch.set_active(self._config.get_config().getboolean(option['section'], opt_name))
            switch.connect("notify::active", self.switch_config_option, option['section'], opt_name,
                           option['callback'] if "callback" in option else None)
            dev.add(switch)
        elif option['type'] == "dropdown":
            dropdown = Gtk.ComboBoxText()
            for i, opt in enumerate(option['options']):
                dropdown.append(opt['value'], opt['name'])
                if opt['value'] == self._config.get_config()[option['section']].get(opt_name, option['value']):
                    dropdown.set_active(i)
            dropdown.connect("changed", self.on_dropdown_change, option['section'], opt_name,
                             option['callback'] if "callback" in option else None)
            dropdown.set_entry_text_column(0)
            dev.add(dropdown)
        elif option['type'] == "scale":
            dev.set_orientation(Gtk.Orientation.VERTICAL)
            scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                             min=option['range'][0], max=option['range'][1], step=option['step'])
            scale.set_hexpand(True)
            scale.set_value(int(self._config.get_config().get(option['section'], opt_name, fallback=option['value'])))
            scale.set_digits(0)
            scale.connect("button-release-event", self.scale_moved, option['section'], opt_name)
            dev.add(scale)
        elif option['type'] == "printer":
            box = Gtk.Box()
            box.set_vexpand(False)
            label = Gtk.Label(f"{option['moonraker_host']}:{option['moonraker_port']}")
            box.add(label)
            dev.add(box)
        elif option['type'] == "menu":
            open_menu = self._gtk.Button("list", style="color3")
            open_menu.connect("clicked", self.load_menu, option['menu'], option['name'])
            open_menu.set_hexpand(False)
            open_menu.set_halign(Gtk.Align.END)
            dev.add(open_menu)
        elif option['type'] == "panel":
            open_panel = self._gtk.Button(option['icon'], style="color3")
            open_panel.connect("clicked", self.menu_item_clicked, option['panel'], {
            "name": option['name'],
            "panel": option['panel']
            })
            open_panel.set_hexpand(False)
            open_panel.set_halign(Gtk.Align.END)
            dev.add(open_panel)
        elif option['type'] == "script":
            open_panel = self._gtk.Button(option['icon'], style="color3")
            open_panel.connect("clicked",self.set_fix_option_to, option['script'])
            open_panel.connect("clicked", self.menu_item_clicked, "script", {
            "name": option['name'],
            "panel": "script"
            })
            open_panel.set_hexpand(False)
            open_panel.set_halign(Gtk.Align.END)
            dev.add(open_panel)

        opt_array[opt_name] = {
            "name": option['name'],
            "row": dev
        }

        opts = sorted(list(opt_array), key=lambda x: opt_array[x]['name'])
        pos = opts.index(opt_name)

        self.labels[boxname].insert_row(pos)
        self.labels[boxname].attach(opt_array[opt_name]['row'], 0, pos, 1, 1)
        self.labels[boxname].show_all()

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)
