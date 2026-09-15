import sys
from pathlib import Path


def is_frozen() -> bool:
    """True when running inside a PyInstaller-frozen app bundle."""
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    """Root for read-only bundled resources (assets, the compiled capture
    binary): the repo root in development. When packaged, PyInstaller's
    macOS .app layout puts the executable in `Contents/MacOS/` but
    `--add-data` resources in `Contents/Resources/` (mirrored into
    `Contents/Frameworks/` via symlink), so resolve from there instead of
    next to the executable."""
    if is_frozen():
        return Path(sys.executable).resolve().parent.parent / "Resources"

    return Path(__file__).resolve().parents[1]


def user_data_root() -> Path:
    """Root for files the app writes (recordings, transcripts, temp
    audio): the repo root in development, matching prior behavior; a
    writable per-user directory when packaged, since an installed `.app`
    bundle is read-only."""
    if is_frozen():
        return Path.home() / "Library" / "Application Support" / "Lecture Transcriber"

    return Path(__file__).resolve().parents[1]
