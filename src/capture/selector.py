import platform
from typing import Callable
from pathlib import Path


def get_capture_backend() -> Callable[[Path, int], None]:
    system = platform.system()

    if system == "Darwin":
        from src.capture.macos import run_capture

        return run_capture

    raise NotImplementedError(
        f"No capture backend available for platform: {system}"
    )
