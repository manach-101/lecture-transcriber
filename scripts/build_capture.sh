#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT_DIR/native/macos/capture.swift"
OUTPUT="$ROOT_DIR/native/macos/capture"

if ! command -v swiftc >/dev/null 2>&1; then
    echo "Error: swiftc not found." >&2
    echo "Install Xcode or the Xcode Command Line Tools, then re-run this script." >&2
    exit 1
fi

echo "Compiling macOS capture helper..."
swiftc -parse-as-library "$SOURCE" -o "$OUTPUT"
echo "Built: $OUTPUT"
