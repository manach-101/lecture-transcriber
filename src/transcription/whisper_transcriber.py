from pathlib import Path
import subprocess


MODEL_NAME = "mlx-community/whisper-large-v3-turbo"


def transcribe_audio(
    audio_path: Path,
    transcript_path: Path,
    language: str = "es",
) -> None:
    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    transcript_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "mlx_whisper",
        str(audio_path),
        "--model",
        MODEL_NAME,
        "--output-dir",
        str(transcript_path.parent),
        "--output-name",
        transcript_path.stem,
        "--output-format",
        "txt",
    ]

    if language != "auto":
        command.extend(["--language", language])

    subprocess.run(
        command,
        check=True,
    )

    if not transcript_path.exists():
        raise FileNotFoundError(
            f"Transcript was not created: {transcript_path}"
        )