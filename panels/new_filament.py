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
    return NewFilament(*args)

class NewFilament(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['filament']

        self.current_extruder = self._printer.get_stat("toolhead", "extruder")
        filament_sensors_list = self._printer.get_filament_sensors()
        self.nozzle = self.get_variable('nozzle')

        self.buttons = {
            'load': self._gtk.Button("arrow-up", _("Load"), "color3", Gtk.PositionType.BOTTOM, 3),
            'unload': self._gtk.Button("arrow-down", _("Unload"), "color2", Gtk.PositionType.BOTTOM, 3),
            'extrude': self._gtk.Button("extrude", None, "color1", .62),
            'retract': self._gtk.Button("retract", None, "color1", .62),
            'material_ext0': self._gtk.Button("filament", None, "color2", .62),
            'material_ext1': self._gtk.Button("filament", None, "color2", .62),
        }

        grid = self._gtk.HomogeneousGrid()
        # COLUNA, LINHA, ESPAÇO COLUNA, ESPAÇO LINHA
        grid.attach(self.buttons['load'], 0, 0, 3, 2)
        grid.attach(self.buttons['unload'], 3, 0, 3, 2)
        grid.attach(self.buttons['material_ext0'], 0, 2, 1, 1)
        grid.attach(self.buttons['extrude'], 1, 2, 2, 1)
        grid.attach(self.buttons['retract'], 3, 2, 2, 1)
        grid.attach(self.buttons['material_ext1'], 5, 2, 1, 1)

        i = 0
        for extruder in self._printer.get_tools():
            self.labels[extruder] = self._gtk.Button(f"extruder-{i+1}", None, None, .50, Gtk.PositionType.LEFT, 1)
            self.labels[extruder].connect("clicked", self.change_extruder, extruder)
            self.labels[extruder].get_style_context().add_class("filament_sensor") # here
            if extruder != self.current_extruder:
                self.labels[extruder].set_property("opacity", 0.3)
            if i == 0:
                grid.attach(self.labels[extruder], i, 3, 3, 1)
            else:
                grid.attach(self.labels[extruder], 3, 3, 3, 1)
            i += 1

        self.proextruders = {
            'Standard 0.25mm': 'nozzle-ST025',
            'Standard 0.4mm': 'nozzle-ST04',
            'Standard 0.8mm': 'nozzle-ST08',
            'Metal 0.4mm': 'nozzle-METAL04',
            'Fiber 0.6mm': 'nozzle-FIBER06',
        }

        i: int = 0
        for key, value in self.proextruders.items():
            self.labels[key] = self._gtk.Button(value, None, None)
            self.labels[key].connect("clicked", self.nozzlegcodescript, key)
            grid.attach(self.labels[key], i, 4, 1, 1)
            i += 1

        self.labels['settings'] = self._gtk.Button("settings", None, None)
        grid.attach(self.labels['settings'], i, 4, 1, 1)






        self.content.add(grid)

    def get_variable(self, key) -> str:
        return self._config.variables_value_reveal(key)[1:-1]

    def process_update(self, action, data):
        if action == "notify_busy":
            self.process_busy(data)
            return
        if action != "notify_status_update":
            return

        self.labels[self.current_extruder].set_property("opacity", 1.0)
        self.current_extruder = self._printer.get_stat("toolhead", "extruder")

        for extruder in self._printer.get_tools():
            if '1' in extruder:
                material = self.get_variable('material_ext1')
            else:
                material = self.get_variable('material_ext0')
            if 'empty' in material:
                material = _("Empty")
            self.labels[extruder].set_label(f"{material}")
            if extruder != self.current_extruder:
                self.labels[extruder].set_property("opacity", 0.3)

        if self.get_variable('nozzle') not in self.proextruders:
            pass
        else:
            self.labels[self.nozzle].get_style_context().remove_class("button_active")
            self.nozzle = self.get_variable('nozzle')
            self.labels[self.nozzle].get_style_context().add_class("button_active")

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








    def change_extruder(self, widget, extruder):
        logging.info(f"Changing extruder to {extruder}")
        self._screen._ws.klippy.gcode_script(f"T{self._printer.get_tool_number(extruder)}")

        


    def nozzlegcodescript(self, widget, nozzle: str):
        self._config.replace_nozzle(newvalue=nozzle)
        self._screen._ws.klippy.gcode_script(f"NOZZLE_SET NZ='{nozzle}'")
        #self.labels[nozzle].get_style_context().add_class("button_active")