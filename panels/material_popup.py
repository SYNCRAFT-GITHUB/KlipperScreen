import logging
import json
import os
import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes as Gcode
from ks_includes.screen_panel import ScreenPanel

class PrinterMaterial:
    def __init__ (self, name: str, code: str, compatible: [str] = [], experimental: [str] = [], temp: int=0):
        self.name = name
        self.code = code
        self.compatible = compatible
        self.experimental = experimental
        self.temp = temp

class CustomPrinterMaterial:
    def __init__ (self, name: str, code: str, compatible: [str] = [], temp: int=0):
        self.name = name
        self.code = code
        self.compatible = compatible
        self.temp = temp

def read_materials_from_json(file_path: str, custom: bool = False):

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return_array = []
            for item in data:
                if custom:
                    material = CustomPrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        compatible=item['compatible'],
                        temp=item['temp'],
                    )
                    return_array.append(material)
                else:
                    material = PrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        compatible=item['compatible'],
                        experimental=item['experimental'],
                        temp=item['temp'],
                    )
                    return_array.append(material)
            return return_array
    except FileNotFoundError:
        print(f"Not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")

def create_panel(*args):
    return MaterialPopUp(*args)

class MaterialPopUp(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['material_set_menu_popup']

        self.current_extruder = self._config.variables_value_reveal('currentextruder')
        self.nozzle: str = self._config.get_nozzle()

        self.materials_json_path = self._config.materials_path(custom=False)
        self.custom_json_path = self._config.materials_path(custom=True)

        self.materials = read_materials_from_json(self.materials_json_path)
        self.custom_materials = read_materials_from_json(self.custom_json_path, custom=True)

        self.proextruders = {
            'Standard 0.25mm': 'nozzle-ST025',
            'Standard 0.4mm': 'nozzle-ST04',
            'Standard 0.8mm': 'nozzle-ST08',
            'Metal 0.4mm': 'nozzle-METAL04',
            'Fiber 0.6mm': 'nozzle-FIBER06',
        }

        self.buttons = {}

        self.texts = [
            _("This material is considered experimental for the selected Extruder."),
            _("This action may result in unexpected results.")
            ]

        grid = self._gtk.HomogeneousGrid()

        i: int = 0
        for key, value in self.proextruders.items():
            self.labels[key] = self._gtk.Button(value, None, None)
            grid.attach(self.labels[key], i, 0, 1, 1)
            i += 1

        self.gridattach(gridvariable=grid)

        self.labels['material_set_menu_popup'] = self._gtk.HomogeneousGrid()
        self.labels['material_set_menu_popup'].attach(grid, 0, 0, 1, 3)

        self.content.remove(self.labels['material_set_menu_popup'])
        self.content.add(self.labels['material_set_menu_popup'])

        self.storegrid = grid

    def process_update(self, action, data):

        for x in self._printer.get_filament_sensors():

            if x in data:
                
                if 'enabled' in data[x]:
                    self._printer.set_dev_stat(x, "enabled", data[x]['enabled'])
                if 'filament_detected' in data[x]:
                    self._printer.set_dev_stat(x, "filament_detected", data[x]['filament_detected'])
                    if self._printer.get_stat(x, "enabled"):
                        if not data[x]['filament_detected'] and x == self._config.get_spool_option():
                            self._config.replace_filament_activity(x, "empty")
                            self._screen._menu_go_back()

        if self.get_variable('nozzle') not in self.proextruders:
            self.generic_button.set_label(_("Select Syncraft ProExtruder"))
            for key, value in self.proextruders.items():
                try:
                    self.labels[key].set_property("opacity", 0.3)
                except:
                    pass
        else:
            for key, value in self.proextruders.items():
                self.labels[key].set_property("opacity", 0.3)
            self.labels[self.nozzle].set_property("opacity", 1.0)
        

    def gridattach(self, gridvariable):

        repeat_three: int = 0
        i: int = 1

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(gridvariable)
        self.content.add(scroll)

        try:
            iter(self.materials)
        except:
            self.materials = []

        for material in self.materials:

            if self.nozzle in material.compatible:
                index_button = self._gtk.Button("circle-green", material.name, "color3")
                index_button.connect("clicked", self.confirm_set_default, material.code)
                gridvariable.attach(index_button, repeat_three, i, 1, 1)
                
                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1

        try:
            iter(self.custom_materials)
        except:
            self.custom_materials = []

        for material in self.custom_materials:
        
            if self.nozzle in material.compatible:
                allow = self.allow_custom(material)

                if allow:
                    index_button = self._gtk.Button("circle-purple", material.name, "color2")
                    index_button.connect("clicked", self.confirm_set_custom)
                else:
                    index_button = self._gtk.Button("invalid", _('Invalid'), "color2")
                    index_button.connect("clicked", self.set_invalid_material)

                gridvariable.attach(index_button, repeat_three, i, 1, 1)

                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1
                

        for material in self.materials:

            show_experimental = self._config.get_main_config().getboolean('show_experimental_material', False)
            allowed_for_experimental = ["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"]
            
            if self.nozzle in material.experimental and self.nozzle in allowed_for_experimental:
                index_button = self._gtk.Button("circle-orange", material.name, "color1")
                index_button.connect("clicked", self.confirm_set_experimental, material.code)
                if show_experimental:
                    gridvariable.attach(index_button, repeat_three, i, 1, 1)
                    if repeat_three == 4:
                        repeat_three = 0
                        i += 1
                    else:
                        repeat_three += 1

            if material.code == self.materials[-1].code:
                size: int = 1
                index: int = repeat_three
                while index != 4:
                    size += 1
                    index += 1
                self.generic_button = self._gtk.Button("circle-red", _("Generic"), "color2")
                self.generic_button.connect("clicked", self.confirm_set_custom)
                gridvariable.attach(self.generic_button, repeat_three, i, size, 1)

    def get_variable(self, key) -> str:
        return self._config.variables_value_reveal(key)

    def allow_custom(self, material: CustomPrinterMaterial) -> bool:
        pattern = r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]'
        name = material.name
        code = material.code
        if not len(name) in range(3, 8):
            return False
        if re.search(pattern, name):
            return False
        if re.search(pattern, code):
            return False
        if not material.temp in range(5, 351):
            return False
        return True

    def confirm_set_default(self, widget, code):
        self._screen._ws.klippy.gcode_script(Gcode.change_material(m=code, ext=self._config.get_extruder_option()))
        self._config.replace_filament_activity(self._config.get_spool_option(), "busy")
        self._screen._menu_go_back()

    def confirm_set_empty(self, widget):
        self._screen._ws.klippy.gcode_script(Gcode.change_material(m='empty', ext=self._config.get_extruder_option()))
        self._config.replace_filament_activity(self._config.get_spool_option(), "busy")
        self._screen._menu_go_back()

    def confirm_set_experimental(self, widget, code):
        script = Gcode.change_material(m=code, ext=self._config.get_extruder_option())
        params = {"script": script}
        self._screen._confirm_send_action(
            None,
            self.texts[0] + "\n\n" + self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        self._config.replace_filament_activity(self._config.get_spool_option(), "busy")
        self._screen._menu_go_back()

    def confirm_set_custom(self, widget):
        script = Gcode.change_material(m='GENERIC', ext=self._config.get_extruder_option())
        params = {"script": script}
        self._screen._confirm_send_action(
            None,
            self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        self._config.replace_filament_activity(self._config.get_spool_option(), "busy")
        self._screen._menu_go_back()

    def set_invalid_material(self, widget=None):
        message: str = _("Incompatible Material")
        self._screen.show_popup_message(message, level=3)
        return None