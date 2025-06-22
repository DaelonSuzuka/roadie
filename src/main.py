# fix "RuntimeError: A SemLock created in a fork context is being shared with a process in a spawn context."
# https://github.com/zauberzeug/nicegui/issues/1841#issuecomment-1942955835
import multiprocessing

multiprocessing.set_start_method('spawn', force=True)


import nicegui.ui as ui  # noqa: E402
import roadie  # noqa: E402 F401

ui.run(
    dark=True,
    native=True,
)
