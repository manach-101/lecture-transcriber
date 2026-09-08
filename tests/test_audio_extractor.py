from pathlib import Path
from unittest.mock import patch

import pytest

from src.processing.audio_extractor import extract_audio


def test_extract_audio_builds_expected_ffmpeg_command(tmp_path: Path) -> None:
    input_video = tmp_path / "lecture.mov"
    output_audio = tmp_path / "lecture.wav"

    input_video.touch()

    with patch("src.processing.audio_extractor.subprocess.run") as mock_run:
        extract_audio(input_video, output_audio)

    expected_command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_audio),
    ]

    mock_run.assert_called_once_with(
        expected_command,
        check=True,
    )


def test_extract_audio_raises_when_input_does_not_exist(
    tmp_path: Path,
) -> None:
    missing_video = tmp_path / "missing.mov"
    output_audio = tmp_path / "output.wav"

    with pytest.raises(FileNotFoundError):
        extract_audio(
            missing_video,
            output_audio,
        )
        