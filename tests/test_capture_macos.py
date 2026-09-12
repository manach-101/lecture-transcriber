from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

import pytest

from src.capture.macos import (
    run_capture,
    start_capture_process,
    stop_capture_process,
)


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


def test_run_capture_raises_actionable_error_when_binary_missing(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "recording.mov"
    missing_binary = tmp_path / "capture"

    with patch("src.capture.macos.CAPTURE_BINARY", missing_binary):
        with pytest.raises(FileNotFoundError, match="scripts/build_capture.sh"):
            run_capture(output_path)


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


def test_start_capture_process_launches_binary_with_piped_stdin(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "recording.mov"
    fake_binary = tmp_path / "capture"
    fake_binary.touch()

    with patch("src.capture.macos.CAPTURE_BINARY", fake_binary), patch(
        "src.capture.macos.subprocess.Popen"
    ) as mock_popen:
        start_capture_process(output_path, display=1)

    mock_popen.assert_called_once_with(
        [str(fake_binary), str(output_path), "1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def test_start_capture_process_raises_when_binary_missing(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "recording.mov"
    missing_binary = tmp_path / "capture"

    with patch("src.capture.macos.CAPTURE_BINARY", missing_binary):
        with pytest.raises(FileNotFoundError, match="scripts/build_capture.sh"):
            start_capture_process(output_path)


def test_stop_capture_process_writes_newline_and_waits() -> None:
    process = MagicMock()
    process.stdin = MagicMock()
    process.returncode = 0

    stop_capture_process(process)

    process.stdin.write.assert_called_once_with("\n")
    process.stdin.flush.assert_called_once()
    process.wait.assert_called_once()


def test_stop_capture_process_raises_on_nonzero_exit() -> None:
    process = MagicMock()
    process.stdin = MagicMock()
    process.returncode = 1
    process.args = ["capture"]

    with pytest.raises(subprocess.CalledProcessError):
        stop_capture_process(process)


def test_stop_capture_process_tolerates_closed_stdin() -> None:
    process = MagicMock()
    process.stdin = MagicMock()
    process.stdin.write.side_effect = BrokenPipeError()
    process.returncode = 0

    stop_capture_process(process)

    process.wait.assert_called_once()
