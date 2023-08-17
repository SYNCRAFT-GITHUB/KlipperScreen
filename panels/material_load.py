import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return ChMaterialPanel(*args)

class ChMaterialPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['material_menu']

        class PrinterMaterial:
            def __init__ (self, name: str, code: str, compatible: [str], experimental: [str]):
                self.name = name
                self.code = code
                self.compatible = compatible
                self.experimental = experimental

        self.materials = [
            PrinterMaterial(
                name="PLA", 
                code="PLA", 
                compatible=["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"], 
                experimental=["Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="NYLON",
                code="NYLON", 
                compatible=["Standard 0.4mm", "Standard 0.8mm"],
                experimental=["Standard 0.25mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="TO. PLA",
                code="TOUGH PLA", 
                compatible=["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"],
                experimental=["Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="CPE",
                code="CPE",
                compatible=["Standard 0.4mm", "Standard 0.8mm"], 
                experimental=["Standard 0.25mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="ABS", 
                code="ABS", 
                compatible=["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"], 
                experimental=["Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="PP", 
                code="PP", 
                compatible=["Standard 0.4mm"], 
                experimental=["Standard 0.25mm", "Standard 0.8mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="CPE +", 
                code="CPE+", 
                compatible=["Standard 0.4mm"], 
                experimental=["Standard 0.25mm", "Standard 0.8mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="PETG",
                code="PETG", 
                compatible=["Standard 0.4mm", "Standard 0.8mm"], 
                experimental=["Standard 0.25mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="PC", 
                code="PC",
                compatible=["Standard 0.4mm"], 
                experimental=["Standard 0.25mm", "Standard 0.8mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="TPU 95A",
                code="TPU 95A", 
                compatible=["Standard 0.4mm", "Standard 0.8mm"],
                experimental=["Standard 0.25mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="TPU D64", 
                code="TPU D64",
                compatible=["Standard 0.4mm", "Standard 0.8mm"], 
                experimental=["Standard 0.25mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="PET", 
                code="PET", 
                compatible=[],
                experimental=["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm", "Fiber 0.6mm", "Metal 0.4mm"]),
            PrinterMaterial(
                name="PAHT CF15", 
                code="PAHT CF15", 
                compatible=["Fiber 0.6mm"], 
                experimental=[]),
            PrinterMaterial(
                name="PET CF15", 
                code="PET CF15",
                compatible=["Fiber 0.6mm"], 
                experimental=[]),
            PrinterMaterial(
                name="PC GF30", 
                code="PC GF30", 
                compatible=["Fiber 0.6mm"], 
                experimental=[]),
            PrinterMaterial(
                name="PP GF30", 
                code="PP GF30", 
                compatible=["Fiber 0.6mm"],
                experimental=[]),
            PrinterMaterial(
                name="316 L", 
                code="316L", 
                compatible=["Metal 0.4mm"],
                experimental=[]),
            PrinterMaterial(
                name="17-4PH",
                code="17-4PH", 
                compatible=["Metal 0.4mm"],
                experimental=[]),
            PrinterMaterial(
                name="ASA",
                code="ASA",
                compatible=["Standard 0.4mm"], 
                experimental=[]),
        ]

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
        self._screen._ws.klippy.gcode_script(f"LOAD_FILAMENT MAT='{material}'")
        for _ in range(0,2):
            self._screen._menu_go_back()

    def gridattach(self, gridvariable):

        selected_nozzle: str = self._config.get_nozzle()
        repeat_three: int = 0
        i: int = 0

        for material in self.materials:

            if selected_nozzle in material.compatible:
                index_button = self._gtk.Button("circle-green", material.name, "color3")
                index_button.connect("clicked", self.materialgcodescript, material.code)
                gridvariable.attach(index_button, i, repeat_three, 1, 1)
                
                if repeat_three == 2:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1
                

        for material in self.materials:

            show_experimental = self._config.get_main_config().getboolean('show_experimental_material', False)
            allowed_for_experimental = ["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"]
            
            if selected_nozzle in material.experimental and self._config.get_nozzle() in allowed_for_experimental:
                index_button = self._gtk.Button("circle-orange", material.name, "color1")
                index_button.connect("clicked", self.confirm_print_experimental, material.code)
                if show_experimental:
                    gridvariable.attach(index_button, i, repeat_three, 1, 1)
                    if repeat_three == 2:
                        repeat_three = 0
                        i += 1
                    else:
                        repeat_three += 1

            if material.code == self.materials[-1].code:
                size: int = 1
                index: int = repeat_three
                while index != 2:
                    size += 1
                    index += 1
                index_button = self._gtk.Button("circle-red", _("Generic"), "color4")
                index_button.connect("clicked", self.confirm_print_generic)
                gridvariable.attach(index_button, i, repeat_three, 1, size)

    def confirm_print_experimental(self, widget, code):
        params = {"script": f"LOAD_FILAMENT MAT='{code}'"}
        self._screen._confirm_send_action(
            None,
            self.texts[0] + "\n\n" + self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        for _ in range(0,2):
            self._screen._menu_go_back()
        

    def confirm_print_generic(self, widget):
        params = {"script": "LOAD_FILAMENT"}
        self._screen._confirm_send_action(
            None,
            self.texts[2] + "\n\n",
            "printer.gcode.script",
            params
        )
        for _ in range(0,2):
                self._screen._menu_go_back()