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

materials = []
custom_materials = []

materials_json_path: str = os.path.join(os.getcwd(), "ks_includes", "materials", "stock.json")
custom_json_path: str = os.path.join(os.getcwd(), "ks_includes", "materials", "custom.json")

def read_materials_from_json(file_path=materials_json_path, custom_path=custom_json_path):
    print(f'file_path: {file_path}')
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            for item in data:
                material = PrinterMaterial(
                    name=item['name'],
                    code=item['code'],
                    compatible=item['compatible'],
                    experimental=item['experimental'],
                )
                materials.append(material)
    except FileNotFoundError:
        print(f"Not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")

    try:
        with open(custom_path, 'r') as json_file:
            data = json.load(json_file)
            for item in data:
                material = CustomPrinterMaterial(
                    name=item['name'],
                    code=item['code'],
                    compatible=item['compatible'],
                    temp=item['temp'],
                )
                custom_materials.append(material)
    except FileNotFoundError:
        print(f"Not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")

read_materials_from_json()

def create_panel(*args):
    return ChMaterialPanel(*args)

class ChMaterialPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['material_menu']

        self.buttons = {}

        self.texts = [
            _("This material is considered experimental for the selected Extruder."),
            _("This action may result in unexpected results."),
            _("You are loading untested material, this may result in unexpected results.")
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

        for material in materials:

            if selected_nozzle in material.compatible:
                index_button = self._gtk.Button("circle-green", material.name, "color3")
                index_button.connect("clicked", self.materialgcodescript, material.code)
                gridvariable.attach(index_button, i, repeat_three, 1, 1)
                
                if repeat_three == 2:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1

        for material in custom_materials:
        
            if selected_nozzle in material.compatible:
                index_button = self._gtk.Button("circle-blue", material.name, "color2")
                index_button.connect("clicked", self.nothing_at_all)
                gridvariable.attach(index_button, i, repeat_three, 1, 1)
                
                if repeat_three == 2:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1
                

        for material in materials:

            show_experimental = self._config.get_main_config().getboolean('show_experimental_material', False)
            allowed_for_experimental = ["ST025", "ST04", "ST08"]
            
            if selected_nozzle in material.experimental and selected_nozzle in allowed_for_experimental:
                index_button = self._gtk.Button("circle-orange", material.name, "color1")
                index_button.connect("clicked", self.confirm_print_experimental, material.code)
                if show_experimental:
                    gridvariable.attach(index_button, i, repeat_three, 1, 1)
                    if repeat_three == 2:
                        repeat_three = 0
                        i += 1
                    else:
                        repeat_three += 1

            if material.code == materials[-1].code:
                size: int = 1
                index: int = repeat_three
                while index != 2:
                    size += 1
                    index += 1
                index_button = self._gtk.Button("circle-red", _("Generic"), "color4")
                index_button.connect("clicked", self.confirm_print_generic)
                gridvariable.attach(index_button, i, repeat_three, 1, size)

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

    def confirm_print_custom(self, widget, code):
        params = {"script": f"LOAD_FILAMENT_{code}"}
        self._screen._confirm_send_action(
            None,
            self.texts[0] + "\n\n" + self.texts[1] + "\n\n",
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