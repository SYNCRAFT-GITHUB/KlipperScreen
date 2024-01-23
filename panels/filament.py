import configparser
import logging
import random
import time
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return FilamentPanel(*args)

class FilamentPanel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['filament']

        macros = self._printer.get_gcode_macros()
        self.load_filament = any("LOAD_FILAMENT" in macro.upper() for macro in macros)
        self.unload_filament = any("UNLOAD_FILAMENT" in macro.upper() for macro in macros)

        self.speed: int = 2

        self.current_extruder = self.get_variable('currentextruder')
        self.nozzle = self.get_variable('nozzle')

        self.buttons = {
            'load': self._gtk.Button("arrow-up", _("Load"), "color3", Gtk.PositionType.BOTTOM, 3),
            'unload': self._gtk.Button("arrow-down", _("Unload"), "color2", Gtk.PositionType.BOTTOM, 3),
            'material_ext0': self._gtk.Button("filament", None, "color1", .68),
            'material_ext1': self._gtk.Button("filament", None, "color1", .68),
        }

        grid = self._gtk.HomogeneousGrid()
        grid.attach(self.buttons['load'], 0, 0, 3, 3)
        grid.attach(self.buttons['unload'], 3, 0, 3, 3)
        grid.attach(self.buttons['material_ext0'], 0, 3, 1, 1)
        grid.attach(self.buttons['material_ext1'], 5, 3, 1, 1)

        self.buttons['unload'].connect("clicked", self.load_unload, "-")
        self.buttons['load'].connect("clicked", self.load_material)
        self.buttons['material_ext0'].connect("clicked", self.select_material, 'extruder')
        self.buttons['material_ext1'].connect("clicked", self.select_material, 'extruder1')

        self.ext_feeder = {
            'extruder_stepper extruder1': 'extruder1',
            'extruder': 'extruder'
        }

        i = 1
        for extruder in self._printer.get_tools():
            self.labels[extruder] = self._gtk.Button(f"extruder-{i}", None, None, .68, Gtk.PositionType.LEFT, 1)
            self.labels[extruder].connect("clicked", self.change_extruder, extruder)
            self.labels[extruder].get_style_context().add_class("filament_sensor")
            if self.ext_feeder[extruder] != self.current_extruder:
                self.labels[extruder].set_property("opacity", 0.3)
            grid.attach(self.labels[extruder], (i+(i/2)), 3, 2, 1)
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

        self.labels['settings'].connect("clicked", self.menu_item_clicked, "filament_gear", {
            "name": _("Filament"),
            "panel": "filament_gear"
        })

        self.content.add(grid)

    def replace_extruder_option(self, newvalue):
        self._config.replace_extruder_option(newvalue=newvalue)

    def load_unload(self, widget, direction):
        if direction == "-":
            if not self.unload_filament:
                self._screen.show_popup_message("Macro UNLOAD_FILAMENT not found")
            else:
                self._screen._ws.klippy.gcode_script(f"UNLOAD_FILAMENT SPEED={self.speed * 60}")
        if direction == "+":
            if not self.load_filament:
                self._screen.show_popup_message("Macro LOAD_FILAMENT not found")
            else:
                self._screen._ws.klippy.gcode_script(f"LOAD_FILAMENT SPEED={self.speed * 60}")

    def get_variable(self, key) -> str:
        return self._config.variables_value_reveal(key)

    def process_busy(self, busy):
        for button in self.buttons:
            self.buttons[button].set_sensitive((not busy))
        try:
            for key, value in self.proextruders.items():
                self.labels[key].set_sensitive((not busy))
            for extruder in self._printer.get_tools():
                self.labels[extruder].set_sensitive((not busy))
        except:
            pass

    def process_update(self, action, data):
        if action == "notify_busy":
            self.process_busy(data)
            return
        if action != "notify_status_update":
            return
    
        self.current_extruder = self.get_variable('currentextruder')

        for extruder in self._printer.get_tools():
            if '1' in extruder:
                material = self.get_variable('material_ext1')
            else:
                material = self.get_variable('material_ext0')
            if 'empty' in material.lower():
                material = _("Empty")
            if 'generic' in material.lower():
                material = _("Generic")
            self.labels[extruder].set_label(material)
            if self.ext_feeder[extruder] != self.current_extruder:
                self.labels[extruder].set_property("opacity", 0.3)
            else:
                self.labels[extruder].set_property("opacity", 1.0)

        if self.get_variable('nozzle') not in self.proextruders:
            for key, value in self.proextruders.items():
                try:
                    self.labels[key].get_style_context().remove_class("button_active")
                    break
                except:
                    pass
        else:
            self.labels[self.nozzle].get_style_context().remove_class("button_active")
            self.nozzle = self.get_variable('nozzle')
            self.labels[self.nozzle].get_style_context().add_class("button_active")

        for x, extruder in zip(self._printer.get_filament_sensors(), self._printer.get_tools()):
            if self._config.detected_in_filament_activity() and ((time.time() - self.start_time) > 1.0):
                self._config.replace_filament_activity(None, "busy", replace="detected")
                if self._config.get_main_config().getboolean('auto_select_material', False):
                    self._screen.delete_temporary_panels()
                    self.start_time = time.time()
                    self.menu_item_clicked(widget="material_popup", panel="material_popup", item={
                                        "name": _("Select the Material"),
                                        "panel": "material_popup"
                                    })
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
                            self._config.replace_filament_activity(x, "empty")

                        if self._config.get_filament_activity(x) == "empty" and data[x]['filament_detected']:
                            self.start_time = time.time()
                            self._config.replace_filament_activity(x, "detected")
                            self._config.replace_spool_option(x)
                            if 'two' in str(x):
                                self._config.replace_extruder_option(newvalue='extruder1')
                            else:
                                self._config.replace_extruder_option(newvalue='extruder')
                    logging.info(f"{x}: {self._printer.get_stat(x)}")

    def change_extruder(self, widget, extruder):
        logging.info(f"Changing extruder to {extruder}")
        self._screen._ws.klippy.gcode_script(f"T{self._printer.get_tool_number(extruder)}")

    def nozzlegcodescript(self, widget, nozzle: str):
        self._config.replace_nozzle(newvalue=nozzle)
        self._screen._ws.klippy.gcode_script(f"NOZZLE_SET NZ='{nozzle}'")

    def load_material(self, widget):
        self._screen.delete_temporary_panels()
        self.nozzle = self.get_variable('nozzle')

        if self.nozzle not in self.proextruders:
            print(f"self nozzle: {self.nozzle}")
            message: str = _("Select Syncraft ProExtruder")
            self._screen.show_popup_message(message, level=2)
        else:
            self.menu_item_clicked(widget=widget, panel="material_load", item={
                "name": _("Select the Material"),
                "panel": "material_load"
            })

    def select_material(self, widget, extruder: str):
        self._screen.delete_temporary_panels()
        self.replace_extruder_option(newvalue=extruder)
        self.nozzle = self.get_variable('nozzle')

        if self.nozzle not in self.proextruders:
            message: str = _("Select Syncraft ProExtruder")
            self._screen.show_popup_message(message, level=2)
        else:
            self.menu_item_clicked(widget=widget, panel="material_set", item={
                "name": _("Select the Material"),
                "panel": "material_set"
            })
