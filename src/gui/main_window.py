import time

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.gui.hero_background import HeroBackground
from src.gui.pipeline import LANGUAGE_CHOICES, STAGE_LABELS, Stage, language_label_to_code
from src.gui.styles import STATUS_COLORS, STYLESHEET, TEXT_PRIMARY
from src.gui.worker import RecordingWorker
from src.processing.file_manager import RECORDINGS_DIR, TRANSCRIPTS_DIR


DEFAULT_LANGUAGE_LABEL = "Spanish"
MAX_DISPLAY_INDEX = 8


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lecture Transcriber")
        self.resize(1180, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(STYLESHEET)

        self._worker = None
        self._recording_started_at = None
        self._last_recording_path = None
        self._last_transcript_path = None

        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(1000)
        self._elapsed_timer.timeout.connect(self._tick_elapsed)

        self._build_ui()
        self._set_stage(Stage.READY)

    def _build_ui(self) -> None:
        background = HeroBackground(self)
        root_layout = QHBoxLayout(background)
        root_layout.setContentsMargins(40, 40, 40, 40)

        panel = self._build_panel()

        column = QVBoxLayout()
        column.addStretch(1)
        column.addWidget(panel)
        column.addStretch(1)

        root_layout.addLayout(column, 0)
        root_layout.addStretch(1)

        self.setCentralWidget(background)

    def _build_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("controlPanel")
        panel.setFixedWidth(400)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Lecture Transcriber")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Local screen recording + on-device transcription")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        tagline = QLabel("For the lazy but smart.")
        tagline.setObjectName("taglineLabel")
        layout.addWidget(tagline)

        supporting = QLabel(
            "Built for students and professionals who'd rather stay focused "
            "than type notes. Recording and transcription both run on this "
            "Mac — nothing leaves your machine."
        )
        supporting.setObjectName("supportingCopy")
        supporting.setWordWrap(True)
        layout.addWidget(supporting)

        layout.addSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. discrete_math")
        layout.addWidget(self._labeled("RECORDING NAME", self.name_input))

        self.capture_target_combo = QComboBox()
        self.capture_target_combo.addItem("Display")
        self.capture_target_combo.setEnabled(False)
        layout.addWidget(self._labeled("CAPTURE TARGET", self.capture_target_combo))

        self.display_spin = QSpinBox()
        self.display_spin.setRange(0, MAX_DISPLAY_INDEX)
        layout.addWidget(self._labeled("DISPLAY INDEX", self.display_spin))

        self.language_combo = QComboBox()
        for label, _code in LANGUAGE_CHOICES:
            self.language_combo.addItem(label)
        self.language_combo.setCurrentText(DEFAULT_LANGUAGE_LABEL)
        layout.addWidget(self._labeled("LANGUAGE", self.language_combo))

        layout.addSpacing(6)

        record_row = QHBoxLayout()
        record_row.setSpacing(10)

        self.start_button = QPushButton("Start Recording")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self._on_start_clicked)
        record_row.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        record_row.addWidget(self.stop_button)

        layout.addLayout(record_row)

        open_row = QHBoxLayout()
        open_row.setSpacing(10)

        self.open_recordings_button = QPushButton("Open Recordings")
        self.open_recordings_button.setObjectName("secondaryButton")
        self.open_recordings_button.clicked.connect(
            lambda: self._open_folder(RECORDINGS_DIR)
        )
        open_row.addWidget(self.open_recordings_button)

        self.open_transcripts_button = QPushButton("Open Transcripts")
        self.open_transcripts_button.setObjectName("secondaryButton")
        self.open_transcripts_button.clicked.connect(
            lambda: self._open_folder(TRANSCRIPTS_DIR)
        )
        open_row.addWidget(self.open_transcripts_button)

        layout.addLayout(open_row)

        layout.addSpacing(6)

        status_row = QHBoxLayout()

        status_label = QLabel("STATUS")
        status_label.setObjectName("fieldLabel")
        status_row.addWidget(status_label)

        self.status_value = QLabel(STAGE_LABELS[Stage.READY])
        self.status_value.setObjectName("statusValue")
        status_row.addWidget(self.status_value)

        status_row.addStretch(1)

        self.elapsed_value = QLabel("00:00:00")
        self.elapsed_value.setObjectName("statusValue")
        self.elapsed_value.setStyleSheet(f"color: {TEXT_PRIMARY};")
        status_row.addWidget(self.elapsed_value)

        layout.addLayout(status_row)

        self.path_value = QLabel("No recordings yet.")
        self.path_value.setObjectName("pathValue")
        self.path_value.setWordWrap(True)
        layout.addWidget(self.path_value)

        layout.addStretch(1)

        return panel

    def _labeled(self, text: str, field: QWidget) -> QWidget:
        container = QWidget()
        column = QVBoxLayout(container)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)

        label = QLabel(text)
        label.setObjectName("fieldLabel")
        column.addWidget(label)
        column.addWidget(field)

        return container

    def _settings_widgets(self):
        return (
            self.name_input,
            self.display_spin,
            self.language_combo,
        )

    def _set_stage(self, stage: str, detail: str = "") -> None:
        self.status_value.setText(STAGE_LABELS.get(stage, stage))
        color = STATUS_COLORS.get(stage, TEXT_PRIMARY)
        self.status_value.setStyleSheet(f"color: {color};")

        if detail:
            self.path_value.setText(detail)

    def _tick_elapsed(self) -> None:
        if self._recording_started_at is None:
            return

        elapsed = int(time.monotonic() - self._recording_started_at)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed_value.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def _on_start_clicked(self) -> None:
        name = self.name_input.text().strip()

        if not name:
            self._set_stage(Stage.ERROR, "Recording name is required.")
            return

        language_code = language_label_to_code(self.language_combo.currentText())
        display = self.display_spin.value()

        for widget in self._settings_widgets():
            widget.setEnabled(False)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.elapsed_value.setText("00:00:00")
        self._recording_started_at = time.monotonic()
        self._elapsed_timer.start()

        self._worker = RecordingWorker(name, language_code, display, parent=self)
        self._worker.stage_changed.connect(self._on_stage_changed)
        self._worker.recording_started.connect(self._on_recording_started)
        self._worker.finished_ok.connect(self._on_finished_ok)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_stop_clicked(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()

        self.stop_button.setEnabled(False)
        self._elapsed_timer.stop()

    def _on_stage_changed(self, stage: str) -> None:
        self._set_stage(stage)

    def _on_recording_started(self, recording_path: str, transcript_path: str) -> None:
        self._last_recording_path = recording_path
        self._last_transcript_path = transcript_path
        self.path_value.setText(f"Recording to:\n{recording_path}")

    def _on_finished_ok(self, recording_path: str, transcript_path: str) -> None:
        self._last_recording_path = recording_path
        self._last_transcript_path = transcript_path
        self.path_value.setText(
            f"Recording:\n{recording_path}\n\nTranscript:\n{transcript_path}"
        )
        self._finish_run()

    def _on_failed(self, stage: str, message: str) -> None:
        stage_name = STAGE_LABELS.get(stage, stage)
        self.path_value.setText(f"{stage_name} failed:\n{message}")
        self._finish_run()

    def _finish_run(self) -> None:
        self._elapsed_timer.stop()
        self._recording_started_at = None

        for widget in self._settings_widgets():
            widget.setEnabled(True)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._worker = None

    def _open_folder(self, path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            confirmation = QMessageBox.question(
                self,
                "Recording in progress",
                "A recording is still running. Stop it and quit?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if confirmation != QMessageBox.Yes:
                event.ignore()
                return

            self._worker.request_stop()
            self._worker.wait(10_000)

        event.accept()
