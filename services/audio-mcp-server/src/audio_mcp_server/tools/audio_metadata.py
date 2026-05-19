from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioMetadata:
    filename: str
    format: str
    size_bytes: int


def get_audio_metadata(audio_path: str) -> AudioMetadata:
    path = Path(audio_path)
    if not path.exists() or not path.is_file():
        raise ValueError("Audio file does not exist.")
    if not path.suffix:
        raise ValueError("Audio file must have an extension.")

    return AudioMetadata(
        filename=path.name,
        format=path.suffix.removeprefix(".").lower(),
        size_bytes=path.stat().st_size,
    )
