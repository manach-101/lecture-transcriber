from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_BINARY = PROJECT_ROOT / "native" / "macos" / "capture"


def run_capture(output_path: Path, display: int = 0) -> None:
    if not CAPTURE_BINARY.exists():
        raise FileNotFoundError(
            f"macOS capture binary not found: {CAPTURE_BINARY}\n"
            "Build it with: scripts/build_capture.sh"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(CAPTURE_BINARY),
            str(output_path),
            str(display),
        ],
        check=True,
    )


def start_capture_process(
    output_path: Path, display: int = 0
) -> subprocess.Popen:
    """Non-blocking variant of run_capture, for callers (the GUI) that stop
    recording programmatically instead of waiting on stdin ENTER."""
    if not CAPTURE_BINARY.exists():
        raise FileNotFoundError(
            f"macOS capture binary not found: {CAPTURE_BINARY}\n"
            "Build it with: scripts/build_capture.sh"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    return subprocess.Popen(
        [
            str(CAPTURE_BINARY),
            str(output_path),
            str(display),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def stop_capture_process(process: subprocess.Popen) -> None:
    """Mirrors the ENTER keypress the CLI relies on to finish recording."""
    if process.stdin is not None:
        try:
            process.stdin.write("\n")
            process.stdin.flush()
        except (BrokenPipeError, ValueError):
            pass

    process.wait()

    if process.returncode not in (0, None):
        raise subprocess.CalledProcessError(process.returncode, process.args)
