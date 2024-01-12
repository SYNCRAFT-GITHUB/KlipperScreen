import configparser
import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return JobMaterialChange(*args)

class JobMaterialChange(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['filament']

        macros = self._printer.get_gcode_macros()

        self.current_extruder = self.get_variable('currentextruder')
        self.nozzle = self.get_variable('nozzle')

        self.content.add(self._gtk.Label("\n\n"))

        self.buttons = {
            'material_change': self._gtk.Button("filament", _("Change material for non-active feeder"), "color1", 1, Gtk.PositionType.BOTTOM),
        }

        grid = self._gtk.HomogeneousGrid()

        self.buttons['material_change'].connect("clicked", self.set_material)

        self.ext_feeder = {
            'extruder_stepper extruder1': 'extruder1',
            'extruder': 'extruder'
        }

        extruder_index = 0
        position = 0
        for extruder in self._printer.get_tools():
            self.labels[extruder] = self._gtk.Button(f"extruder-{extruder_index+1}", None, None, .68, Gtk.PositionType.LEFT, 1)
            self.labels[extruder].get_style_context().add_class("filament_sensor")
            grid.attach(self.labels[extruder], position, 0, 2, 1)
            extruder_index += 1
            position += 3

        self.proextruders = {
            'Standard 0.25mm': 'nozzle-ST025',
            'Standard 0.4mm': 'nozzle-ST04',
            'Standard 0.8mm': 'nozzle-ST08',
            'Metal 0.4mm': 'nozzle-METAL04',
            'Fiber 0.6mm': 'nozzle-FIBER06',
        }

        position = 0
        for key, value in self.proextruders.items():
            self.labels[key] = self._gtk.Button(value, None, None)
            grid.attach(self.labels[key], position, 2, 1, 1)
            position += 1

        grid.attach(self.buttons['material_change'], 0, 3, 5, 2)

        self.content.add(grid)

    def reset_material_panel(self):
        panels = ["material_load", "material_set"]
        for panel in panels:
            try:
                del self._screen.panels[panel]
            except:
                pass

    def set_material(self, button):
        self.reset_material_panel()
        if "extruder1" in self.current_extruder:
            self._config.replace_extruder_option(newvalue="extruder")
        else:
            self._config.replace_extruder_option(newvalue="extruder1")
        self.menu_item_clicked(widget=button, panel="material_set", item={
            "name": _("Select the Material"),
            "panel": "material_set"
        })

    def get_variable(self, key) -> str:
        return self._config.variables_value_reveal(key)

    def process_update(self, action, data):
        if action == "notify_busy":
            return
        if action != "notify_status_update":
            return

        self.current_extruder = self.get_variable('currentextruder')
        self.nozzle = self.get_variable('nozzle')

        for extruder in self._printer.get_tools():
            if '1' in extruder:
                material = self.get_variable('material_ext1')
            else:
                material = self.get_variable('material_ext0')
            if 'empty' in material:
                material = _("Empty")
            self.labels[extruder].set_label(material)

        if self.get_variable('nozzle') not in self.proextruders:
            for key, value in self.proextruders.items():
                try:
                    self.labels[key].set_property("opacity", 0.3)
                    break
                except:
                    pass
        else:
            for key, value in self.proextruders.items():
                self.labels[key].set_property("opacity", 0.3)
            self.labels[self.nozzle].set_property("opacity", 1.0)

        for x, extruder in zip(self._printer.get_filament_sensors(), self._printer.get_tools()):
            if x in data:
                if 'enabled' in data[x]:
                    self._printer.set_dev_stat(x, "enabled", data[x]['enabled'])
                if 'filament_detected' in data[x]:
                    self._printer.set_dev_stat(x, "filament_detected", data[x]['filament_detected'])
                    if self._printer.get_stat(x, "enabled"):
                        if data[x]['filament_detected']:
                            self.labels[extruder].get_style_context().remove_class("filament_sensor_empty")
                            self.labels[extruder].get_style_context().add_class("filament_sensor_detected")
                        else:
                            self.labels[extruder].get_style_context().remove_class("filament_sensor_detected")
                            self.labels[extruder].get_style_context().add_class("filament_sensor_empty")
                logging.info(f"{x}: {self._printer.get_stat(x)}")