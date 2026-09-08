from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_BINARY = PROJECT_ROOT / "native" / "macos" / "capture"


def run_capture(output_path: Path) -> None:
    if not CAPTURE_BINARY.exists():
        raise FileNotFoundError(
            f"macOS capture binary not found: {CAPTURE_BINARY}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            str(CAPTURE_BINARY),
            str(output_path),
        ],
        check=True,
    )