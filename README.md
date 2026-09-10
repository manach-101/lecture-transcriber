# Lecture Transcriber

A local-first lecture recording and transcription tool for macOS.

Lecture Transcriber records the screen and system audio using Apple's native ScreenCaptureKit framework, saves the recording locally, extracts speech-optimized audio with FFmpeg, and generates a raw transcript using Whisper optimized for Apple Silicon.

No recordings, extracted audio files, or transcripts are uploaded to external services.

## Current Status

The core V0 pipeline is stable on macOS. V1 development is currently in progress.

Current pipeline:

```text
Screen + System Audio
        ↓
ScreenCaptureKit
        ↓
MOV Recording
        ↓
FFmpeg
        ↓
16 kHz Mono WAV
        ↓
MLX Whisper
        ↓
TXT Transcript
```

The current implementation has been tested on:

- MacBook Air with Apple M4
- macOS Sequoia 15.3
- Python 3.9.6
- Xcode 16.4
- FFmpeg 9.0.1
- MLX Whisper
- Whisper Large V3 Turbo

## Features

- Native macOS screen capture
- Selectable display via `--display INDEX` (default: `0`)
- System audio capture
- H.264 video recording
- AAC audio at 48 kHz stereo
- Manual recording stop using ENTER
- Automatic audio extraction with FFmpeg
- Local Whisper transcription
- Configurable transcription language via `--language` (default: `es`)
- Automatic language detection with `--language auto`
- Apple Silicon optimized inference with MLX
- Automatic cleanup of the temporary WAV file after successful transcription
- Temporary WAV preservation for recovery or debugging if transcription fails
- Timestamped temporary WAV filenames so a preserved recovery file is never
  silently overwritten by a later run with the same `--name`
- User-friendly error messages for expected runtime failures
- Actionable errors when `ffmpeg`, `mlx_whisper`, or the native capture
  binary cannot be found, including how to fix it
- Non-zero exit status on failure
- Stage-by-stage progress output (`==> Recording`, `==> Extracting audio`,
  `==> Transcribing audio`, `==> Done`) with clear start/complete messages
- Suppressed FFmpeg banner/stats noise on successful runs; FFmpeg errors
  remain visible
- Clean Ctrl+C handling: no raw Python traceback, exits with status `130`,
  and preserves the recording and/or temporary audio whenever they exist
- Automated build script for the native macOS capture helper
  (`scripts/build_capture.sh`)
- Platform selector architecture for the capture backend
- Timestamped recording and transcript filenames
- No external API required for recording or transcription
- No cloud processing of recordings or transcripts
- Terminal-first workflow
- Pytest coverage for the core Python pipeline

## Architecture

The project separates platform-specific capture logic from shared processing and transcription logic.

```text
lecture-transcriber/
│
├── native/
│   └── macos/
│       └── capture.swift
│
├── src/
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── macos.py
│   │   └── selector.py
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── audio_extractor.py
│   │   └── file_manager.py
│   │
│   ├── transcription/
│   │   ├── __init__.py
│   │   └── whisper_transcriber.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── recordings/
├── transcripts/
├── temp/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

### Capture Layer

Screen recording is implemented in Swift using Apple's ScreenCaptureKit.

A small platform selector (`src/capture/selector.py`) chooses the capture backend at runtime based on the operating system.

Only the macOS backend is currently implemented. Running on an unsupported platform raises a clear `NotImplementedError` instead of attempting to record.

The native macOS capture helper produces a `.mov` file containing:

- H.264 video
- AAC system audio
- 48 kHz stereo audio

Python resolves the backend through the selector and launches the native capture binary with the output path and requested display index.

The `--display` argument defaults to `0`. The native helper validates the requested index against the available displays and exits with an error if the index is invalid.

This platform-specific layer is intentionally separated from the rest of the application so additional capture backends can be added later without replacing the shared processing and transcription pipeline.

### Audio Processing

FFmpeg extracts the audio track from the recording and converts it to:

```text
WAV
16 kHz
Mono
PCM 16-bit
```

This produces a speech-oriented intermediate audio file for transcription.

The temporary WAV is automatically deleted after successful transcription.

If transcription fails, the WAV is preserved so it can be reused for debugging or manual recovery.

### Transcription

Transcription runs locally using:

```text
mlx-community/whisper-large-v3-turbo
```

MLX is used to take advantage of Apple Silicon hardware acceleration.

The resulting transcript is saved as a plain `.txt` file.

The Whisper model may need to be downloaded the first time it is used. After the model is available locally, transcription runs on-device.

Lecture recordings, extracted audio, and transcripts are not uploaded for transcription.

## Requirements

### macOS

The current implementation supports macOS only.

An Apple Silicon Mac is currently required for the MLX transcription backend.

Intel Macs are not currently supported or tested.

Tested configuration:

```text
macOS Sequoia 15.3
Apple M4
Xcode 16.4
```

### Python

Python 3.9 or newer.

Check your version:

```bash
python3 --version
```

### Homebrew

Homebrew is recommended for installing FFmpeg.

Check whether it is installed:

```bash
brew --version
```

### FFmpeg

Install FFmpeg with Homebrew:

```bash
brew install ffmpeg
```

Verify the installation:

```bash
ffmpeg -version
```

### Xcode

A full Xcode installation is currently required to compile the native ScreenCaptureKit helper.

The tested version is:

```text
Xcode 16.4
```

Verify the active developer directory:

```bash
xcode-select -p
```

Example:

```text
/Applications/Xcode-16.4.0.app/Contents/Developer
```

If necessary, select Xcode manually:

```bash
sudo xcode-select --switch /Applications/Xcode-16.4.0.app/Contents/Developer
```

## macOS Permissions

The terminal application used to run Lecture Transcriber needs permission to capture screen and system audio.

Go to:

```text
System Settings
→ Privacy & Security
→ Screen & System Audio Recording
```

Enable permission for your terminal application.

The current implementation captures system audio but does not capture microphone input.

## Setup

Clone the repository:

```bash
git clone https://github.com/manach-101/lecture-transcriber.git
```

Enter the project directory:

```bash
cd lecture-transcriber
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Compile the macOS capture helper:

```bash
scripts/build_capture.sh
```

This checks that `swiftc` is available and compiles
`native/macos/capture.swift` to `native/macos/capture`. You can still run
the underlying command directly if you prefer:

```bash
swiftc -parse-as-library native/macos/capture.swift -o native/macos/capture
```

The compiled binary is intentionally excluded from Git and should currently be built locally.

## Testing

The core Python pipeline is covered by automated tests written with `pytest`.

Coverage includes:

- audio extraction command generation
- transcription command generation
- configurable transcription languages
- automatic language detection
- file naming and output paths
- capture backend selection
- macOS display argument forwarding
- temporary audio cleanup
- runtime error handling

Run the full test suite with:

```bash
python3 -m pytest -v
```

The native Swift capture helper is not currently covered by automated tests.

Capture behavior and display selection have been manually validated on the tested macOS configuration.

## Usage

Start a recording with:

```bash
python3 -m src.main --name discrete_math
```

The `--name` argument is required and is used to generate the output filenames.

For example:

```bash
python3 -m src.main --name systems_engineering
```

### Language Selection

The `--language` argument is optional and controls the transcription language passed to Whisper.

Spanish (`es`) is used by default.

Example using English:

```bash
python3 -m src.main --name systems_engineering --language en
```

Example using automatic language detection:

```bash
python3 -m src.main --name systems_engineering --language auto
```

When `--language auto` is used, no explicit language is passed to Whisper and the model detects the spoken language automatically.

### Display Selection

The `--display` argument is optional and selects which display to record by index.

Display `0` is used by default.

Example selecting the second detected display:

```bash
python3 -m src.main --name systems_engineering --display 1
```

Language and display options can be combined:

```bash
python3 -m src.main --name systems_engineering --language auto --display 1
```

If the requested display index does not exist, the application reports an error and exits with a non-zero status.

### Recording

After starting the application, the native capture helper displays:

```text
Recording started...
Press ENTER to stop.
```

Press ENTER when the lecture is finished.

The application will then automatically:

1. stop the recording
2. save the video
3. extract the audio with FFmpeg
4. convert the audio to a Whisper-friendly format
5. run Whisper locally
6. generate the transcript
7. remove the temporary WAV after successful transcription
8. display the final output paths

Each stage prints a short header so the pipeline is easy to follow. Example:

```text
==> Recording
Output: /path/to/lecture-transcriber/recordings/discrete_math_2026-09-07_21-22-28.mov

Recording started...
Press ENTER to stop.
Recording finished.

==> Extracting audio
Audio extraction complete.

==> Transcribing audio
Transcription complete.

==> Done
Recording saved:
/path/to/lecture-transcriber/recordings/discrete_math_2026-09-07_21-22-28.mov
Transcript saved:
/path/to/lecture-transcriber/transcripts/discrete_math_2026-09-07_21-22-28.txt
```

### Cancelling with Ctrl+C

Pressing Ctrl+C during audio extraction or transcription is handled cleanly:
the application prints `<stage> cancelled.`, lists whichever output files
still exist on disk (the recording and/or the temporary WAV) so you know
what to retry from, and exits with status `130` instead of printing a raw
Python traceback.

Ctrl+C during the recording stage itself is a known limitation: SIGINT goes
directly to the native Swift capture helper, which does not currently trap
it, so the `.mov` file may not finish writing correctly if interrupted mid
recording. Prefer pressing ENTER to stop the recording normally.

## Error Handling

Lecture Transcriber replaces raw Python tracebacks with concise user-facing messages for expected runtime failures.

Handled cases include:

- missing or uncompiled macOS capture binary (message points to
  `scripts/build_capture.sh`)
- missing FFmpeg executable (message points to `brew install ffmpeg`)
- missing MLX Whisper executable (message points to
  `pip install -r requirements.txt`)
- unsupported capture platform
- capture subprocess failure
- FFmpeg subprocess failure
- transcription subprocess failure
- invalid display index
- user cancellation via Ctrl+C (see [Cancelling with Ctrl+C](#cancelling-with-ctrlc))

Expected runtime failures return a non-zero exit status.

If transcription fails after the WAV has already been extracted, the WAV is preserved in `temp/` so the transcription can be retried without repeating the recording. The temporary WAV filename includes the same timestamp as the recording and transcript, so a preserved file from a failed run is never overwritten by a later run using the same `--name`.

## Output Files

Recordings are stored in:

```text
recordings/
```

Example:

```text
recordings/discrete_math_2026-09-07_21-22-28.mov
```

Transcripts are stored in:

```text
transcripts/
```

Example:

```text
transcripts/discrete_math_2026-09-07_21-22-28.txt
```

Temporary audio is stored in:

```text
temp/
```

The temporary WAV file is deleted automatically after successful transcription.

If transcription fails, the WAV file is preserved for debugging or manual retry.

The following generated directories are excluded from Git:

```text
recordings/
transcripts/
temp/
```

## Privacy

Lecture Transcriber is designed as a local-first application.

The current implementation does not upload:

- recordings
- extracted audio
- transcripts

to external transcription services.

Whisper inference runs locally on the machine.

No API key is required for the recording or transcription pipeline.

The Whisper model may require a one-time download before first use.

Users are responsible for ensuring they have permission to record lectures, meetings, calls, or other content.

## Current Limitations

The current implementation:

- supports macOS only
- currently requires an Apple Silicon Mac for MLX transcription
- supports selecting a display by index but not selecting an individual window
- captures system audio but not microphone input
- defaults to Spanish for transcription, although the language can be configured or automatically detected
- requires the native Swift helper to be compiled locally, though
  `scripts/build_capture.sh` automates the compile step
- requires FFmpeg to be installed separately
- requires Python and a virtual environment
- has no graphical interface
- does not include speaker diarization
- does not generate summaries or explanations
- does not currently provide structured logging (plain `print`-based stage
  output is used instead)
- if Ctrl+C is pressed while the native capture helper is actively
  recording, the `.mov` file may not finish writing correctly; pressing
  ENTER to stop is the reliable way to end a recording
- does not currently ship as a standalone macOS application
- does not currently support Windows
- does not currently include automated tests for the native Swift capture helper

## Roadmap

### V1

- selectable window in addition to display selection
- structured logging
- optional microphone capture
- graceful Ctrl+C handling in the native capture helper itself, so a
  recording interrupted mid-capture finalizes cleanly

### V1.5

Optional LLM processing layer:

```text
Transcript
    ↓
Optional LLM API
    ├── summary.md
    ├── explanation.md
    └── questions.md
```

The local recording and transcription pipeline should continue working without an API key.

### V2

- standalone macOS application
- graphical interface
- Windows capture backend
- Windows transcription backend
- standalone Windows application
- packaging without requiring users to manually install Python or FFmpeg
- simplified installation and first-run setup

### V3

- macOS code signing
- macOS notarization
- Windows code signing if appropriate
- versioned GitHub Releases
- downloadable binaries
- checksums
- release notes

## Design Principles

The project follows a few simple principles:

- local-first processing
- minimal external dependencies
- platform-specific capture separated from shared logic
- reliability over unnecessary complexity
- explicit error handling
- testable orchestration
- no database for the initial versions
- no external LLM dependency for basic functionality
- no unnecessary abstraction before the core workflow is stable

## License

License to be defined.