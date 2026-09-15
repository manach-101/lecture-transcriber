from pathlib import Path
from typing import Optional, Tuple

from src.app_paths import user_data_root
from src.capture.selector import get_capture_controls
from src.processing.audio_extractor import extract_audio
from src.processing.file_manager import build_output_paths
from src.transcription.whisper_transcriber import transcribe_audio


TEMP_DIR = user_data_root() / "temp"


class Stage:
    READY = "ready"
    RECORDING = "recording"
    EXTRACTING = "extracting_audio"
    TRANSCRIBING = "transcribing"
    DONE = "done"
    ERROR = "error"


STAGE_LABELS = {
    Stage.READY: "Ready",
    Stage.RECORDING: "Recording",
    Stage.EXTRACTING: "Extracting audio",
    Stage.TRANSCRIBING: "Transcribing",
    Stage.DONE: "Done",
    Stage.ERROR: "Error",
}


class RecordingSession:
    """Orchestrates one record -> extract -> transcribe run using the
    existing backend modules, split into separate steps so a GUI thread
    can drive start/stop asynchronously instead of blocking on stdin."""

    def __init__(self, get_controls=get_capture_controls):
        self._get_controls = get_controls
        self._process = None
        self._stop_capture = None

    def start_recording(
        self, name: str, display: int
    ) -> Tuple[Path, Path]:
        start_capture, stop_capture = self._get_controls()
        self._stop_capture = stop_capture

        recording_path, transcript_path = build_output_paths(name)
        self._process = start_capture(recording_path, display)

        return recording_path, transcript_path

    def stop_recording(self) -> None:
        if self._process is not None and self._stop_capture is not None:
            self._stop_capture(self._process)

    def extract(self, recording_path: Path, transcript_path: Path) -> Path:
        audio_path = TEMP_DIR / f"{transcript_path.stem}.wav"
        extract_audio(recording_path, audio_path)
        return audio_path

    def transcribe(
        self,
        audio_path: Path,
        transcript_path: Path,
        language: str,
    ) -> None:
        transcribe_audio(audio_path, transcript_path, language=language)
        audio_path.unlink()


LANGUAGE_CHOICES = (
    ("Auto", "auto"),
    ("Spanish", "es"),
    ("English", "en"),
)


def language_label_to_code(label: str) -> Optional[str]:
    for choice_label, code in LANGUAGE_CHOICES:
        if choice_label == label:
            return code
    return None
