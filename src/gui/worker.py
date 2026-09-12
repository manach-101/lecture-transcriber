import threading

from PySide6.QtCore import QThread, Signal

from src.gui.pipeline import RecordingSession, Stage


class RecordingWorker(QThread):
    """Runs the record -> extract -> transcribe pipeline off the UI
    thread. Stopping is a threading.Event so the blocking subprocess wait
    and the ffmpeg/whisper calls all stay off the main thread."""

    stage_changed = Signal(str)
    recording_started = Signal(str, str)
    finished_ok = Signal(str, str)
    failed = Signal(str, str)

    def __init__(self, name: str, language: str, display: int, parent=None):
        super().__init__(parent)
        self._name = name
        self._language = language
        self._display = display
        self._session = RecordingSession()
        self._stop_event = threading.Event()

    def request_stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        stage = Stage.RECORDING

        try:
            self.stage_changed.emit(Stage.RECORDING)

            recording_path, transcript_path = self._session.start_recording(
                self._name, self._display
            )
            self.recording_started.emit(
                str(recording_path), str(transcript_path)
            )

            self._stop_event.wait()
            self._session.stop_recording()

            stage = Stage.EXTRACTING
            self.stage_changed.emit(Stage.EXTRACTING)
            audio_path = self._session.extract(recording_path, transcript_path)

            stage = Stage.TRANSCRIBING
            self.stage_changed.emit(Stage.TRANSCRIBING)
            self._session.transcribe(audio_path, transcript_path, self._language)

            self.stage_changed.emit(Stage.DONE)
            self.finished_ok.emit(str(recording_path), str(transcript_path))
        except Exception as error:
            self.stage_changed.emit(Stage.ERROR)
            self.failed.emit(stage, str(error))
