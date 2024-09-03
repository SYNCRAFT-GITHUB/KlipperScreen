import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from ks_includes.screen_panel import ScreenPanel

def create_panel(*args):
    return V3PasswordPanel(*args)

class V3PasswordPanel(ScreenPanel):
    # FIXME: Not using _() translation strings
    def __init__(self, screen, title):
        super().__init__(screen, title)

        self._screen.show_popup_message(
            """
            Apenas atualize se sua máquina for compatível,
            caso contrário pode gerar riscos de segurança
            """,
            level=3 # message_popup_warning
        )

        pl = self._gtk.Label("Digite a senha para atualizar para V3.")
        pl.set_hexpand(False)
        self.labels['password'] = Gtk.Entry()
        self.labels['password'].set_visibility(False) # Hide pasword
        self.labels['password'].set_text('')
        self.labels['password'].set_hexpand(True)
        self.labels['password'].connect("activate", self.check_password)
        self.labels['password'].connect("focus-in-event", self._screen.show_keyboard)

        submit = self._gtk.Button(None, "Enviar", "color3")
        submit.set_hexpand(False)
        submit.connect("clicked", self.check_password)

        box = Gtk.Box()
        box.pack_start(self.labels['password'], True, True, 5)
        box.pack_start(submit, False, False, 5)

        self.labels['insert_password'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.labels['insert_password'].set_valign(Gtk.Align.CENTER)
        self.labels['insert_password'].pack_start(pl, True, True, 5)
        self.labels['insert_password'].pack_start(box, True, True, 5)

        self.content.add(self.labels['insert_password'])

        self.labels['password'].grab_focus_without_selecting()

    def check_password(self, widget):
        password = self.labels['password'].get_text()

        # It is insecure because user (you) was warned, dont do it!
        available_passwords = ['maker265.v3']

        if password in available_passwords:
            self._config.replace_fix_option(newvalue="FILES_V3")
            # Show panel and delete current
            self._screen.show_panel("fix_steps", "fix_steps", "Fix steps", 1, False)
            self._screen.remove_keyboard()
            return

        self._screen.show_popup_message(
            "Senha incorreta",
            level=3 # message_popup_error
        )