from pathlib import Path
from unittest.mock import patch

from src.app_paths import bundle_root, is_frozen, user_data_root


def test_is_frozen_false_by_default() -> None:
    assert is_frozen() is False


def test_bundle_root_is_repo_root_when_not_frozen() -> None:
    with patch("src.app_paths.is_frozen", return_value=False):
        root = bundle_root()

    assert (root / "src").is_dir()
    assert (root / "native").is_dir()


def test_bundle_root_is_contents_resources_dir_when_frozen(tmp_path: Path) -> None:
    fake_executable = (
        tmp_path / "App.app" / "Contents" / "MacOS" / "LectureTranscriber"
    )
    fake_executable.parent.mkdir(parents=True)
    fake_executable.touch()

    with patch("src.app_paths.is_frozen", return_value=True), patch(
        "src.app_paths.sys.executable", str(fake_executable)
    ):
        root = bundle_root()

    assert root == tmp_path / "App.app" / "Contents" / "Resources"


def test_user_data_root_is_repo_root_when_not_frozen() -> None:
    with patch("src.app_paths.is_frozen", return_value=False):
        root = user_data_root()

    assert (root / "src").is_dir()


def test_user_data_root_is_application_support_when_frozen() -> None:
    with patch("src.app_paths.is_frozen", return_value=True):
        root = user_data_root()

    assert root == Path.home() / "Library" / "Application Support" / "Lecture Transcriber"
