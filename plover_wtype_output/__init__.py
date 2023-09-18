import subprocess
from plover.oslayer.keyboardcontrol import KeyboardEmulation as OldKeyboardEmulation
from plover import log
try:
    from plover.key_combo import parse_key_combo
except ImportError:
    log.warning('with KeyCombo new interface')
    from plover.key_combo import KeyCombo
    _key_combo = KeyCombo()
    def parse_key_combo(combo_string: str):
        return _key_combo.parse(combo_string)

have_output_plugin = False
try:
    from plover.oslayer import KeyboardEmulationBase
    have_output_plugin = True
except ImportError:
    pass
class Main:
    def __init__(self, engine):
        self._engine = engine
        self._old_keyboard_emulation=None
    def start(self):
        if hasattr(self._engine, "_output"):
            pass
        else:
            if False: # stfu
                log.warning("Output plugin not properly supported!")
            assert self._old_keyboard_emulation is None
            self._old_keyboard_emulation = self._engine._keyboard_emulation
            assert isinstance(self._old_keyboard_emulation, OldKeyboardEmulation)
            self._engine._keyboard_emulation = KeyboardEmulation()
    def stop(self):
        if hasattr(self._engine, "_output"):
            log.warning("stop (while Plover has not quited) not supported -- uninstall the plugin instead")
        else:
            assert self._old_keyboard_emulation is not None
            self._engine._keyboard_emulation = self._old_keyboard_emulation
            self._old_keyboard_emulation = None

def wtype(*args):
    subprocess.run(["wtype"] + list(args))

def wtype_string(s):
    wtype("--", s)

mods = {
    'alt_l': 'alt', 'alt_r': 'alt',
    'control_l': 'ctrl', 'control_r': 'ctrl',
    'shift_l': 'shift', 'shift_r': 'shift',
    'super_l': 'logo', 'super_r': 'logo',
}

def key_event_to_wtype_arg(ev):
    (name, pressed) = ev
    mod = False
    if name in mods:
        name = mods[name]
        mod = True
    flag = 'm' if mod else 'p'
    if pressed:
        flag = flag.upper()
    return ('-' + flag,  name)

class KeyboardEmulation(*([KeyboardEmulationBase] if have_output_plugin else [])):
    """Emulate keyboard events."""

    @classmethod
    def get_option_info(cls):
        return {}

    def __init__(self, params = None):
        if have_output_plugin:
            KeyboardEmulationBase.__init__(self, params)
        self._ms = None

    def start(self):
        start()

    def cancel(self):
        pass

    def set_ms(self, ms):
        if self._ms != ms:
            self._ms = ms

    def _wtype_string(self, s):
        ms = self._ms
        wtype("--", *(["-d", ms] if ms != None else []), s)

    def send_string(self, s):
        self._wtype_string(s)

    def send_key_combination(self, combo_string):
        key_events = parse_key_combo(combo_string)
        args = [arg for ev in key_events for arg in key_event_to_wtype_arg(ev)]
        wtype(*args)

    def send_backspaces(self, n):
        self._wtype_string("\b" * n)
