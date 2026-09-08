# Lecture Transcriber

A local-first lecture recording and transcription tool for macOS.

Lecture Transcriber records the screen and system audio using Apple's native ScreenCaptureKit framework, saves the recording locally, extracts speech-optimized audio with FFmpeg, and generates a raw transcript using Whisper optimized for Apple Silicon.

No recordings, audio files, or transcripts are uploaded to external services.

## Current Status

V0 is functional on macOS.

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
- System audio capture
- H.264 video recording
- AAC audio at 48 kHz stereo
- Manual recording stop using ENTER
- Automatic audio extraction with FFmpeg
- Local Whisper transcription
- Apple Silicon optimized inference with MLX
- Timestamped recording and transcript filenames
- No external API required
- No cloud processing
- Terminal-first workflow

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
│   │   └── macos.py
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

The native macOS capture helper produces a `.mov` file containing:

- H.264 video
- AAC system audio
- 48 kHz stereo audio

Python launches the native capture binary and provides the output path.

This platform-specific layer is intentionally separated from the rest of the application so that other capture backends, such as Windows, can be added later without replacing the shared processing and transcription pipeline.

### Audio Processing

FFmpeg extracts the audio track from the recording and converts it to:

```text
WAV
16 kHz
Mono
PCM 16-bit
```

This produces a lightweight speech-oriented audio file for transcription.

### Transcription

Transcription runs locally using:

```text
mlx-community/whisper-large-v3-turbo
```

MLX is used to take advantage of Apple Silicon hardware.

The resulting transcript is saved as a plain `.txt` file.

## Requirements

### macOS

The current V0 supports macOS only.

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

The current V0 captures system audio but does not capture microphone input.

## Setup

Clone the repository:

```bash
git clone <repository-url>
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
swiftc -parse-as-library native/macos/capture.swift -o native/macos/capture
```

The compiled binary is intentionally excluded from Git and should be built locally.

## Usage

Start a recording with:

```bash
python3 -m src.main --name discrete_math
```

The `--name` argument is used to generate the output filenames.

For example:

```bash
python3 -m src.main --name systems_engineering
```

The application will start recording and display:

```text
Recording started...
Press ENTER to stop.
```

Press ENTER when the lecture is finished.

The application will then automatically:

1. stop the recording;
2. save the video;
3. extract the audio with FFmpeg;
4. convert the audio to a Whisper-friendly format;
5. run Whisper locally;
6. generate the transcript;
7. display the final output paths.

Example:

```text
Done.

Recording saved:
/path/to/lecture-transcriber/recordings/discrete_math_2026-09-07_21-22-28.mov

Transcript saved:
/path/to/lecture-transcriber/transcripts/discrete_math_2026-09-07_21-22-28.txt
```

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

Temporary audio files are stored in:

```text
temp/
```

These directories are excluded from Git.

## Privacy

Lecture Transcriber is designed as a local-first application.

The current V0 does not upload:

- recordings
- extracted audio
- transcripts

to external services.

Whisper inference runs locally on the machine.

No API key is required.

Users are responsible for ensuring they have permission to record lectures, meetings, calls, or other content.

## Current Limitations

V0 currently:

- supports macOS only
- captures the first detected display
- captures system audio but not microphone input
- uses Spanish as the default transcription language
- requires the native Swift helper to be compiled manually
- requires FFmpeg to be installed
- requires Python and a virtual environment
- has no graphical interface
- does not include speaker diarization
- does not generate summaries or explanations

## Roadmap

### V1

- selectable display or window
- configurable transcription language
- improved CLI
- structured logging
- improved error handling
- progress information
- optional microphone capture
- automated native helper compilation
- pytest coverage

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

The local recording and transcription pipeline should continue working without any API key.

### V2

- Windows capture backend
- standalone macOS application
- standalone Windows application
- packaging without requiring Python or FFmpeg installation
- possible PyInstaller or equivalent distribution workflow

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
- no database for the initial versions
- no frontend or GUI until the core pipeline is stable
- no external LLM dependency for basic functionality

## License

License to be defined.