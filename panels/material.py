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
        self.page: int = 1

        self.buttons = {}
        self.createbuttons()

        grid = self._gtk.HomogeneousGrid()

        self.gridattach(pagenumber=self.page, gridvariable=grid)

        self.labels['material_menu'] = self._gtk.HomogeneousGrid()
        self.labels['material_menu'].attach(grid, 0, 0, 1, 3)

        self.content.remove(self.labels['material_menu'])
        self.content.add(self.labels['material_menu'])

        self.storegrid = grid
        

    def materialgcodescript(self, widget, material: str):
        self._screen._ws.klippy.gcode_script(f"LOAD_FILAMENT_{material}")
        self._screen._menu_go_back()

    def changepage (self, widget):
        if (self.page == 1):
            self.page = 2
        else:
            self.page = 1
        self.update_grid()

    def createbuttons (self):

        self.buttons = {
            'PLA': self._gtk.Button(None, "PLA", "color1"),
            'NYLON': self._gtk.Button(None, "NYLON", "color1"),
            'PLATOUGH': self._gtk.Button(None, "TOUGH PLA", "color1"),
            'CPE': self._gtk.Button(None, "CPE", "color1"),
            'ABS': self._gtk.Button(None, "ABS", "color1"),
            'PP': self._gtk.Button(None, "PP", "color1"),
            'PLA': self._gtk.Button(None, "PLA", "color1"),
            'CPEPLUS': self._gtk.Button(None, "CPE+", "color1"),
            'PETG': self._gtk.Button(None, "PETG", "color1"),
            'PC': self._gtk.Button(None, "PC", "color1"),
            'TPU95A': self._gtk.Button(None, "TPU 95A", "color1"),
            'TPU64D': self._gtk.Button(None, "TPU 64D", "color1"),
            'PET': self._gtk.Button(None, "PET", "color1"),
            'PAHTCF15': self._gtk.Button(None, "PAHT CF15", "color1"),
            'PETCF15': self._gtk.Button(None, "PET CF15", "color1"),
            'PCGF30': self._gtk.Button(None, "PC GF30", "color1"),
            'PPGF30': self._gtk.Button(None, "PP GF30", "color1"),
            '316L': self._gtk.Button(None, "316 L", "color1"),
            '174PH': self._gtk.Button(None, "17-4PH", "color1"),
            'ASA': self._gtk.Button(None, "ASA", "color1"),
            'OTHER': self._gtk.Button(None, _("Auto"), "color3"),
            'PAGESWAP': self._gtk.Button("shuffle", None, "color4"),
        }
        self.buttons['PLA'].connect("clicked", self.materialgcodescript, "PLA")
        self.buttons['NYLON'].connect("clicked", self.materialgcodescript, "NYLON")
        self.buttons['PLATOUGH'].connect("clicked", self.materialgcodescript, "TOUGH_PLA")
        self.buttons['CPE'].connect("clicked", self.materialgcodescript, "CPE")
        self.buttons['ABS'].connect("clicked", self.materialgcodescript, "ABS")
        self.buttons['PP'].connect("clicked", self.materialgcodescript, "PP")
        self.buttons['CPEPLUS'].connect("clicked", self.materialgcodescript, "CPEPLUS")
        self.buttons['PETG'].connect("clicked", self.materialgcodescript, "PETG")
        self.buttons['PC'].connect("clicked", self.materialgcodescript, "PC")
        self.buttons['TPU95A'].connect("clicked", self.materialgcodescript, "TPU_95A")
        self.buttons['TPU64D'].connect("clicked", self.materialgcodescript, "TPU_64D")
        self.buttons['PET'].connect("clicked", self.materialgcodescript, "PET")
        self.buttons['PAHTCF15'].connect("clicked", self.materialgcodescript, "PAHT_CF15")
        self.buttons['PETCF15'].connect("clicked", self.materialgcodescript, "PET_CF15")
        self.buttons['PCGF30'].connect("clicked", self.materialgcodescript, "PC_GF30")
        self.buttons['PPGF30'].connect("clicked", self.materialgcodescript, "PP_GF30")
        self.buttons['316L'].connect("clicked", self.materialgcodescript, "316L")
        self.buttons['174PH'].connect("clicked", self.materialgcodescript, "17_4PH")
        self.buttons['ASA'].connect("clicked", self.materialgcodescript, "ASA")
        self.buttons['OTHER'].connect("clicked", self.materialgcodescript, "GENERIC")
        self.buttons['PAGESWAP'].connect("clicked", self.changepage)

    def gridattach(self, pagenumber: int, gridvariable):

        if (pagenumber == 1):

            gridvariable.attach(self.buttons['NYLON'], 0, 1, 1, 1) # 5
            gridvariable.attach(self.buttons['PLATOUGH'], 1, 0, 1, 1) # 2
            gridvariable.attach(self.buttons['CPE'], 1, 1, 1, 1) # 6
            gridvariable.attach(self.buttons['PLA'], 0, 0, 1, 1) # 1
            gridvariable.attach(self.buttons['TPU64D'], 0, 2, 1, 1) # 9
            gridvariable.attach(self.buttons['TPU95A'], 1, 2, 1, 1) # 10
            gridvariable.attach(self.buttons['PETCF15'], 0, 3, 1, 1) # 13
            gridvariable.attach(self.buttons['PCGF30'], 1, 3, 1, 1) # 14
            gridvariable.attach(self.buttons['174PH'], 0, 4, 1, 1) # 17
            gridvariable.attach(self.buttons['PC'], 1, 4, 1, 1) # 18
            gridvariable.attach(self.buttons['PAGESWAP'], 2, 0, 1, 5)

        if (pagenumber == 2):

            gridvariable.attach(self.buttons['CPEPLUS'], 2, 1, 1, 1) # 7
            gridvariable.attach(self.buttons['ABS'], 3, 0, 1, 1) # 4
            gridvariable.attach(self.buttons['PP'], 3, 1, 1, 1) # 8
            gridvariable.attach(self.buttons['PETG'], 2, 0, 1, 1) # 3
            gridvariable.attach(self.buttons['PET'], 2, 2, 1, 1) # 11
            gridvariable.attach(self.buttons['PAHTCF15'], 3, 2, 1, 1) # 12
            gridvariable.attach(self.buttons['PPGF30'], 2, 3, 1, 1) # 15
            gridvariable.attach(self.buttons['316L'], 3, 3, 1, 1) # 16
            gridvariable.attach(self.buttons['ASA'], 2, 4, 1, 1) # 19
            gridvariable.attach(self.buttons['OTHER'], 3, 4, 1, 1) # 20
            gridvariable.attach(self.buttons['PAGESWAP'], 0, 0, 1, 5)

    def update_grid(self):
        self.content.remove(self.labels['material_menu'])
        self.labels['material_menu'] = self._gtk.HomogeneousGrid()
        self.createbuttons()
        self.gridattach(pagenumber=self.page, gridvariable=self.labels['material_menu'])

        #self.labels['material_menu'].attach(self.storegrid, 0, 0, 1, 3) 
        self.content.add(self.labels['material_menu'])
        self.labels['material_menu'].show_all()


    