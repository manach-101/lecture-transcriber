from pathlib import Path
import shutil
import subprocess


def extract_audio(input_video: Path, output_audio: Path) -> None:
    if not input_video.exists():
        raise FileNotFoundError(
            f"Input video not found: {input_video}"
        )

    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError(
            "ffmpeg not found on PATH. Install it with: brew install ffmpeg"
        )

    output_audio.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_video),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(output_audio),
    ]

    subprocess.run(
        command,
        check=True,
    )