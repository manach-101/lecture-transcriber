from unittest.mock import patch

import pytest

from src.capture.selector import get_capture_backend


def test_get_capture_backend_returns_macos_backend_on_darwin() -> None:
    with patch(
        "src.capture.selector.platform.system",
        return_value="Darwin",
    ):
        from src.capture.macos import run_capture as macos_run_capture

        backend = get_capture_backend()

    assert backend is macos_run_capture


def test_get_capture_backend_raises_for_unsupported_platform() -> None:
    with patch(
        "src.capture.selector.platform.system",
        return_value="Windows",
    ):
        with pytest.raises(NotImplementedError):
            get_capture_backend()
