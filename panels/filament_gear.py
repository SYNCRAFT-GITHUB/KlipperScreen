import logging
import re
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return FilamentGear(*args)


class FilamentGear(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.current_extruder = self._config.variables_value_reveal('currentextruder')
        macros = self._printer.get_gcode_macros()
        self.load_filament = any("LOAD_FILAMENT" in macro.upper() for macro in macros)
        self.unload_filament = any("UNLOAD_FILAMENT" in macro.upper() for macro in macros)

        self.speeds = ['1', '2', '5', '25']
        self.distances = ['5', '10', '15', '25']
        if self.ks_printer_cfg is not None:
            dis = self.ks_printer_cfg.get("extrude_distances", '5, 10, 15, 25')
            if re.match(r'^[0-9,\s]+$', dis):
                dis = [str(i.strip()) for i in dis.split(',')]
                if 1 < len(dis) < 5:
                    self.distances = dis
            vel = self.ks_printer_cfg.get("extrude_speeds", '1, 2, 5, 25')
            if re.match(r'^[0-9,\s]+$', vel):
                vel = [str(i.strip()) for i in vel.split(',')]
                if 1 < len(vel) < 5:
                    self.speeds = vel

        self.distance = int(self.distances[1])
        self.speed = int(self.speeds[1])
        self.buttons = {
            'extrude': self._gtk.Button("extrude", _("Extrude"), "color4"),
            'retract': self._gtk.Button("retract", _("Retract"), "color1"),
            'temperature': self._gtk.Button("heat-up", _("Temperature"), "color4"),
        }
        self.buttons['extrude'].connect("clicked", self.extrude, "+")
        self.buttons['retract'].connect("clicked", self.extrude, "-")
        self.buttons['temperature'].connect("clicked", self.menu_item_clicked, "temperature", {
            "name": _("Temperature"),
            "panel": "temperature"
        })

        extgrid = self._gtk.HomogeneousGrid()
        limit = 5

        distgrid = Gtk.Grid()
        for j, i in enumerate(self.distances):
            self._screen.lang_ltr = True
            self.labels[f"dist{i}"] = self._gtk.Button(label=i)
            self.labels[f"dist{i}"].connect("clicked", self.change_distance, int(i))
            ctx = self.labels[f"dist{i}"].get_style_context()
            if ((self._screen.lang_ltr is True and j == 0) or
                    (self._screen.lang_ltr is False and j == len(self.distances) - 1)):
                ctx.add_class("distbutton_top")
            elif ((self._screen.lang_ltr is False and j == 0) or
                  (self._screen.lang_ltr is True and j == len(self.distances) - 1)):
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if int(i) == self.distance:
                ctx.add_class("distbutton_active")
            distgrid.attach(self.labels[f"dist{i}"], j, 0, 1, 1)

        speedgrid = Gtk.Grid()
        for j, i in enumerate(self.speeds):
            self.labels[f"speed{i}"] = self._gtk.Button(label=i)
            self.labels[f"speed{i}"].connect("clicked", self.change_speed, int(i))
            ctx = self.labels[f"speed{i}"].get_style_context()
            if ((self._screen.lang_ltr is True and j == 0) or
                    (self._screen.lang_ltr is False and j == len(self.speeds) - 1)):
                ctx.add_class("distbutton_top")
            elif ((self._screen.lang_ltr is False and j == 0) or
                  (self._screen.lang_ltr is True and j == len(self.speeds) - 1)):
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if int(i) == self.speed:
                ctx.add_class("distbutton_active")
            speedgrid.attach(self.labels[f"speed{i}"], j, 0, 1, 1)

        distbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.labels['extrude_dist'] = Gtk.Label(_("Distance (mm)"))
        distbox.pack_start(self.labels['extrude_dist'], True, True, 0)
        distbox.add(distgrid)
        speedbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.labels['extrude_speed'] = Gtk.Label(_("Speed (mm/s)"))
        speedbox.pack_start(self.labels['extrude_speed'], True, True, 0)
        speedbox.add(speedgrid)

        filament_sensors = self._printer.get_filament_sensors()
        sensors = Gtk.Grid()
        sensors.set_size_request(self._gtk.content_width - 30, -1)
        if len(filament_sensors) > 0:
            sensors.set_column_spacing(5)
            sensors.set_row_spacing(5)
            sensors.set_halign(Gtk.Align.CENTER)
            sensors.set_valign(Gtk.Align.CENTER)
            for s, x in enumerate(filament_sensors):
                if s > limit:
                    break
                name = x[23:].strip()
                public_name = name.replace('_', ' ').replace('spool', _('Spool')).replace('one', _("One")).replace('two', _("Two"))
                self.labels[x] = {
                    'label': Gtk.Label(public_name),
                    'public': str(public_name),
                    'switch': Gtk.Switch(),
                    'box': Gtk.Box()
                }
                self.labels[x]['label'].set_halign(Gtk.Align.CENTER)
                self.labels[x]['label'].set_hexpand(True)
                self.labels[x]['label'].set_ellipsize(Pango.EllipsizeMode.END)
                self.labels[x]['switch'].set_property("width-request", round(self._gtk.font_size * 2))
                self.labels[x]['switch'].set_property("height-request", round(self._gtk.font_size))
                self.labels[x]['switch'].connect("notify::active", self.enable_disable_fs, name, x)
                self.labels[x]['box'].pack_start(self.labels[x]['label'], True, True, 5)
                self.labels[x]['box'].pack_start(self.labels[x]['switch'], False, False, 5)
                self.labels[x]['box'].get_style_context().add_class("filament_sensor")
                self.labels[x]['box'].set_hexpand(True)
                sensors.attach(self.labels[x]['box'], s, 0, 1, 1)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.attach(extgrid, 0, 0, 4, 1)

        grid.attach(self.buttons['extrude'], 0, 1, 2, 1)
        grid.attach(self.buttons['retract'], 2, 1, 2, 1)
        grid.attach(self.buttons['temperature'], 0, 0, 4, 1)
        grid.attach(distbox, 0, 3, 2, 1)
        grid.attach(speedbox, 2, 3, 2, 1)
        grid.attach(sensors, 0, 4, 4, 1)

        self.content.add(grid)

    def process_busy(self, busy):
        for button in self.buttons:
            if button == "temperature":
                continue
            self.buttons[button].set_sensitive((not busy))

    def process_update(self, action, data):
        if action == "notify_busy":
            self.process_busy(data)
            return
        if action != "notify_status_update":
            return
        for x in self._printer.get_tools():
            self.update_temp(
                x,
                self._printer.get_dev_stat(x, "nothing"), # It should be "temperature"
                self._printer.get_dev_stat(x, "target"),
                self._printer.get_dev_stat(x, "power"),
                lines=2,
            )

        self.current_extruder = self._config.variables_value_reveal('currentextruder')

        for x in self._printer.get_filament_sensors():
            if x in data:
                if 'enabled' in data[x]:
                    self._printer.set_dev_stat(x, "enabled", data[x]['enabled'])
                    self.labels[x]['switch'].set_active(data[x]['enabled'])
                if 'filament_detected' in data[x]:
                    self._printer.set_dev_stat(x, "filament_detected", data[x]['filament_detected'])
                    if self._printer.get_stat(x, "enabled"):
                        if data[x]['filament_detected']:
                            self.labels[x]['box'].get_style_context().remove_class("filament_sensor_empty")
                            self.labels[x]['box'].get_style_context().add_class("filament_sensor_detected")
                        else:
                            self.labels[x]['box'].get_style_context().remove_class("filament_sensor_detected")
                            self.labels[x]['box'].get_style_context().add_class("filament_sensor_empty")
                logging.info(f"{x}: {self._printer.get_stat(x)}")

    def change_distance(self, widget, distance):
        logging.info(f"### Distance {distance}")
        self.labels[f"dist{self.distance}"].get_style_context().remove_class("distbutton_active")
        self.labels[f"dist{distance}"].get_style_context().add_class("distbutton_active")
        self.distance = distance

    def change_speed(self, widget, speed):
        logging.info(f"### Speed {speed}")
        self.labels[f"speed{self.speed}"].get_style_context().remove_class("distbutton_active")
        self.labels[f"speed{speed}"].get_style_context().add_class("distbutton_active")
        self.speed = speed

    def extrude(self, widget, direction):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.EXTRUDE_REL)
        self._screen._ws.klippy.gcode_script(KlippyGcodes.extrude(f"{direction}{self.distance}", f"{self.speed * 60}"))

    def enable_disable_fs(self, switch, gparams, name, x):
        if switch.get_active():
            self._printer.set_dev_stat(x, "enabled", True)
            self._screen._ws.klippy.gcode_script(f"SET_FILAMENT_SENSOR SENSOR={name} ENABLE=1")
            if self._printer.get_stat(x, "filament_detected"):
                self.labels[x]['box'].get_style_context().add_class("filament_sensor_detected")
            else:
                self.labels[x]['box'].get_style_context().add_class("filament_sensor_empty")
        else:
            self._printer.set_dev_stat(x, "enabled", False)
            self._screen._ws.klippy.gcode_script(f"SET_FILAMENT_SENSOR SENSOR={name} ENABLE=0")
            self.labels[x]['box'].get_style_context().remove_class("filament_sensor_empty")
            self.labels[x]['box'].get_style_context().remove_class("filament_sensor_detected")