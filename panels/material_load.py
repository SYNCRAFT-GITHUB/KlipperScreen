import logging
import json
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel

class PrinterMaterial:
    def __init__ (self, name: str, code: str, compatible: [str] = [], experimental: [str] = []):
        self.name = name
        self.code = code
        self.compatible = compatible
        self.experimental = experimental

class CustomPrinterMaterial:
    def __init__ (self, name: str, code: str, compatible: [str] = [], temp: int=0):
        self.name = name
        self.code = code
        self.compatible = compatible
        self.temp = temp

def read_materials_from_json(file_path: str, custom_path: str, custom: bool = False):

    if custom:
        try:
            with open(custom_path, 'r') as json_file:
                data = json.load(json_file)
                return_array = []
                for item in data:
                    material = CustomPrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        compatible=item['compatible'],
                        temp=item['temp'],
                    )
                    return_array.append(material)
                return return_array
        except FileNotFoundError:
            print(f"Not found: {file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {file_path}")

    if not custom:
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                return_array = []
                for item in data:
                    material = PrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        compatible=item['compatible'],
                        experimental=item['experimental'],
                    )
                    return_array.append(material)
                return return_array
        except FileNotFoundError:
            print(f"Not found: {file_path}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {file_path}")

def create_panel(*args):
    return ChMaterialPanel(*args)

class ChMaterialPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['material_menu']

        self.materials_json_path = self._config.materials_path(custom=False)
        self.custom_json_path = self._config.materials_path(custom=True)

        self.materials = read_materials_from_json(self.materials_json_path, self.custom_json_path)
        self.custom_materials = read_materials_from_json(self.materials_json_path, self.custom_json_path, custom=True)

        self.buttons = {}

        self.texts = [
            _("This material is considered experimental for the selected Extruder."),
            _("This action may result in unexpected results."),
            _("You are loading untested material, this may result in unexpected results."),
            _("Extrusion Temperature for the Material")
            ]

        grid = self._gtk.HomogeneousGrid()

        self.gridattach(gridvariable=grid)

        self.labels['material_menu'] = self._gtk.HomogeneousGrid()
        self.labels['material_menu'].attach(grid, 0, 0, 1, 3)

        self.content.remove(self.labels['material_menu'])
        self.content.add(self.labels['material_menu'])

        self.storegrid = grid
        

    def materialgcodescript(self, widget, material: str):
        self._screen._ws.klippy.gcode_script(f"LOAD_FILAMENT_{material}")
        for _ in range(0,2):
            self._screen._menu_go_back()

    def gridattach(self, gridvariable):

        selected_nozzle: str = self._config.get_nozzle()
        repeat_three: int = 0
        i: int = 0

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(gridvariable)
        self.content.add(scroll)

        for material in self.materials:

            if selected_nozzle in material.compatible:
                index_button = self._gtk.Button("circle-green", material.name, "color3")
                index_button.connect("clicked", self.materialgcodescript, material.code)
                gridvariable.attach(index_button, repeat_three, i, 1, 1)
                
                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1

        for material in self.custom_materials:
        
            if selected_nozzle in material.compatible:
                index_button = self._gtk.Button("circle-purple", material.name, "color2")
                index_button.connect("clicked", self.confirm_print_custom, material.code, material.temp)
                gridvariable.attach(index_button, repeat_three, i, 1, 1)
                
                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1
                

        for material in self.materials:

            show_experimental = self._config.get_main_config().getboolean('show_experimental_material', False)
            allowed_for_experimental = ["ST025", "ST04", "ST08"]
            
            if selected_nozzle in material.experimental and selected_nozzle in allowed_for_experimental:
                index_button = self._gtk.Button("circle-orange", material.name, "color1")
                index_button.connect("clicked", self.confirm_print_experimental, material.code)
                if show_experimental:
                    gridvariable.attach(index_button, repeat_three, i, 1, 1)
                    if repeat_three == 4:
                        repeat_three = 0
                        i += 1
                    else:
                        repeat_three += 1

            if selected_nozzle in allowed_for_experimental:
                if material.code == self.materials[-1].code:
                    size: int = 1
                    index: int = repeat_three
                    while index != 4:
                        size += 1
                        index += 1
                    index_button = self._gtk.Button("circle-red", _("Generic"), "color4")
                    index_button.connect("clicked", self.confirm_print_generic)
                    gridvariable.attach(index_button, repeat_three, i, size, 1)


    def confirm_print_experimental(self, widget, code):
        params = {"script": f"LOAD_FILAMENT_{code}"}
        self._screen._confirm_send_action(
            None,
            self.texts[0] + "\n\n" + self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        for _ in range(0,2):
            self._screen._menu_go_back()

    def confirm_print_custom(self, widget, code, temp: int):
        params = {"script": f"LOAD_FILAMENT_GENERIC T={temp}"}
        self._screen._confirm_send_action(
            None,
            self.texts[2] + "\n\n" + self.texts[3] + f": {temp} (°C)\n\n",
            "printer.gcode.script",
            params
        )
        for _ in range(0,2):
            self._screen._menu_go_back()

    def confirm_print_generic(self, widget):
        params = {"script": "LOAD_FILAMENT_GENERIC"}
        self._screen._confirm_send_action(
            None,
            self.texts[2] + "\n\n",
            "printer.gcode.script",
            params
        )
        for _ in range(0,2):
                self._screen._menu_go_back()

    def nothing_at_all():
        pass