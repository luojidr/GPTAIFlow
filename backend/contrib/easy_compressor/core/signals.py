from blinker import Namespace

_signals = Namespace()

batch_saved = _signals.signal("batch-saved")


