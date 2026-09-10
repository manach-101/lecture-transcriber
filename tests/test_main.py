from pathlib import Path
from unittest.mock import patch

import pytest

from src.main import transcribe_and_cleanup


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
