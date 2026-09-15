# PyInstaller spec for the Lecture Transcriber desktop GUI.
#
# The app only needs PySide6 + the stdlib in-process: recording shells out
# to the compiled Swift capture binary, audio extraction shells out to
# ffmpeg, and transcription shells out to the mlx_whisper CLI. None of the
# heavy ML stack (torch/mlx/numba/scipy) is imported by this codebase, so
# none of it needs to be frozen here — see README "macOS App Packaging".
#
# Run via scripts/build_macos_app.sh. Paths are resolved from SPECPATH
# (this file's directory, set by PyInstaller) rather than the invocation
# CWD, so the build works regardless of where pyinstaller is run from.

import os

REPO_ROOT = os.path.dirname(SPECPATH)  # noqa: F821 (SPECPATH is injected by PyInstaller)

a = Analysis(
    [os.path.join(REPO_ROOT, 'src', 'gui_main.py')],
    pathex=[REPO_ROOT],
    binaries=[],
    datas=[
        (os.path.join(REPO_ROOT, 'assets', 'images'), 'assets/images'),
        (os.path.join(REPO_ROOT, 'native', 'macos', 'capture'), 'native/macos'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Lecture Transcriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Lecture Transcriber',
)
app = BUNDLE(
    coll,
    name='Lecture Transcriber.app',
    icon=None,
    bundle_identifier='com.lecturetranscriber.app',
    info_plist={
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': 'True',
    },
)
