"""Color palette and QSS for the dark, cat-themed GUI shell."""

BG_FALLBACK_TOP = "#141a22"
BG_FALLBACK_BOTTOM = "#05070a"

PANEL_BG = "rgba(10, 13, 18, 205)"
PANEL_BORDER = "rgba(255, 255, 255, 28)"

TEXT_PRIMARY = "#F3EFE7"
TEXT_MUTED = "#AEB6C2"
TEXT_FAINT = "#7C838D"

ACCENT_BLUE = "#5B93F5"

CTA_BG = "#3D7CFF"
CTA_BG_HOVER = "#5A91FF"
CTA_BG_PRESSED = "#2E64D9"
CTA_BG_DISABLED = "#2A2F3A"

STOP_BG = "#E5533D"
STOP_BG_HOVER = "#F06B55"
STOP_BG_PRESSED = "#C7432F"
STOP_BG_DISABLED = "#2A2F3A"

SECONDARY_BG = "rgba(255, 255, 255, 18)"
SECONDARY_BG_HOVER = "rgba(255, 255, 255, 32)"
SECONDARY_BG_PRESSED = "rgba(255, 255, 255, 12)"

INPUT_BG = "rgba(255, 255, 255, 14)"
INPUT_BORDER = "rgba(255, 255, 255, 40)"
INPUT_BORDER_FOCUS = ACCENT_BLUE

DISABLED_TEXT = "#6B7178"

STATUS_COLORS = {
    "ready": TEXT_MUTED,
    "recording": STOP_BG,
    "extracting_audio": ACCENT_BLUE,
    "transcribing": ACCENT_BLUE,
    "done": "#4FD17A",
    "error": STOP_BG,
}

STYLESHEET = f"""
QWidget {{
    font-family: ".AppleSystemUIFont", "Helvetica Neue", Arial, sans-serif;
    color: {TEXT_PRIMARY};
}}

QFrame#controlPanel {{
    background-color: {PANEL_BG};
    border: 1px solid {PANEL_BORDER};
    border-radius: 18px;
}}

QLabel#titleLabel {{
    font-size: 26px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#subtitleLabel {{
    font-size: 13px;
    color: {TEXT_MUTED};
}}

QLabel#taglineLabel {{
    font-size: 12px;
    font-style: italic;
    color: {ACCENT_BLUE};
}}

QLabel#supportingCopy {{
    font-size: 11px;
    color: {TEXT_FAINT};
}}

QLabel#fieldLabel {{
    font-size: 11px;
    font-weight: 600;
    color: {TEXT_MUTED};
    letter-spacing: 0.5px;
}}

QLabel#statusValue {{
    font-size: 13px;
    font-weight: 600;
}}

QLabel#pathValue {{
    font-size: 10px;
    color: {TEXT_FAINT};
}}

QLineEdit, QComboBox, QSpinBox {{
    background-color: {INPUT_BG};
    border: 1px solid {INPUT_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    color: {TEXT_PRIMARY};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {INPUT_BORDER_FOCUS};
}}

QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
    color: {DISABLED_TEXT};
    border: 1px solid rgba(255, 255, 255, 18);
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: #14181f;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_BLUE};
    border: 1px solid {INPUT_BORDER};
    outline: none;
}}

QPushButton {{
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#primaryButton {{
    background-color: {CTA_BG};
    color: #FFFFFF;
}}

QPushButton#primaryButton:hover {{
    background-color: {CTA_BG_HOVER};
}}

QPushButton#primaryButton:pressed {{
    background-color: {CTA_BG_PRESSED};
}}

QPushButton#primaryButton:disabled {{
    background-color: {CTA_BG_DISABLED};
    color: {DISABLED_TEXT};
}}

QPushButton#stopButton {{
    background-color: {STOP_BG};
    color: #FFFFFF;
}}

QPushButton#stopButton:hover {{
    background-color: {STOP_BG_HOVER};
}}

QPushButton#stopButton:pressed {{
    background-color: {STOP_BG_PRESSED};
}}

QPushButton#stopButton:disabled {{
    background-color: {STOP_BG_DISABLED};
    color: {DISABLED_TEXT};
}}

QPushButton#secondaryButton {{
    background-color: {SECONDARY_BG};
    color: {TEXT_PRIMARY};
}}

QPushButton#secondaryButton:hover {{
    background-color: {SECONDARY_BG_HOVER};
}}

QPushButton#secondaryButton:pressed {{
    background-color: {SECONDARY_BG_PRESSED};
}}

QPushButton#secondaryButton:disabled {{
    color: {DISABLED_TEXT};
}}

QProgressBar {{
    background-color: {INPUT_BG};
    border: 1px solid {INPUT_BORDER};
    border-radius: 3px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT_BLUE};
    border-radius: 3px;
}}
"""
