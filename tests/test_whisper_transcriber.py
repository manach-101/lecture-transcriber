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

    def fake_run(command, check):
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
        "--language",
        "es",
        "--output-dir",
        str(transcript_path.parent),
        "--output-name",
        transcript_path.stem,
        "--output-format",
        "txt",
    ]

    mock_run.assert_called_once_with(
        expected_command,
        check=True,
    )


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