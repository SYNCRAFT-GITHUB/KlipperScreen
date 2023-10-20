import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel

class PrinterMaterial:
    def __init__ (self, name: str, code: str, compatible: [str] = [], experimental: [str] = [], custom: [str] = []):
        self.name = name
        self.code = code
        self.compatible = compatible
        self.experimental = experimental
        self.custom = custom

materials = [
    PrinterMaterial(
        name="PLA", 
        code="PLA", 
        compatible=["ST025", "ST04", "ST08"], 
        experimental=["FIBER06", "METAL04"]),
    PrinterMaterial(
        name="NYLON",
        code="NYLON", 
        compatible=["ST04", "ST08"],
        experimental=["ST025", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="TO. PLA",
        code="TOUGH_PLA", 
        compatible=["ST025", "ST04", "ST08"],
        experimental=["FIBER06", "METAL04"]),
    PrinterMaterial(
        name="CPE",
        code="CPE",
        compatible=["ST04", "ST08"], 
        experimental=["ST025", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="ABS", 
        code="ABS", 
        compatible=["ST025", "ST04", "ST08"], 
        experimental=["FIBER06", "METAL04"]),
    PrinterMaterial(
        name="PP", 
        code="PP", 
        compatible=["ST04"], 
        experimental=["ST025", "ST08", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="CPE +", 
        code="CPEPLUS", 
        compatible=["ST04"], 
        experimental=["ST025", "ST08", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="PETG",
        code="PETG", 
        compatible=["ST04", "ST08"], 
        experimental=["ST025", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="PC", 
        code="PC",
        compatible=["ST04"], 
        experimental=["ST025", "ST08", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="TPU 95A",
        code="TPU_A95", 
        compatible=["ST04", "ST08"],
        experimental=["ST025", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="TPU D64", 
        code="TPU_D64",
        compatible=["ST04", "ST08"], 
        experimental=["ST025", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="PET", 
        code="PET", 
        compatible=[],
        experimental=["ST025", "ST04", "ST08", "FIBER06", "METAL04"]),
    PrinterMaterial(
        name="PAHT CF15", 
        code="PAHT_CF15", 
        compatible=["FIBER06"], 
        experimental=[]),
    PrinterMaterial(
        name="PET CF15", 
        code="PET_CF15",
        compatible=["FIBER06"], 
        experimental=[]),
    PrinterMaterial(
        name="PC GF30", 
        code="PC_GF30", 
        compatible=["FIBER06"], 
        experimental=[]),
    PrinterMaterial(
        name="PP GF30", 
        code="PP_GF30", 
        compatible=["FIBER06"],
        experimental=[]),
    PrinterMaterial(
        name="316 L", 
        code="L316", 
        compatible=["METAL04"],
        experimental=[]),
    PrinterMaterial(
        name="17-4PH",
        code="PH_174", 
        compatible=["METAL04"],
        experimental=[]),
    PrinterMaterial(
        name="ASA",
        code="ASA",
        compatible=["ST04"], 
        experimental=[]),
]

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

        for material in materials:

            if selected_nozzle in material.custom:
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