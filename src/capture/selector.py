import platform
import subprocess
from typing import Callable, Tuple
from pathlib import Path


def get_capture_backend() -> Callable[[Path, int], None]:
    system = platform.system()

    if system == "Darwin":
        from src.capture.macos import run_capture

        return run_capture

    raise NotImplementedError(
        f"No capture backend available for platform: {system}"
    )


def get_capture_controls() -> Tuple[
    Callable[[Path, int], subprocess.Popen],
    Callable[[subprocess.Popen], None],
]:
    """Return (start, stop) functions for non-blocking capture control,
    used by the GUI to start/stop a recording asynchronously.
    """
    system = platform.system()

    if system == "Darwin":
        from src.capture.macos import start_capture_process, stop_capture_process

        return start_capture_process, stop_capture_process

    raise NotImplementedError(
        f"No capture backend available for platform: {system}"
    )
