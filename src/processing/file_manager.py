from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECORDINGS_DIR = PROJECT_ROOT / "recordings"
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"


def build_output_paths(class_name: str) -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    recording_filename = f"{class_name}_{timestamp}.mov"
    transcript_filename = f"{class_name}_{timestamp}.txt"

    recording_path = RECORDINGS_DIR / recording_filename
    transcript_path = TRANSCRIPTS_DIR / transcript_filename

    return recording_path, transcript_path