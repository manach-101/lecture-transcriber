from src.processing.file_manager import build_output_paths


def test_build_output_paths_uses_same_timestamp() -> None:
    recording_path, transcript_path = build_output_paths("discrete_math")

    recording_stem = recording_path.stem
    transcript_stem = transcript_path.stem

    assert recording_stem == transcript_stem
    assert recording_path.suffix == ".mov"
    assert transcript_path.suffix == ".txt"


def test_build_output_paths_uses_class_name() -> None:
    recording_path, transcript_path = build_output_paths("systems_engineering")

    assert recording_path.name.startswith("systems_engineering_")
    assert transcript_path.name.startswith("systems_engineering_")