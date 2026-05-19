from dataclasses import dataclass
from pathlib import Path
import re


DEFAULT_AUDIO_DIR = Path("generated/audio")
SUPPORTED_FORMAT = "mp3"
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
    audio_path.write_bytes(_build_mock_audio_bytes(script=script, voice=voice))

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


def _build_mock_audio_bytes(script: str, voice: str) -> bytes:
    payload = (
        "PodCraft AI mock audio\n"
        f"Voice: {voice.strip()}\n"
        f"Script: {' '.join(script.split())}\n"
    )
    return b"ID3\x04\x00\x00\x00\x00\x00\x21" + payload.encode("utf-8")
