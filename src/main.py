import argparse
import subprocess
import sys
from pathlib import Path

from src.capture.selector import get_capture_backend
from src.processing.audio_extractor import extract_audio
from src.processing.file_manager import build_output_paths
from src.transcription.whisper_transcriber import transcribe_audio


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMP_DIR = PROJECT_ROOT / "temp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record a lecture and generate a local transcript."
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Name used for recording and transcript files.",
    )

    parser.add_argument(
        "--language",
        default="es",
        help="Transcription language code, or 'auto' for automatic detection.",
    )

    parser.add_argument(
        "--display",
        type=int,
        default=0,
        help="Index of the display to capture.",
    )

    return parser.parse_args()


def transcribe_and_cleanup(
    audio_path: Path,
    transcript_path: Path,
    language: str,
) -> None:
    transcribe_audio(
        audio_path,
        transcript_path,
        language=language,
    )

    audio_path.unlink()


def report_failure(stage: str, error: BaseException) -> None:
    print(f"\n{stage} failed: {error}")


def main() -> int:
    args = parse_args()

    class_name = args.name

    recording_path, transcript_path = build_output_paths(class_name)
    audio_path = TEMP_DIR / f"{class_name}.wav"

    print(f"Recording will be saved to:\n{recording_path}\n")

    try:
        run_capture = get_capture_backend()
        run_capture(recording_path, args.display)
    except (
        FileNotFoundError,
        NotImplementedError,
        subprocess.CalledProcessError,
    ) as error:
        report_failure("Recording", error)
        return 1

    print("\nExtracting audio...")

    try:
        extract_audio(
            recording_path,
            audio_path,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        report_failure("Audio extraction", error)
        return 1

    print("\nTranscribing audio...")

    try:
        transcribe_and_cleanup(
            audio_path,
            transcript_path,
            args.language,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        report_failure("Transcription", error)
        return 1

    print("\nDone.")
    print(f"\nRecording saved:\n{recording_path}")
    print(f"\nTranscript saved:\n{transcript_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())