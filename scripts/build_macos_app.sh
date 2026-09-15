#!/usr/bin/env bash
# Builds the "Lecture Transcriber" macOS .app bundle from a clean dev
# environment. See README "macOS App Packaging" for what is and isn't
# bundled (ffmpeg and mlx_whisper remain external, like the CLI).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_PYINSTALLER="$REPO_ROOT/.venv/bin/pyinstaller"

echo "==> Checking build prerequisites"

if [ ! -x "$VENV_PYINSTALLER" ]; then
  echo "ERROR: pyinstaller not found in .venv."
  echo "Set up the dev environment first:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

if ! command -v swiftc >/dev/null 2>&1; then
  echo "ERROR: swiftc not found."
  echo "Xcode (or the Xcode command line tools) is required to build the"
  echo "native capture helper. See README 'Xcode' section."
  exit 1
fi

echo "==> Compiling native macOS capture helper"
scripts/build_capture.sh

if [ ! -x "$REPO_ROOT/native/macos/capture" ]; then
  echo "ERROR: native/macos/capture was not produced by scripts/build_capture.sh"
  exit 1
fi

if [ ! -f "$REPO_ROOT/assets/images/cat_hero_bg.png" ]; then
  echo "WARNING: assets/images/cat_hero_bg.png not found."
  echo "The packaged app will fall back to a plain dark background."
fi

echo "==> Building the .app bundle with PyInstaller"
rm -rf "$REPO_ROOT/build" "$REPO_ROOT/dist"

"$VENV_PYINSTALLER" \
  --noconfirm \
  --clean \
  --distpath "$REPO_ROOT/dist" \
  --workpath "$REPO_ROOT/build" \
  "$REPO_ROOT/packaging/LectureTranscriber.spec"

APP_PATH="$REPO_ROOT/dist/Lecture Transcriber.app"

echo "==> Validating bundled resources"

fail=0

if [ ! -d "$APP_PATH" ]; then
  echo "ERROR: app bundle was not created at: $APP_PATH"
  exit 1
fi

if [ ! -x "$APP_PATH/Contents/MacOS/Lecture Transcriber" ]; then
  echo "ERROR: bundle executable missing: $APP_PATH/Contents/MacOS/Lecture Transcriber"
  fail=1
fi

if [ ! -x "$APP_PATH/Contents/Resources/native/macos/capture" ]; then
  echo "ERROR: capture helper missing from bundle: $APP_PATH/Contents/Resources/native/macos/capture"
  fail=1
fi

if [ ! -f "$APP_PATH/Contents/Resources/assets/images/cat_hero_bg.png" ]; then
  echo "WARNING: hero background image missing from bundle (app will use the fallback background)."
fi

if [ "$fail" -ne 0 ]; then
  echo "==> Build validation FAILED"
  exit 1
fi

echo "==> Build succeeded"
echo "App bundle: $APP_PATH"
echo ""
echo "Launch it with:"
echo "  open \"$APP_PATH\""
echo ""
echo "NOTE: ffmpeg and mlx_whisper must still be installed and on PATH on"
echo "the machine running this app for recording/transcription to work."
echo "See README 'macOS App Packaging' for details and current limitations."
