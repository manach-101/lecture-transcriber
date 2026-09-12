from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.gui.pipeline import RecordingSession, language_label_to_code


def _fake_controls(process):
    start = MagicMock(return_value=process)
    stop = MagicMock()
    return MagicMock(return_value=(start, stop)), start, stop


def test_start_recording_returns_output_paths_and_starts_process(
    tmp_path: Path,
) -> None:
    process = MagicMock()
    get_controls, start, _stop = _fake_controls(process)

    session = RecordingSession(get_controls=get_controls)

    with patch_build_output_paths(tmp_path) as (recording_path, transcript_path):
        result = session.start_recording("lecture", display=1)

    assert result == (recording_path, transcript_path)
    start.assert_called_once_with(recording_path, 1)


def test_stop_recording_calls_backend_stop_with_process(tmp_path: Path) -> None:
    process = MagicMock()
    get_controls, _start, stop = _fake_controls(process)

    session = RecordingSession(get_controls=get_controls)

    with patch_build_output_paths(tmp_path):
        session.start_recording("lecture", display=0)

    session.stop_recording()

    stop.assert_called_once_with(process)


def test_stop_recording_before_start_is_a_no_op() -> None:
    session = RecordingSession(get_controls=MagicMock())

    session.stop_recording()


def test_extract_builds_temp_wav_path_from_transcript_stem(tmp_path: Path) -> None:
    session = RecordingSession(get_controls=MagicMock())
    recording_path = tmp_path / "lecture.mov"
    transcript_path = tmp_path / "lecture_2026-01-01.txt"

    with patch_extract_audio() as mock_extract, patch_temp_dir(tmp_path):
        audio_path = session.extract(recording_path, transcript_path)

    assert audio_path == tmp_path / "lecture_2026-01-01.wav"
    mock_extract.assert_called_once_with(recording_path, audio_path)


def test_transcribe_removes_audio_after_success(tmp_path: Path) -> None:
    session = RecordingSession(get_controls=MagicMock())
    audio_path = tmp_path / "lecture.wav"
    audio_path.touch()
    transcript_path = tmp_path / "lecture.txt"

    with patch_transcribe_audio() as mock_transcribe:
        session.transcribe(audio_path, transcript_path, "en")

    mock_transcribe.assert_called_once_with(
        audio_path, transcript_path, language="en"
    )
    assert not audio_path.exists()


def test_language_label_to_code_maps_known_labels() -> None:
    assert language_label_to_code("Auto") == "auto"
    assert language_label_to_code("Spanish") == "es"
    assert language_label_to_code("English") == "en"


def test_language_label_to_code_returns_none_for_unknown_label() -> None:
    assert language_label_to_code("Klingon") is None


# --- local helpers -----------------------------------------------------


@contextmanager
def patch_build_output_paths(tmp_path: Path):
    recording_path = tmp_path / "lecture_2026-01-01.mov"
    transcript_path = tmp_path / "lecture_2026-01-01.txt"

    with patch(
        "src.gui.pipeline.build_output_paths",
        return_value=(recording_path, transcript_path),
    ):
        yield recording_path, transcript_path


@contextmanager
def patch_extract_audio():
    with patch("src.gui.pipeline.extract_audio") as mock_extract:
        yield mock_extract


@contextmanager
def patch_transcribe_audio():
    with patch("src.gui.pipeline.transcribe_audio") as mock_transcribe:
        yield mock_transcribe


@contextmanager
def patch_temp_dir(tmp_path: Path):
    with patch("src.gui.pipeline.TEMP_DIR", tmp_path):
        yield
