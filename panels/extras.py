import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return OutputPinPanel(*args)


class OutputPinPanel(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.devices = {}
        # Create a grid for all devices
        self.labels['devices'] = Gtk.Grid()
        self.labels['devices'].set_valign(Gtk.Align.CENTER)

        self.load_pins()

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.add(self.labels['devices'])

        self.add_button_new(f'{_("Hot Unload")} (°C)', 'hot', 'color1', 'gcode')

        self.content.add(self.scroll)

    def add_button(self, title, icon, color, gcode):

        grid = Gtk.Grid()
        button = self._gtk.Button(icon, title, color)
        button.connect("clicked", self._screen._ws.klippy.gcode_script, gcode)
        grid.attach(button, 0, 0, 1, 1)
        self.scroll.add(grid)

    def load_pins(self):
        output_pins = self._printer.get_output_pins()
        for pin in output_pins:
            # Support for hiding devices by name
            name = pin.split()[1]
            if name.startswith("_"):
                continue
            self.add_pin(pin)

    def perform_hot_unload(self, button):
        if self._printer.get_stat("print_stats")['state'] == "printing":
            message: str = _("You cannot perform this action while printing")
            self._screen.show_popup_message(message, level=2)
            return None
        self._screen._ws.klippy.gcode_script(f'HOT_UNLOAD_FILAMENT T={self.devices[_("Hot Unload")]["scale"].get_value()}')

    def add_button_new(self, title, icon, color, gcode):

        name = Gtk.Label()
        name.set_markup(f'\n<big><b>{title}</b></big>\n') 
        name.set_hexpand(True)
        name.set_vexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_valign(Gtk.Align.CENTER)
        name.set_line_wrap(True)
        name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        scale = Gtk.Button(icon, None, color)
        scale.set_hexpand(True)
        scale.get_style_context().add_class("fan_slider")

        scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=100, max=300, step=1)
        scale.set_value(200)
        scale.set_digits(0)
        scale.set_hexpand(True)
        scale.set_has_origin(True)
        scale.get_style_context().add_class("fan_slider")

        act_btn = self._gtk.Button(icon, None, "color1", 1)
        act_btn.set_hexpand(False)
        act_btn.connect("clicked", self.perform_hot_unload)

        pin_col = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        pin_col.add(act_btn)
        pin_col.add(scale)

        pin_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pin_row.add(name)
        pin_row.add(pin_col)

        self.devices[title] = {
            "row": pin_row,
            "scale": scale,
        }

        devices = sorted(self.devices)
        pos = 2

        self.labels['devices'].insert_row(pos)
        self.labels['devices'].attach(self.devices[title]['row'], 0, pos, 1, 1)
        self.labels['devices'].show_all()

    def add_pin(self, pin):

        pin_name: str = 'Title'
        if 'case_light' in pin:
            pin_name = _("Internal Lights")

        logging.info(f"Adding pin: {pin}")
        name = Gtk.Label()
        name.set_markup(f'\n<big><b>{pin_name}</b></big>\n') 
        name.set_hexpand(True)
        name.set_vexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_valign(Gtk.Align.CENTER)
        name.set_line_wrap(True)
        name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        scale.set_value(self.check_pin_value(pin))
        scale.set_digits(0)
        scale.set_hexpand(True)
        scale.set_has_origin(True)
        scale.get_style_context().add_class("fan_slider")
        scale.connect("button-release-event", self.set_output_pin, pin)

        min_btn = self._gtk.Button("back-fill", None, "color1", 1)
        min_btn.set_hexpand(False)
        min_btn.connect("clicked", self.update_pin_value, pin, 0)

        pin_col = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        pin_col.add(min_btn)
        pin_col.add(scale)

        pin_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pin_row.add(name)
        pin_row.add(pin_col)

        self.devices[pin] = {
            "row": pin_row,
            "scale": scale,
        }

        devices = sorted(self.devices)
        pos = devices.index(pin)

        self.labels['devices'].insert_row(pos)
        self.labels['devices'].attach(self.devices[pin]['row'], 0, pos, 1, 1)
        self.labels['devices'].show_all()

    def set_output_pin(self, widget, event, pin):
        self._screen._ws.klippy.gcode_script(f'SET_PIN PIN={" ".join(pin.split(" ")[1:])} '
                                             f'VALUE={self.devices[pin]["scale"].get_value() / 100}')
        # Check the speed in case it wasn't applied
        GLib.timeout_add_seconds(1, self.check_pin_value, pin)

    def check_pin_value(self, pin):
        self.update_pin_value(None, pin, self._printer.get_pin_value(pin))
        return False

    def process_update(self, action, data):
        if action != "notify_status_update":
            return

        for pin in self.devices:
            if pin in data and "value" in data[pin]:
                self.update_pin_value(None, pin, data[pin]["value"])

    def update_pin_value(self, widget, pin, value):
        if pin not in self.devices:
            return

        self.devices[pin]['scale'].disconnect_by_func(self.set_output_pin)
        self.devices[pin]['scale'].set_value(round(float(value) * 100))
        self.devices[pin]['scale'].connect("button-release-event", self.set_output_pin, pin)

        if widget is not None:
            self.set_output_pin(None, None, pin)