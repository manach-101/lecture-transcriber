import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

PySide6 = pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.gui.pipeline import Stage


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


@pytest.fixture
def window(app):
    win = MainWindow()
    yield win
    win.deleteLater()


def test_initial_state_is_ready_with_stop_disabled(window: MainWindow) -> None:
    assert window.status_value.text() == "Ready"
    assert not window.stop_button.isEnabled()
    assert window.start_button.isEnabled()


def test_start_with_empty_name_shows_error_without_starting_worker(
    window: MainWindow,
) -> None:
    window.name_input.setText("   ")

    window._on_start_clicked()

    assert window.status_value.text() == "Error"
    assert "name is required" in window.path_value.text()
    assert window._worker is None
    assert window.start_button.isEnabled()


def test_on_failed_restores_controls_and_shows_message(window: MainWindow) -> None:
    window.name_input.setEnabled(False)
    window.start_button.setEnabled(False)
    window.stop_button.setEnabled(True)

    window._on_failed(Stage.EXTRACTING, "ffmpeg not found on PATH.")

    assert "ffmpeg not found on PATH." in window.path_value.text()
    assert window.name_input.isEnabled()
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()


def test_on_finished_ok_restores_controls_and_shows_paths(window: MainWindow) -> None:
    window.start_button.setEnabled(False)
    window.stop_button.setEnabled(True)

    window._on_finished_ok("/tmp/rec.mov", "/tmp/rec.txt")

    assert "/tmp/rec.mov" in window.path_value.text()
    assert "/tmp/rec.txt" in window.path_value.text()
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()
