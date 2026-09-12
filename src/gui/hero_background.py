from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QLinearGradient, QColor
from PySide6.QtWidgets import QWidget

from src.gui.styles import BG_FALLBACK_TOP, BG_FALLBACK_BOTTOM


ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"
HERO_IMAGE_PATH = ASSETS_DIR / "cat_hero_bg.png"


class HeroBackground(QWidget):
    """Paints the hero image (cover-fit, cropped to the window) with a dark
    gradient overlay so the control panel text stays readable. Falls back
    to a plain dark gradient when the image asset is not present yet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None

        if HERO_IMAGE_PATH.exists():
            pixmap = QPixmap(str(HERO_IMAGE_PATH))
            if not pixmap.isNull():
                self._pixmap = pixmap

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        rect = self.rect()

        if self._pixmap is not None:
            scaled = self._pixmap.scaled(
                rect.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
            x = (rect.width() - scaled.width()) // 2
            y = (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            gradient = QLinearGradient(0, 0, rect.width(), rect.height())
            gradient.setColorAt(0.0, QColor(BG_FALLBACK_TOP))
            gradient.setColorAt(1.0, QColor(BG_FALLBACK_BOTTOM))
            painter.fillRect(rect, gradient)

        overlay = QLinearGradient(0, 0, rect.width(), 0)
        overlay.setColorAt(0.0, QColor(4, 6, 9, 235))
        overlay.setColorAt(0.55, QColor(4, 6, 9, 130))
        overlay.setColorAt(1.0, QColor(4, 6, 9, 40))
        painter.fillRect(rect, overlay)

        bottom_fade = QLinearGradient(0, rect.height() * 0.6, 0, rect.height())
        bottom_fade.setColorAt(0.0, QColor(0, 0, 0, 0))
        bottom_fade.setColorAt(1.0, QColor(0, 0, 0, 90))
        painter.fillRect(rect, bottom_fade)

        painter.end()
