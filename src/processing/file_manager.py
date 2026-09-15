from datetime import datetime
from pathlib import Path

from src.app_paths import user_data_root


RECORDINGS_DIR = user_data_root() / "recordings"
TRANSCRIPTS_DIR = user_data_root() / "transcripts"


def build_output_paths(class_name: str) -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    recording_filename = f"{class_name}_{timestamp}.mov"
    transcript_filename = f"{class_name}_{timestamp}.txt"

    recording_path = RECORDINGS_DIR / recording_filename
    transcript_path = TRANSCRIPTS_DIR / transcript_filename

    return recording_path, transcript_path