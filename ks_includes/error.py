import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class KnownError(Gtk.Window):
    def __init__(self, error: str, message: str, code: str):
        self.error = error
        self.message = message
        self.code = code

known_errors = [
    KnownError(
        error= '!PROEXTRUDER_DOESNT_MATCH_GCODE',
        message= 'The inserted Extruder is incompatible with this File',
        code="88E"
        ),
    KnownError(
        error= '!MATERIAL_DOESNT_MATCH_GCODE',
        message= 'The material you\'re using is not compatible with this file',
        code=None
        ),
    KnownError(
        error= '!SOME_MATERIAL_DOESNT_MATCH_GCODE',
        message= 'One of the materials you\'re using is not compatible with this file',
        code=None
        ),
    KnownError(
        error= '!PRINTER_MODEL_MISMATCH',
        message= 'The file you are trying to print is for a different printer model',
        code=None
        ),
    KnownError(
        error= 'Probe triggered prior to movement',
        message= 'PROBE TRIGGERED PRIOR TO MOVEMENT',
        code=None
        ),
    KnownError(
        error= 'Already in a manual Z probe. Use ABORT to abort it.',
        message= 'ALREADY IN A MANUAL Z PROBE. USE ABORT TO ABORT IT',
        code=None
        ),
    KnownError(
        error= 'Endstop x still triggered after retract',
        message= 'ENDSTOP X STILL TRIGGERED AFTER RETRACT',
        code=None
        ),
    KnownError(
        error= 'No trigger on probe after full movement',
        message= 'NO TRIGGER ON PROBE AFTER FULL MOVEMENT',
        code=None
        ),
    KnownError(
        error= 'Probe samples exceed samples_tolerance',
        message= 'PROBE SAMPLES EXCEED SAMPLES_TOLERANCE',
        code=None
        ),
]