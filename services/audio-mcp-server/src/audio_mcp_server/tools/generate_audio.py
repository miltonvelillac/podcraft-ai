from dataclasses import dataclass
import math
from pathlib import Path
import re
import wave


DEFAULT_AUDIO_DIR = Path("generated/audio")
SUPPORTED_FORMAT = "wav"
SAMPLE_RATE = 8_000
_SAFE_PODCAST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class AudioGenerationResult:
    audio_url: str
    format: str
    duration_seconds: int


def generate_audio_from_text(
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
    output_dir: Path = DEFAULT_AUDIO_DIR,
) -> AudioGenerationResult:
    _validate_audio_request(
        podcast_id=podcast_id,
        script=script,
        voice=voice,
        duration_seconds=duration_seconds,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{podcast_id}.{SUPPORTED_FORMAT}"
    _write_mock_audio_file(
        audio_path=audio_path,
        script=script,
        voice=voice,
        duration_seconds=duration_seconds,
    )

    return AudioGenerationResult(
        audio_url=f"/generated/audio/{audio_path.name}",
        format=SUPPORTED_FORMAT,
        duration_seconds=duration_seconds,
    )


def _validate_audio_request(
    podcast_id: str,
    script: str,
    voice: str,
    duration_seconds: int,
) -> None:
    if not _SAFE_PODCAST_ID.fullmatch(podcast_id):
        raise ValueError("Podcast ID must be a safe filename.")
    if not script.strip():
        raise ValueError("Script cannot be empty.")
    if not voice.strip():
        raise ValueError("Voice cannot be empty.")
    if duration_seconds <= 0:
        raise ValueError("Duration must be greater than zero.")


def _write_mock_audio_file(
    audio_path: Path,
    script: str,
    voice: str,
    duration_seconds: int,
) -> None:
    voice_offset = sum(ord(character) for character in voice.strip()) % 80
    script_words = max(1, len(script.split()))
    base_frequency = 260 + voice_offset
    beat_frequency = 360 + (script_words % 120)

    with wave.open(str(audio_path), "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(SAMPLE_RATE)

        total_frames = duration_seconds * SAMPLE_RATE
        chunk_size = SAMPLE_RATE
        frames_written = 0

        while frames_written < total_frames:
            frames_in_chunk = min(chunk_size, total_frames - frames_written)
            audio_file.writeframesraw(
                _build_tone_chunk(
                    start_frame=frames_written,
                    frames=frames_in_chunk,
                    base_frequency=base_frequency,
                    beat_frequency=beat_frequency,
                )
            )
            frames_written += frames_in_chunk


def _build_tone_chunk(
    start_frame: int,
    frames: int,
    base_frequency: int,
    beat_frequency: int,
) -> bytes:
    chunk = bytearray()

    for offset in range(frames):
        frame = start_frame + offset
        second = frame // SAMPLE_RATE
        frequency = beat_frequency if second % 4 == 0 else base_frequency
        envelope = 0.35 if second % 2 == 0 else 0.22
        sample = int(8_000 * envelope * math.sin(2 * math.pi * frequency * frame / SAMPLE_RATE))
        chunk.extend(sample.to_bytes(2, byteorder="little", signed=True))

    return bytes(chunk)
