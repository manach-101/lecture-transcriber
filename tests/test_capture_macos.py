from pathlib import Path
from unittest.mock import patch
import subprocess

import pytest

from src.capture.macos import run_capture


def test_run_capture_uses_default_display_zero(tmp_path: Path) -> None:
    output_path = tmp_path / "recording.mov"
    fake_binary = tmp_path / "capture"
    fake_binary.touch()

    with patch("src.capture.macos.CAPTURE_BINARY", fake_binary), patch(
        "src.capture.macos.subprocess.run"
    ) as mock_run:
        run_capture(output_path)

    mock_run.assert_called_once_with(
        [str(fake_binary), str(output_path), "0"],
        check=True,
    )


def test_run_capture_uses_explicit_display(tmp_path: Path) -> None:
    output_path = tmp_path / "recording.mov"
    fake_binary = tmp_path / "capture"
    fake_binary.touch()

    with patch("src.capture.macos.CAPTURE_BINARY", fake_binary), patch(
        "src.capture.macos.subprocess.run"
    ) as mock_run:
        run_capture(output_path, display=2)

    mock_run.assert_called_once_with(
        [str(fake_binary), str(output_path), "2"],
        check=True,
    )


def test_run_capture_propagates_error_for_invalid_display(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "recording.mov"
    fake_binary = tmp_path / "capture"
    fake_binary.touch()

    with patch("src.capture.macos.CAPTURE_BINARY", fake_binary), patch(
        "src.capture.macos.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, [str(fake_binary)]),
    ):
        with pytest.raises(subprocess.CalledProcessError):
            run_capture(output_path, display=99)
