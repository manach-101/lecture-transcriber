import argparse
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.main import main, transcribe_and_cleanup


def test_transcribe_and_cleanup_removes_wav_on_success(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    with patch("src.main.transcribe_audio") as mock_transcribe:
        transcribe_and_cleanup(audio_path, transcript_path, "es")

    mock_transcribe.assert_called_once_with(
        audio_path,
        transcript_path,
        language="es",
    )

    assert not audio_path.exists()


def test_transcribe_and_cleanup_preserves_wav_on_failure(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    with patch(
        "src.main.transcribe_audio",
        side_effect=RuntimeError("transcription failed"),
    ):
        with pytest.raises(RuntimeError):
            transcribe_and_cleanup(audio_path, transcript_path, "es")

    assert audio_path.exists()


def _fake_args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(name="lecture", language="es")


def test_main_reports_error_and_exits_nonzero_when_capture_binary_missing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture.txt"

    with patch("src.main.parse_args", return_value=_fake_args(tmp_path)), patch(
        "src.main.build_output_paths",
        return_value=(recording_path, transcript_path),
    ), patch(
        "src.main.get_capture_backend",
        side_effect=FileNotFoundError(
            "macOS capture binary not found: native/macos/capture"
        ),
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Recording failed" in capsys.readouterr().out


def test_main_reports_error_and_exits_nonzero_when_capture_subprocess_fails(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture.txt"

    failing_run_capture = Mock(
        side_effect=subprocess.CalledProcessError(1, ["capture"])
    )

    with patch("src.main.parse_args", return_value=_fake_args(tmp_path)), patch(
        "src.main.build_output_paths",
        return_value=(recording_path, transcript_path),
    ), patch(
        "src.main.get_capture_backend",
        return_value=failing_run_capture,
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Recording failed" in capsys.readouterr().out


def test_main_reports_error_and_exits_nonzero_when_ffmpeg_missing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture.txt"

    with patch("src.main.parse_args", return_value=_fake_args(tmp_path)), patch(
        "src.main.build_output_paths",
        return_value=(recording_path, transcript_path),
    ), patch(
        "src.main.get_capture_backend",
        return_value=lambda path: None,
    ), patch(
        "src.main.extract_audio",
        side_effect=FileNotFoundError(
            "[Errno 2] No such file or directory: 'ffmpeg'"
        ),
    ):
        exit_code = main()

    assert exit_code == 1
    assert "Audio extraction failed" in capsys.readouterr().out


def test_main_preserves_wav_and_exits_nonzero_when_transcription_fails(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture.txt"

    with patch("src.main.TEMP_DIR", tmp_path):
        audio_path = tmp_path / "lecture.wav"
        audio_path.touch()

        with patch(
            "src.main.parse_args", return_value=_fake_args(tmp_path)
        ), patch(
            "src.main.build_output_paths",
            return_value=(recording_path, transcript_path),
        ), patch(
            "src.main.get_capture_backend",
            return_value=lambda path: None,
        ), patch(
            "src.main.extract_audio",
            return_value=None,
        ), patch(
            "src.main.transcribe_audio",
            side_effect=FileNotFoundError(
                "[Errno 2] No such file or directory: 'mlx_whisper'"
            ),
        ):
            exit_code = main()

        assert exit_code == 1
        assert "Transcription failed" in capsys.readouterr().out
        assert audio_path.exists()


def test_main_returns_zero_on_success(
    tmp_path: Path,
) -> None:
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture.txt"

    with patch("src.main.TEMP_DIR", tmp_path):
        audio_path = tmp_path / "lecture.wav"
        audio_path.touch()

        with patch(
            "src.main.parse_args", return_value=_fake_args(tmp_path)
        ), patch(
            "src.main.build_output_paths",
            return_value=(recording_path, transcript_path),
        ), patch(
            "src.main.get_capture_backend",
            return_value=lambda path: None,
        ), patch(
            "src.main.extract_audio",
            return_value=None,
        ), patch(
            "src.main.transcribe_audio",
            return_value=None,
        ):
            exit_code = main()

        assert exit_code == 0
        assert not audio_path.exists()
