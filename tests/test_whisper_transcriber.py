from pathlib import Path
from unittest.mock import patch

import pytest

from src.transcription.whisper_transcriber import (
    MODEL_NAME,
    transcribe_audio,
)


def test_transcribe_audio_builds_expected_command(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    def fake_run(command, check, env):
        transcript_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:
        transcribe_audio(
            audio_path,
            transcript_path,
            language="es",
        )

    expected_command = [
        "mlx_whisper",
        str(audio_path),
        "--model",
        MODEL_NAME,
        "--output-dir",
        str(transcript_path.parent),
        "--output-name",
        transcript_path.stem,
        "--output-format",
        "txt",
        "--verbose",
        "False",
        "--language",
        "es",
    ]

    mock_run.assert_called_once()
    called_command = mock_run.call_args.args[0]
    called_kwargs = mock_run.call_args.kwargs

    assert called_command == expected_command
    assert called_kwargs["check"] is True
    assert called_kwargs["env"]["HF_HUB_DISABLE_PROGRESS_BARS"] == "1"


def test_transcribe_audio_uses_explicit_language(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    def fake_run(command, check, env):
        transcript_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:
        transcribe_audio(
            audio_path,
            transcript_path,
            language="en",
        )

    expected_command = [
        "mlx_whisper",
        str(audio_path),
        "--model",
        MODEL_NAME,
        "--output-dir",
        str(transcript_path.parent),
        "--output-name",
        transcript_path.stem,
        "--output-format",
        "txt",
        "--verbose",
        "False",
        "--language",
        "en",
    ]

    called_command = mock_run.call_args.args[0]
    assert called_command == expected_command


def test_transcribe_audio_omits_language_flag_when_auto(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    def fake_run(command, check, env):
        transcript_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:
        transcribe_audio(
            audio_path,
            transcript_path,
            language="auto",
        )

    expected_command = [
        "mlx_whisper",
        str(audio_path),
        "--model",
        MODEL_NAME,
        "--output-dir",
        str(transcript_path.parent),
        "--output-name",
        transcript_path.stem,
        "--output-format",
        "txt",
        "--verbose",
        "False",
    ]

    called_command = mock_run.call_args.args[0]
    assert called_command == expected_command
    assert "--language" not in called_command


def test_transcribe_audio_passes_quiet_verbose_flag(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    def fake_run(command, check, env):
        transcript_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:
        transcribe_audio(audio_path, transcript_path, language="es")

    called_command = mock_run.call_args.args[0]
    verbose_index = called_command.index("--verbose")
    assert called_command[verbose_index + 1] == "False"


def test_transcribe_audio_disables_huggingface_progress_bars_without_dropping_path(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    def fake_run(command, check, env):
        transcript_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:
        transcribe_audio(audio_path, transcript_path, language="es")

    called_env = mock_run.call_args.kwargs["env"]

    assert called_env["HF_HUB_DISABLE_PROGRESS_BARS"] == "1"
    assert "PATH" in called_env


def test_transcribe_audio_raises_when_audio_does_not_exist(
    tmp_path: Path,
) -> None:
    missing_audio = tmp_path / "missing.wav"
    transcript_path = tmp_path / "output.txt"

    with pytest.raises(FileNotFoundError):
        transcribe_audio(
            missing_audio,
            transcript_path,
        )


def test_transcribe_audio_raises_actionable_error_when_mlx_whisper_missing(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "lecture.wav"
    transcript_path = tmp_path / "lecture.txt"

    audio_path.touch()

    with patch(
        "src.transcription.whisper_transcriber.shutil.which",
        return_value=None,
    ):
        with pytest.raises(FileNotFoundError, match="mlx_whisper"):
            transcribe_audio(audio_path, transcript_path)
