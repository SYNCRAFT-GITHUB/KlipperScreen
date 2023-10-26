import logging
import re
import random
import json
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel
from .material_load import CustomPrinterMaterial

def create_panel(*args):
    return AddCustomMaterial(*args)

error_messages = [
    _("An error has occurred"),
    _("This name cannot be used"),
    _("Select at least one Extruder"),
    _("The maximum limit has been reached")
]

class AddCustomMaterial(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)
        i: int = 0

        self.bools = {
            'ST025': False,
            'ST04': False,
            'ST08': False,
            'METAL04': False,
            'FIBER06': False,
        }

        self.materials_json_path = self._config.materials_path(custom=False)
        self.custom_json_path = self._config.materials_path(custom=True)

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        textfield_label = self._gtk.Label(f"{_('Insert Material Name')}")
        textfield_label.set_hexpand(False)
        self.labels['filament_name'] = Gtk.Entry()
        self.labels['filament_name'].set_text('')
        self.labels['filament_name'].set_hexpand(True)
        self.labels['filament_name'].connect("activate", self.apply_custom_filament)
        self.labels['filament_name'].connect("focus-in-event", self._screen.show_keyboard)

        box = Gtk.Box()
        box.pack_start(self.labels['filament_name'], True, True, 5)

        self.labels['insert_name'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.labels['insert_name'].set_valign(Gtk.Align.CENTER)
        self.labels['insert_name'].set_hexpand(True)
        self.labels['insert_name'].set_vexpand(True)
        self.labels['insert_name'].pack_start(textfield_label, True, True, 5)
        self.labels['insert_name'].pack_start(box, True, True, 5)

        grid.attach(self.labels['insert_name'], 0, (i), 3, 1)
        i += 1
        self.labels['filament_name'].grab_focus_without_selecting()

        self.labels['text_nozzle'] = Gtk.Label(_('Select which extruders are compatible'))
        grid.attach(self.labels['text_nozzle'], 0, (i), 3, 1)
        i += 1

        for key, value in self.bools.items():

            dev = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5) # 5
            dev.get_style_context().add_class("frame-item")
            dev.set_hexpand(True)
            dev.set_vexpand(False)
            dev.set_valign(Gtk.Align.CENTER)

            key_title: str = key
            if 'ST025' in key:
                key_title = f'Standard 0.25{_("mm")}'
            elif 'ST04' in key:
                key_title = f'Standard 0.4{_("mm")}'
            elif 'ST08' in key:
                key_title = f'Standard 0.8{_("mm")}'
            elif 'FIBER06' in key:
                key_title = f'Fiber 0.6{_("mm")}'
            elif 'METAL04' in key:
                key_title = f'Metal 0.4{_("mm")}'

            name = Gtk.Label()
            name.set_markup(f"<big><b>{key_title}</b></big>")
            name.set_hexpand(True)
            name.set_vexpand(True)
            name.set_halign(Gtk.Align.START)
            name.set_valign(Gtk.Align.CENTER)
            name.set_line_wrap(True)
            name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

            labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            labels.add(name)
            dev.add(labels)

            switch = Gtk.Switch()
            switch.set_active(self.bools[key])
            switch.connect("notify::active", self.toggle_bool, key)
            dev.add(switch)
            grid.attach(dev, 0, i, 3, 1)
            i += 1

        self.temp_value: int = 225
        self.default_temp_text = f"{_('Extrusion Temperature for the Material')}: {self.temp_value}"
        self.labels['text_temp'] = Gtk.Label(self.default_temp_text)
        grid.attach(self.labels['text_temp'], 0, (i), 3, 1)
        i += 1

        self.labels['plus_button'] = self._gtk.Button("increase", None, f"color{random.randint(1, 4)}")
        self.labels['plus_button'].connect("clicked", self.increase_temp, 5)
        self.labels['minus_button'] = self._gtk.Button("decrease", None, f"color{random.randint(1, 4)}")
        self.labels['minus_button'].connect("clicked", self.decrease_temp, 5)

        grid.attach(self.labels['plus_button'], 2, (i), 1, 1)
        grid.attach(self.labels['minus_button'], 0, (i), 1, 1)
        i += 1

        self.labels['finish'] = self._gtk.Button("complete", _('Add Custom Material'), f"color1")
        self.labels['finish'].connect("clicked", self.apply_custom_filament)
        grid.attach(self.labels['finish'], 0, (i), 3, 2)
        i += 2

        self.labels['export_usb'] = self._gtk.Button("usb-save", _('Export custom materials to USB'), "color2")
        self.labels['export_usb'].connect("clicked", self.set_fix_option_to, "EXPORTCUSTOMMATERIALSTOUSB")
        self.labels['export_usb'].connect("clicked", self.menu_item_clicked, "update_usb", {
            "name": _("System"),
            "panel": "script"
        })
        grid.attach(self.labels['export_usb'], 0, (i), 3, 1)
        i += 1

        self.labels['import_usb'] = self._gtk.Button("usb", _('Import custom materials from USB'), "color2")
        self.labels['import_usb'].connect("clicked", self.set_fix_option_to, "IMPORTCUSTOMMATERIALSFROMUSB")
        self.labels['import_usb'].connect("clicked", self.menu_item_clicked, "update_usb", {
            "name": _("System"),
            "panel": "script"
        })
        grid.attach(self.labels['import_usb'], 0, (i), 3, 1)
        i += 1

        self.labels['clear_all'] = self._gtk.Button("stock", _('Delete all custom Materials'), None)
        self.labels['clear_all'].connect("clicked", self.clear_all)
        grid.attach(self.labels['clear_all'], 0, (i), 3, 1)
        i += 1


    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def apply_custom_filament(self, widget):

        if not os.path.isfile(self.custom_json_path):
            with open(self.custom_json_path, 'w') as json_file:
                json.dump([], json_file)

        with open(self.custom_json_path, 'r') as json_file:
            try:
                custom_json_file = json.load(json_file)
            except json.JSONDecodeError:
                custom_json_file = []

        with open(self.materials_json_path, 'r') as json_file:
            try:
                materials_json_file = json.load(json_file)
            except json.JSONDecodeError:
                materials_json_file = []

        code = (self.labels['filament_name'].get_text()).lstrip()
        
        if len(code) < 3 or len(code) > 7:
            message = f"{error_messages[1]} (3...7)"
            self._screen.show_popup_message(message, level=2)
            return None
        else:
            name = code.upper()

        code = self.clean_code(code)
        compatible_extruders = []

        has_extruder: bool = False
        for key, value in self.bools.items():
            if value:
                compatible_extruders.append(key)
                has_extruder = True

        if not has_extruder:
            message = error_messages[2]
            self._screen.show_popup_message(message, level=2)
            return None

        try:
            iter(custom_json_file)
        except:
            custom_json_file = []

        for material in custom_json_file:
            if (material['name'] == name or material['code'] == code):
                message = error_messages[1]
                self._screen.show_popup_message(message, level=2)
                return None

        try:
            iter(materials_json_file)
        except:
            materials_json_file = []

        for material in materials_json_file:
            if (material['name'] == name or material['code'] == code):
                message = error_messages[1]
                self._screen.show_popup_message(message, level=2)
                return None

        new_material = {
            "name": name,
            "code": code,
            "compatible" : compatible_extruders,
            "temp": int(self.temp_value)
        }
        
        custom_json_file.append(new_material)

        if (len(custom_json_file) >= 30):
            message = error_messages[3]
            self._screen.show_popup_message(message, level=2)
            return None

        with open(self.custom_json_path, 'w') as json_file:
            json.dump(custom_json_file, json_file, indent=4)

        os.system('service KlipperScreen restart')
        self._screen.restart_ks()
        return None

    def clear_all(self, button):

        if not os.path.isfile(self.custom_json_path):
            with open(self.custom_json_path, 'w') as json_file:
                json.dump([], json_file)

        with open(self.custom_json_path, 'r') as json_file:
            try:
                custom_json_file = json.load(json_file)
            except json.JSONDecodeError:
                custom_json_file = []

        with open(self.custom_json_path, 'w') as file:
            json.dump([], file)

        os.system('service KlipperScreen restart')
        self._screen.restart_ks()
        return None
    
    def clean_code(self, text: str) -> str:
        clean_code = (re.sub(r'[^a-zA-Z0-9]', '', text)).upper()
        self.letters = self.numbers = ""
        for char in clean_code:
            if char.isalpha():
                self.letters += char
            elif char.isdigit():
                self.numbers += char
        result = self.letters + self.numbers
        return result

    def reload_temp_text(self):
        self.default_temp_text = f"{_('Extrusion Temperature for the Material')}: {self.temp_value}"

    def decrease_temp(self, button, by: int):
        self.temp_value -= by
        if not self.temp_value in range(80, 351):
            self.temp_value += by
            return None
        self.reload_temp_text()
        self.labels['text_temp'].set_label(self.default_temp_text)

    def increase_temp(self, button, by: int):
        self.temp_value += by
        if not self.temp_value in range(80, 351):
            self.temp_value -= by
            return None
        self.reload_temp_text()
        self.labels['text_temp'].set_label(self.default_temp_text)

    def toggle_bool(self, switch, state, bool_key):
        try:
            if self.bools[bool_key]:
                self.bools[bool_key] = False
            else:
                self.bools[bool_key] = True
        except:
            pass