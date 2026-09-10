from pathlib import Path
import os
import shutil
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

    if shutil.which("mlx_whisper") is None:
        raise FileNotFoundError(
            "mlx_whisper not found on PATH. Install it with: "
            "pip install -r requirements.txt"
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
        "--verbose",
        "False",
    ]

    if language != "auto":
        command.extend(["--language", language])

    # mlx_whisper's own --verbose flag only controls the "Args: {...}" line
    # and per-segment prints. Model loading always goes through
    # huggingface_hub's snapshot_download, which prints its own "Fetching
    # N files" progress bar even on a pure cache hit; this env var is the
    # supported way to silence that separately from --verbose.
    env = {**os.environ, "HF_HUB_DISABLE_PROGRESS_BARS": "1"}

    subprocess.run(
        command,
        check=True,
        env=env,
    )

    if not transcript_path.exists():
        raise FileNotFoundError(
            f"Transcript was not created: {transcript_path}"
        )